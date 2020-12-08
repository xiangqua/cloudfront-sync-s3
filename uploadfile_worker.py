import json

import time
import urllib
import hashlib
import base64
import boto3
from boto3.session import Session
from botocore.client import Config

global DesBucket
global MaxRetry

MaxRetry = 2
DesBucket = 'httpdnsnlbtest'


def download_upload_small_http(srcfileKey,url):
    for retryTime in range(MaxRetry + 1):
        try:
            pstart_time = time.time()
            # Get object
            Srcurl =  url + srcfileKey
            print("Srcurl is -------------")
            print(Srcurl)
            print(f"\033[0;33;1m--->Downloading\033[0m {srcfileKey} - small file - {retryTime} ")
            resp = urllib.request.urlopen(Srcurl)
            response_get_object = resp.read()
            chunkdata_md5 = hashlib.md5(response_get_object)
            ContentMD5 = base64.b64encode(chunkdata_md5.digest()).decode('utf-8')
            print(chunkdata_md5)
            # Put object
            print(f'\033[0;32;1m    --->Uploading\033[0m {srcfileKey} - small file')
            
            DesProfileName = "default"
            s3_config = Config(max_pool_connections=200)
            s3_dest_client = boto3.client('s3')
            
            print(DesBucket)
            print(srcfileKey)
            response= s3_dest_client.put_object(
                Body=response_get_object,
                Bucket=DesBucket,
                Key=srcfileKey,
                ContentMD5=ContentMD5,
            )
            print("upload response is-----------------")
            print(response)
            # 结束 Upload/download
            pload_time = time.time() - pstart_time
            pload_bytes = len(response_get_object)
            #pload_speed = size_to_str(int(pload_bytes / pload_time)) + "/s"
            #print(f'\033[0;34;1m        --->Complete\033[0m {srcfileKey}  - small file - {pload_speed}')
            break
        except Exception as e:
            #logger.warning(f'Download/Upload small file Fail: {srcfileKey}, '
                           #f'{str(e)}, Attempts: {retryTime}')
            print(str(e))
            if retryTime >= MaxRetry:
                #logger.error(f'Fail MaxRetry Download/Upload small file: {srcfileKey}')
                return "MaxRetry"
            else:
                time.sleep(5 * retryTime)
    return


def lambda_handler(event, context):
    srcurl = 'http://d1zi40b7x5dwgb.cloudfront.net/'
    # TODO implement
    print("-----------------event-------------------")
    print(event)
    job = json.dumps(event)
    print("-----------------srcfilekey-------------")
    print(job)
    srcfileKey = json.loads(job)['Key']
    download_upload_small_http(srcfileKey,srcurl)

