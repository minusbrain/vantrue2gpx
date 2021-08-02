# Vantrue Video to GPX File converter

This script can parse MP4 files taken by Vantrue cameras and extract the following information
from it:
* Timestamp
* Geo Coordinates (Latitude, Longitude, Elevation)
* Speed
This data is then exported into GPX files, where each GPX file is one trip.

# Usage

Make sure you checked the [Supprt](#Support) section and the [Dependencies](#Dependencies) section
before trying to run the script.

## Make all video files available

Copy or move all video files you want to evaluate from your camera to your PC. This includes
event videos and normal (ringbuffer) videos. Please be aware that videodata in the Event folder
is not available in the Normal folder, so in order to get a complete picture you might need both.

Only one perspective is required (e.g. front camera) but you can use the script internal filter
to filter one perspective by providing a videofile suffix to look put for.

## Call the script

```bash
./vantrue2gpx.py -v ~/Videos/NORMAL/ -v ~/Videos/EVENT -g ~/Documents/dashcam_trips --ignore_errors
```

* Using the option -v you can provide one or more folder the script will search for relevant input files
  by applying the videofile suffix (_a.mp4 by default).
* Using the option -g you can provide the output folder where the generated GPX files should be put to
* --ignore_errors will (if possible) continue script execution even if input data cannot be handled
  properly for whatever reason (e.g. corrupt videofile)

## View GPX files in your favorite viewer

* One option is [gpx-viewer for Linux](https://blog.sarine.nl/tag/gpxviewer/)
* There are many more options as GPX is a pretty standard format

## Test out the other command line options

You'll get an overview of the other options by invoking the help option.

```bash
./vantrue2gpx.py -h
```

The recommendation is to run the script first on a small subset of video files until you are satisfied
with the options before you run it on all the new videofiles you got.

# Support

If something is not listed here it does not automatically mean it will not work,
just that nobody has tested it before.

* OS: Only tested on Linux
* Camera: Only tested with Vantrue N4
* Known limitations
    * Currently this has only been tested in the N/E hemisphere. This is not a limitation per
      see and the code is expected to work with video files from anywhere on earth. But as the
      format used by Vantrue is not documented (at least I did not find any documentation) and
      I do not have a way to get videodata from somewhere else this is currently untested.

# Dependencies

* Python 3 (Python 2 is untested)
* 'ffmpeg' must be installed
* 'ffmpeg-python' package must be installed
* 'sqlite3' must be installed
* 'sqlite3' python package must be installed
* 'gpxpy' python package must be installed

One of the items on the todo list is to define a docker image to run the script in with all
dependencies installed.
