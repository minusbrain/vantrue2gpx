#!/usr/bin/python
import sys
import argparse
import os
import tempfile
import businesslogic as bl
from sqldb import connect_and_init_db

class Vantrue2GpxArgparse:
    def __init__(self):
        self.parser=argparse.ArgumentParser(prog="vantrue2gpx", description="Parses Vantrue mp4 files into GPX tracks")
        self.parser.add_argument("--verbose", default=False, action='store_true', help="Activate verbose output")
        self.parser.add_argument("--ignore_errors", "-i", default=False, action='store_true', help="Ignore errors as long as possible")

        requiredNamed = self.parser.add_argument_group('required named arguments')
        requiredNamed.add_argument("--videoin", "-v", default=None, type=str, help="Input folder containing all vantrue MP4 videos to parse", required=True)
        requiredNamed.add_argument("--gpxout", "-g", default=None, type=str, help="Output folder to write resulting GPX files to", required=True)

    def parse(self, argv):
        args = vars(self.parser.parse_args(argv))

        return args

def main():
    parser = Vantrue2GpxArgparse()
    args = parser.parse(sys.argv[1:])

    #tempdb = os.path.join(tempfile.gettempdir(), 'vantrue2gpx_data.db')
    tempdb = ":memory:"
    sqlcon = connect_and_init_db(tempdb)
    if sqlcon == None:
        print ("ERROR: Could not open temp databasefile: " + tempdb)
        sys.exit(1)

    print ("== STEP 1/4  -  Identifying relevant input files")
    relevantfiles = [ x for x in os.listdir(args["videoin"]) if x.lower().endswith("_a.mp4") ]
    print ("                Found {} relevant files to process".format(len(relevantfiles)))

    print ("== STEP 2/4  -  Extracting GPS Metadata and storing it in Database")
    bl.vantruevid_2_db(args, relevantfiles, sqlcon)

    print ("== STEP 3/4  -  Identify distinct trips in data")
    trips = bl.find_distinct_trips_in_db(sqlcon)
    print ("                Found {} distinct trips".format(len(trips)))

    print ("== STEP 4/4  -  Generate GPX files for each trip")
    bl.generate_gpx_for_all_trips(args["gpxout"], trips, sqlcon)
    print ("Done")

    sqlcon.close()


if __name__ == "__main__":
    main()
