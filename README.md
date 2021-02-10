# 利用CloudFront进行跨region的S3数据同步

## 背景介绍
AWS提供了多种实现S3跨region数据同步的方式，但不论采用哪种数据同步的技术，都会产生cross region的费用，当需要同步的数据量很大的时候会很可观，本方案旨在降低cross region的数据同步费用而设计。

## 使用说明

### 1、创建CloudFront分配，分配源指向源S3桶

### 2、创建lambda函数 uploadfile
部署脚本参考uploadfile.py ，修改配置文件中的SrcBucket(源S3桶) DesBucket（目标S3桶），S3_Prefix(同步文件在S3中的前缀)

SrcBucket = 'quandata1'

DesBucket = 'httpdnsnlbtest'

S3_Prefix = 'www'

### 3、部署lambda函数upload_worker
部署脚本参考 uploadfile_worker.py，修改脚本中的DesBucket（目标S3桶）和srcurl（使用CloudFront创建分配，CloudFront分配的域名例如： 'http://d1zi40b7x5dwgb.cloudfront.net/'）

### 4、配置cloudwatch event，定时触发lambda函数 uploadfile

### 5、可以通过单独部署compare_bucket.py来对比同步状态，上传同步状态文件
