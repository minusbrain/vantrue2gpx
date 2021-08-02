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
import sqlite3

from datetime import datetime

def db_ensure_gps_table_exists(sqlcon):
    cur = sqlcon.cursor()

    #get the count of tables with the name
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='location_data' ''')

    #if the count is 1, then table exists
    if cur.fetchone()[0] != 1 :
        cur.execute('''CREATE TABLE location_data (datetime int PRIMARY KEY, filename text, lng_deg int, lng_min int, lng_sec int, lat_deg int, lat_min int, lat_sec int, speed int, elevation int)''')

    # Save (commit) the changes
    sqlcon.commit()

def connect_and_init_db(dbfile):
    sqlcon = None
    try:
        sqlcon = sqlite3.connect(dbfile)
        db_ensure_gps_table_exists(sqlcon)
    except Exception as ex:
        print("Error while opening DB: {0}".format(ex))
        return None
    return sqlcon

def add_datapoint_to_sql(data, sqlcur, filename):
    sqlcur.execute(
        ''' INSERT OR REPLACE INTO location_data VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
        (
            datetime.timestamp(data["timestamp"]),
            filename,
            data["lng_deg"], data["lng_min"], data["lng_sec"],
            data["lat_deg"], data["lat_min"], data["lat_sec"],
            data["speed"], data["elevation"]
        )
    )

def getSortedListOfAllTimestamps(sqlcon):
    cur = sqlcon.cursor()
    cur.row_factory = lambda cursor, row: row[0]

    #get the count of tables with the name
    cur.execute(''' SELECT datetime FROM location_data ORDER BY datetime ASC ''')

    data = cur.fetchall()

    sqlcon.commit()

    return data

def get_trip_data(sqlcon, start_timestamp, end_timestamp):
    cur = sqlcon.cursor()
    cur.row_factory = None

    #get the count of tables with the name
    cur.execute(''' SELECT * FROM location_data WHERE datetime >= ? AND datetime <= ? ORDER BY datetime ASC ''', (start_timestamp, end_timestamp))

    data = cur.fetchall()

    sqlcon.commit()
    return data