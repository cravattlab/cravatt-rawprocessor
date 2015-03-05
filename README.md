This project provides an API for converting `.RAW` files into `.mxZML` via [`ReAdW 4.2.1`](http://sourceforge.net/projects/sashimi/files/ReAdW%20%28Xcalibur%20converter%29/ReAdW-4.2.1/) and `.ms2` via [`RawConverter`](http://fields.scripps.edu/rawconv/).

Tested on Windows Server 2012 R2.

The skinny:

1. Install MsFileReader from rawconv folder
2. Add readw and rawconv folders to path
3. Register XRawfile2.dll: `regsvr32 Xrawfile2.dll` 

Then, install python, install requirements `pip install -r requirements.txt` and `virtualenv env`. Activate environment and run app `python index.py`.

To run the application you must rename `config.sample.py` to `config.py` and provide a path to the network share you will be using. After uploading `.RAW` files to a folder within that network share, you can then have the files converted by sending a GET request as such: `127.0.0.1:5000/upload/FOLDER_CONTAINING_RAW_FILES`. This is assuming default setup on the same machine.