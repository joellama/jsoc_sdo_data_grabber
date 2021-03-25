"""
Script to download data from JSOC
Written by Joe Llama (Lowell Observatory) 
v1.0 2021-03-25
"""
import requests as re
import time
from datetime import datetime
import pandas as pd
import os 
import wget

def print_message(msg):
    print(datetime.now().strftime(f"[%Y-%m-%d %H:%M:%S] {msg}"))


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser("Script to download data from JSOC")
    
    # Require config and or dates
    parser.add_argument('-s', '--series', type=str, default='hmi.ic_720s[$]',
                        help="The series query to retrieve")
    parser.add_argument('-e', '--email', type=str, 
                        help='Email address to be notified')
    parser.add_argument('-o', '--out-dir', type=str, default='./',
                        help='Directory to save the downloaded data')
    parser.add_argument('-v', '--verbose', help='Verbose output', action="store_true")
    parser.add_argument('-p', '--parallel', help='Downlaod files in parallel', action="store_true")

    # Arguments that can override the defaults
    parser.add_argument('--ndownloads', type=int, default=5,
                        help="Number of simultaneous downloads if using parallel")
    parser.add_argument('--jsoc-url', type=str, default="http://jsoc.stanford.edu",
                        help=f"URL for the JSOC website (Default: http://jsoc.stanford.edu).")
    parser.add_argument('--fetch-url', type=str, default="/cgi-bin/ajax/jsoc_fetch",
                        help=f"URL for the fetch ajax routine (Default: /cgi-bin/ajax/jsoc_fetch).")  
    parser.add_argument('--protocol', type=str, default="FITS",
                        help=f"Protocol for file acquisition (Default: FITS, options are: FITS, JPEG, MP4, MPEG).")                            
    parser.add_argument('--method', type=str, default="url",
                        help=f"Fetch method (Default: url, options are: url, ftp, url-tar, ftp-tar).") 
    parser.add_argument('--sleep-time', type=int, default=5,
                        help=f"Time in s to sleep between checks on export request") 
     
    args = parser.parse_args()

    if args.email is None:
        raise RuntimeError(f"A registered email address is required to submit the query")

    if args.protocol not in ['FITS', 'JPEG', 'MP4', 'MPEG']:
        raise RuntimeError(f"Protocol {args.protocol} not understood, must be one of FITS, JPEG, MP4, MPEG")

    if args.method not in ['url', 'ftp', 'url-tar', 'ftp-tar']:
        raise RuntimeError(f"Method {args.protocol} not understood, must be one of url, ftp, url-tar, ftp-tar")

    if not '[' in args.series:
        raise RuntimeError(f"Failed to parse series {args.series}")

    if args.verbose:
        print_message(f"Requesting {args.series} and will notify {args.email}")
    series_str = args.series.split('[')[0]    
    op_str = f"op=exp_request&ds={args.series}&sizeratio=1&process=n=0|no_op&requestor=&notify={args.email}&method={args.method}&filenamefmt={series_str}.{{T_REC:A}}.{{CAMERA}}.{{segment}}&format=json&protocol={args.protocol},compress Rice"
    qry_url = args.jsoc_url + args.fetch_url + '?' + op_str
    if args.verbose:
        print_message("Submitting request to JSOC")
    req = re.get(qry_url)
    if not req.status_code == 200:
        raise RuntimeError(f"Request failed with error code {req.status_code}. A 500 error could indicate you have a request pending.")
    req_status = req.json()['status']
    if req_status == 6:
        raise RuntimeError(f"Email address {args.email} is not registered with JSOC.")
    if req_status == 4:
        raise RuntimeError(f"Export request failed: {req.json()['error']}")    
    req_id = req.json()['requestid']      
    op_str = f"op=exp_status&requestid={req_id}&format=json"      
    qry_url =  args.jsoc_url + args.fetch_url + '?' + op_str
    req = re.get(qry_url)
    if not req.status_code == 200:
        raise RuntimeError(f"Request failed with error code {req.status_code}")
    status = int(req.json()['status'])
    while status != 0:
        if 'wait' in req.json().keys() and args.verbose:
            wait_time = abs(int(req.json()['wait']))
            print_message(f'Waiting for data to stage. Status = {status}, wait time = {wait_time}s')
        time.sleep(args.sleep_time)
        req = re.get(qry_url)
        status = int(req.json()['status'])    
    data_dict = req.json()
    remote_dir = data_dict['dir']
    files = [x['filename'] for x in data_dict['data']]
    infiles = [f"{args.jsoc_url}{remote_dir}/{file}" for file in files]
    outfiles = [f"{args.out_dir}{os.sep}{file}" for file in files]
    if args.verbose:
        print_message(f"Data finished staging. Now downloading {len(files)} files to destination: {args.out_dir}")
    if args.parallel:
        from pqdm.threads import pqdm
        if args.verbose:
            print_message(f"Downloading files in parallel: {args.ndownloads} simultaneously.")
        result = pqdm(list(zip(infiles, outfiles)), download_file, n_jobs=args.ndownloads)
    else:
        from tqdm import tqdm 
        if args.verbose:
            print_message(f"Downloading files")
        for file in tqdm(list(zip(infiles, outfiles))):
            download_file(file)
    
def download_file(file):
        infile = file[0]
        outfile = file[1]
        if not os.path.exists(outfile):
            if not os.path.exists(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))
            wget.download(infile, outfile, bar=None)
        return True
 

if __name__=='__main__':
    import sys
    sys.exit(main())