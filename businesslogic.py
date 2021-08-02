#!/usr/bin/python
# Copyright (c) 2021 Andreas Evers

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
from datetime import datetime
import signal
import sqlite3
import os
import array
import sqldb
import ffmpeg
import tempfile
import gpxpy
import xml.etree.ElementTree as ET
from coord import deg2dec
from progress_bar import progressBar

signal.signal(signal.SIGPIPE, signal.SIG_DFL) # To avoid broken pipes

def get_datapoint_from_raw(rawin, data):
    # data[12] always 1?
    # data[13-24] always 0?
    # data[31] always 0?
    # data[32] always 2?
    # data[33-35] always 0?
    # data[36-47] ?
    # data[48-50] always AEN?
    # data[64-80] always 0?
    # data[81] ? J/K
    # data[82-100] always 0?
    #print (data[36:48])
    year = int.from_bytes(rawin[24:26], byteorder=sys.byteorder)
    month = int(rawin[26])
    day = int(rawin[27])
    hour = int(rawin[28])
    minute = int(rawin[29])
    second = int(rawin[30])
    data["timestamp"] = datetime(year, month, day, hour, minute, second)

    data["lng_deg"] = int(rawin[51])
    data["lng_min"] = int(rawin[52])
    data["lng_sec"] = int.from_bytes(rawin[54:56], byteorder=sys.byteorder) # in 0.01 Seconds
    data["lat_deg"] = int(rawin[56])
    data["lat_min"] = int(rawin[57])
    data["lat_sec"] = int.from_bytes(rawin[58:60], byteorder=sys.byteorder) # in 0.01 Seconds
    data["speed"] = int.from_bytes(rawin[60:62], byteorder=sys.byteorder) # in km/h
    data["elevation"] = int.from_bytes(rawin[62:64], byteorder=sys.byteorder) # in 0.1 m

def gpmd_2_sqlite(rawinput_path, sqlcon, source_filename):
    input_filename = os.path.basename(rawinput_path)

    rawdata = None
    try:
        f = open(rawinput_path, "rb")
        rawdata = f.read()
    except Exception as ex:
        print("Error while opening file: {0}".format(ex))
        return False

    sqlcur = sqlcon.cursor()
    x = 0
    lastindex = 0
    while True:
        x = rawdata.find(b'OFNIMMASSAMM', x+1)
        if x < 0:
            break
        data = {}
        get_datapoint_from_raw(rawdata[x:x+100], data)
        # Only one measurement point per second / AND valid GPS data
        if lastindex != data["timestamp"] and not(data["lat_deg"] == 0 and data["lat_deg"] == 0):
            sqldb.add_datapoint_to_sql(data, sqlcur, source_filename)
        lastindex = data["timestamp"]

        # print ( str(data["timestamp"] )
        #         + " - "
        #         + "N{:03}°".format(data["lat_deg"])
        #         + "{:02}'".format(data["lat_min"])
        #         + "{:05.2f}\"".format(data["lat_sec"]/100)
        #         + " - "
        #         + "E{:03}°".format(data["lng_deg"])
        #         + "{:02}'".format(data["lng_min"])
        #         + "{:05.2f}\"".format(data["lng_sec"]/100)
        #         + " - "
        #         + "{:3} km/h".format(data["speed"])
        #         + " - "
        #         + "{:3.1f} m".format(data["elevation"]/10)
        # )

        #print (','.join('{:02x}'.format(x) for x in data[36:48]))

    sqlcon.commit()
    return True

def vantruevid_2_db(args, relevantfiles, sqlcon):
    tempdatafile = os.path.join(tempfile.gettempdir(), 'vantrue_data.bin')

    for current_file_full in progressBar(relevantfiles, prefix = '                Progress:', suffix = 'Complete', length = 50):
        current_file = os.path.basename(current_file_full)
        try:
            os.remove(tempdatafile)
        except FileNotFoundError:
            pass

        try:
            infile = ffmpeg.input(current_file_full, f="mp4")
            outfile = ffmpeg.output(infile, tempdatafile, map="0:2", f="data")
            ffmpeg.run(outfile, quiet=True)
        except ffmpeg.Error as e:
            print("Error while trying to extract GPS Metadata from " + current_file + "\nFFMPEG output: " + e.stderr.decode(), file=sys.stderr)
            if args["ignore_errors"] == False:
                sys.exit(1)

        gpmd_2_sqlite(current_file_full, sqlcon, current_file)

def find_distinct_trips_in_db(args, sqlcon):
    all_timestamps = sqldb.getSortedListOfAllTimestamps(sqlcon)

    start_index = 0
    curr_index = 0
    trips = []
    last_timestamp = 0
    for timestamp in all_timestamps:
        if (timestamp - last_timestamp) > args["trip_timeout"]:
            if curr_index != 0:
                trips.append((all_timestamps[start_index], all_timestamps[curr_index-1]))
                start_index = curr_index
        last_timestamp = timestamp
        curr_index = curr_index + 1

    trips.append((all_timestamps[start_index], all_timestamps[curr_index-1]))

    return trips

def generate_gpx_for_trip(args, trip, sqlcon):
    trip_data = sqldb.get_trip_data(sqlcon, trip[0], trip[1])
    speedtag = (args["gpx_version"] == '1.0')
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    if len(trip_data) < 1 or len(trip_data[0]) < 1:
        print (trip_data)
        return

    gpx_filename = datetime.fromtimestamp(trip_data[0][0]).strftime("trip_%Y%m%d_%H%M.gpx")

    for trackpt in trip_data:
        if speedtag:
            gpx_point = gpxpy.gpx.GPXTrackPoint(time=datetime.fromtimestamp(trackpt[0]), longitude=deg2dec(trackpt[2], trackpt[3], trackpt[4]/100), latitude=deg2dec(trackpt[5], trackpt[6], trackpt[7]/100), elevation=trackpt[9], speed=trackpt[8])
        else:
            gpx_point = gpxpy.gpx.GPXTrackPoint(time=datetime.fromtimestamp(trackpt[0]), longitude=deg2dec(trackpt[2], trackpt[3], trackpt[4]/100), latitude=deg2dec(trackpt[5], trackpt[6], trackpt[7]/100), elevation=trackpt[9])
            gpx_extension_hr = ET.fromstring(f"""<speed>{trackpt[8]}</speed>""")
            gpx_point.extensions.append(gpx_extension_hr)

        gpx_segment.points.append(gpx_point)

    with open(os.path.join(args["gpxout"], gpx_filename), "w") as gpx_file:
        gpx_file.write(gpx.to_xml(version=args["gpx_version"]))

def generate_gpx_for_all_trips(args, trips, sqlcon):
    for trip in trips: #progressBar(trips, prefix = '                Progress:', suffix = 'Complete', length = 50):
        print ("                Processing trip from timestamp {} to {}".format(datetime.fromtimestamp(trip[0]), datetime.fromtimestamp(trip[1])))
        generate_gpx_for_trip(args, trip, sqlcon)
