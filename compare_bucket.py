import json
import boto3
import sys

DesBucket = 'httpdnsnlbtest'
SrcBucket = 'quandata1'
s3_dest_client = boto3.client('s3')
s3_src_client = boto3.client('s3')
S3Prefix = 'www'


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
#        logger.info(f'Bucket list length：{str(len(__des_file_list))}')
    except Exception as err:
#        logger.error(str(err))
        input('PRESS ENTER TO QUIT')
        sys.exit(0)
    return __des_file_list
    

def compare_buckets():
    print('Comparing destination and source ...')
    deltaList = []
    
    desFilelist = get_s3_file_list(s3_client=s3_dest_client,
                                   bucket=DesBucket,
                                   S3Prefix=S3Prefix)

    srcfileList = get_s3_file_list(s3_client=s3_src_client,
                                bucket=SrcBucket,
                                S3Prefix=S3Prefix)

    for source_file in srcfileList:
        if source_file not in desFilelist:
            deltaList.append(source_file)
    print(deltaList)
    #如果两边差异列表为空，证明源bucket桶还没有上传_SUCCESS文件，源桶文件还没正式完成上传
    if not deltaList:
        print('source bucket not include _SUCCESS file')
    else:
        print(f'There are {len(deltaList)} files not in destination or not the same size. List:')
        if len(deltaList) == 1:
            if deltaList[0]["Key"][-8:] == '_SUCCESS':
                print(deltaList[0]["Key"][-8:])
                print("All source files are in destination Bucket,job done")
                return "1"
        else:
            for delta_file in deltaList:
                print(json.dumps(delta_file))
                return "0"

    return "0"

if __name__ == '__main__':
    status = compare_buckets()
    if status == "1":
        print("ok")
        #上传_SUCCESS标志文件到目标S3桶，其中Key的前缀需要根据当前比对的小时目录前缀来修改
        response = s3_dest_client.put_object(
                                    Bucket=DesBucket,
                                    Key='www/_SUCCESS',
                                    )

        print(response)
    if status == "0":
        print("not ok")