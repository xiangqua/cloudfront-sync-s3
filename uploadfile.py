import json
import sys
import boto3
from boto3.session import Session
from botocore.client import Config

def get_s3_file_list(*, s3_client, bucket, S3Prefix, no_prefix=False):
#    logger.info('Get s3 file list ' + bucket)

    # For delete prefix in des_prefix
    if S3Prefix == '':
        # 目的bucket没有设置 Prefix
        dp_len = 0
    else:
        # 目的bucket的 "prefix/"长度
        dp_len = len(S3Prefix) + 1

    paginator = s3_client.get_paginator('list_objects_v2')
    __des_file_list = []
    try:
        response_iterator = paginator.paginate(
            Bucket=bucket,
            Prefix=S3Prefix
        )
        for page in response_iterator:
            if "Contents" in page:
                for n in page["Contents"]:
                    key = n["Key"]
                    if no_prefix:
                        key = key[dp_len:]
                    __des_file_list.append({
                        "Key": key,
                        "Size": n["Size"]
                    })
        #logger.info(f'Bucket list length：{str(len(__des_file_list))}')
    except Exception as err:
        #logger.error(str(err))
        #input('PRESS ENTER TO QUIT')
        print(str(err))
        sys.exit(0)
    return __des_file_list
    
    
def upload_file(*, srcfile, desFilelist, ChunkSize_default):  
    #logger.info(f'Start file: {srcfile["Key"]}')
    client = boto3.client('lambda')
    prefix_and_key = srcfile["Key"]
    if srcfile['Size'] <= ChunkSize_default:
        # Check file exist
        for f in desFilelist:
            if f["Key"] == prefix_and_key and \
                    (srcfile["Size"] == f["Size"]):
                #logger.info(f'Duplicated. {prefix_and_key} same size, goto next file.')
                return
        #找不到文件，或文件Size不一致 Submit upload
        print("invoke lambda to download file %s" %srcfile)
        #payload='{"Key": "www/day=1/powered-by-aws-white.png"}'
        payload=srcfile
        #根据需要上传的文件，异步触发invoke lambda，通过第二个lambda函数根据key进行上传
        response = client.invoke(
                                FunctionName='upload_worker',
                                InvocationType='Event',
                                LogType='None',
                                Payload=json.dumps(payload),
                                #Qualifier='1',
                                )
        #print(response)
    return

def lambda_handler(event, context):
    SrcBucket = 'quandata1'
    DesBucket = 'httpdnsnlbtest'
    S3_Prefix = 'www'
    #定义chunksize，以便后面可以优化成multi upload
    ChunkSize_default = 5000000000
    
    #获取源S3 bucket的文件列表，以S3Prefix为前缀，遍历下面所有文件
    #print("-------------src file list-------------------------")
    s3_Src_client = boto3.client('s3')
    src_file_list = get_s3_file_list(s3_client=s3_Src_client, bucket=SrcBucket, S3Prefix=S3_Prefix)    
    #print(src_file_list)
    
    #获取目标S3 bucket的文件列表，以S3Prefix为前缀，遍历下面所有文件
    #print("-------------des file list-------------------------")
    s3_dest_client = boto3.client('s3')
    des_file_list = get_s3_file_list(s3_client=s3_dest_client, bucket=DesBucket, S3Prefix=S3_Prefix)
    #print(des_file_list)
    
    #遍历所有源bucket的文件，对比是否在目标桶存在，不存在则上传，判断逻辑在upload_file中
    for src_file in src_file_list:
        prefix_and_key = src_file["Key"]
        if prefix_and_key[-8:] != '_SUCCESS':
            upload_file(srcfile=src_file,desFilelist=des_file_list,ChunkSize_default=ChunkSize_default)
