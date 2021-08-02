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
import argparse
import os
import tempfile
import businesslogic as bl
from sqldb import connect_and_init_db

class Vantrue2GpxArgparse:
    def __init__(self):
        self.parser=argparse.ArgumentParser(prog="vantrue2gpx", description="Parses Vantrue mp4 files into GPX tracks", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        requiredNamed = self.parser.add_argument_group('required named arguments')
        requiredNamed.add_argument("--videoin", "-v", action='append', type=str, help="Input folder containing all vantrue MP4 videos to parse", required=True)
        requiredNamed.add_argument("--gpxout", "-g", type=str, help="Output folder to write resulting GPX files to", required=True)

        self.parser.add_argument("--verbose", default=False, action='store_true', help="Activate verbose output")
        self.parser.add_argument("--ignore_errors", "-i", default=False, action='store_true', help="Ignore errors as long as possible")
        self.parser.add_argument("--gpx_version", choices=['1.0', '1.1'], default='1.1', help="Version of GPX Format to output")
        self.parser.add_argument("--trip_timeout", type=int, default=600, help="Time in seconds that must be between two tracking points to consider them for two separate trips")
        self.parser.add_argument("--videofile_suffix", type=str, default='_a.mp4', help="Suffix to select video input files by. Case insensitve.")
    def parse(self, argv):
        args = vars(self.parser.parse_args(argv))

        return args

def main():
    parser = Vantrue2GpxArgparse()
    args = parser.parse(sys.argv[1:])
    relevantfiles = []

    #tempdb = os.path.join(tempfile.gettempdir(), 'vantrue2gpx_data.db')
    tempdb = ":memory:"
    sqlcon = connect_and_init_db(tempdb)
    if sqlcon == None:
        print ("ERROR: Could not open temp databasefile: " + tempdb)
        sys.exit(1)

    print ("== STEP 1/4  -  Identifying relevant input files")
    for videoindir in args["videoin"]:
        relevantfiles.extend([ videoindir + x for x in os.listdir(videoindir) if x.lower().endswith(args["videofile_suffix"]) ])
    print ("                Found {} relevant files to process".format(len(relevantfiles)))

    print ("== STEP 2/4  -  Extracting GPS Metadata and storing it in Database")
    bl.vantruevid_2_db(args, relevantfiles, sqlcon)

    print ("== STEP 3/4  -  Identify distinct trips in data")
    trips = bl.find_distinct_trips_in_db(args, sqlcon)
    print ("                Found {} distinct trips".format(len(trips)))

    print ("== STEP 4/4  -  Generate GPX files for each trip")
    bl.generate_gpx_for_all_trips(args, trips, sqlcon)
    print ("Done")

    sqlcon.close()


if __name__ == "__main__":
    main()
