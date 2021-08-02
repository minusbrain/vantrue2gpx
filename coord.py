#!/usr/bin/python

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def deg2dec (degr, min, sec):
    val = (degr + (min / 60) + (sec / 3600))
    val = truncate(val, 5)
    return val

def main ():
    lng_deg = 6
    lng_min = 4
    lng_sec = 5426
    lat_deg = 51
    lat_min = 51
    lat_sec = 750

    print ("{} {} {} = {}".format(lat_deg, lat_min, lat_sec/100, deg2dec(lat_deg, lat_min, lat_sec/100)))
    print ("{} {} {} = {}".format(lng_deg, lng_min, lng_sec/100, deg2dec(lng_deg, lng_min, lng_sec/100)))

if __name__ == "__main__":
    main()
