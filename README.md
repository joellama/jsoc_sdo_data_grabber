# jsoc_sdo_data_grabber
 Python script to grab data from JSOC. The code is written in `Python 3`. See `requirements.txt` for a list of required packages that should be installed. 
 
 ```
 usage: Script to download data from JSOC [-h] [-s SERIES] [-e EMAIL] [-o OUT_DIR] [-v] [-p] [-n NDOWNLOADS] [--jsoc-url JSOC_URL]
                                         [--fetch-url FETCH_URL] [--protocol PROTOCOL] [--method METHOD] [--sleep-time SLEEP_TIME]
 example query: python jsoc_sdo_data_grabber.py -s hmi.ic_720s[$] -e test@test.com
optional arguments:
  -h, --help            show this help message and exit
  -s SERIES, --series SERIES
                        The series query to retrieve
  -e EMAIL, --email EMAIL
                        Email address to be notified
  -o OUT_DIR, --out-dir OUT_DIR
                        Directory to save the downloaded data
  -v, --verbose         Verbose output
  -p, --parallel        Downlaod the files in parallel
  --ndownloads          Number of simultaneous downloads if using parallel
  --jsoc-url JSOC_URL   URL for the JSOC website (Default: http://jsoc.stanford.edu).
  --fetch-url FETCH_URL
                        URL for the fetch ajax routine (Default: /cgi-bin/ajax/jsoc_fetch).
  --protocol PROTOCOL   Protocol for file acquisition (Default: FITS, options are: FITS, JPEG, MP4, MPEG).
  --method METHOD       Fetch method (Default: url, options are: url, ftp, url-tar, ftp-tar).
  --sleep-time SLEEP_TIME
                        Time in s to sleep between checks on export request
```
