#!/usr/bin/python
import math

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def deg2dec (degr, min, sec):
    val = (abs(degr) + (min / 60) + (sec / 3600)) * math.copysign(1, degr)
    val = truncate(val, 5)
    return float(val)

def main ():
    testcases = [
        ((52, 51, 7.50), 52.85208, (6, 4, 54.26), 6.08174),
        ((-52, 51, 7.50), -52.85208, (-6, 4, 54.26), -6.08174),
        ((0, 0, 0), 0, (0, 0, 0), 0),
        ((-75, 15, 40.55), -75.26126, (156, 58, 28.26), 156.97451),
        ((-75, 15, 40.55), -75.26126, (-156, 58, 28.26), -156.97451),
        ((90, 0, 0), 90, (180, 0, 0), 180),
        ((-90, 0, 0), -90, (-180, 0, 0), -180)
    ]

    for testcase in testcases:
        print ("Test case: " + str(testcase))
        latitude = deg2dec(testcase[0][0], testcase[0][1], testcase[0][2])
        print("Expected latitude {} calculated latitude {}".format(testcase[1], latitude))
        assert(abs(latitude - testcase[1]) <= 0.00001)
        longitude = deg2dec(testcase[2][0], testcase[2][1], testcase[2][2])
        print("Expected latitude {} calculated latitude {}".format(testcase[3], longitude))
        assert(abs(longitude - testcase[3]) <= 0.00001)

if __name__ == "__main__":
    main()
