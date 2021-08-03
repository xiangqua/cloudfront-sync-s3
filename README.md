# 利用CloudFront进行跨region的S3数据同步

## 背景介绍
AWS提供了多种实现S3跨region数据同步的方式，但不论采用哪种数据同步的技术，都会产生cross region的费用，当需要同步的数据量很大的时候会很可观，本方案旨在降低cross region的数据同步费用而设计。

## CloudFront介绍
Amazon CloudFront 是一项快速内容分发网络 (CDN) 服务，可以安全地以低延迟和高传输速度向全球客户分发数据、视频、应用程序和 API，全部都在开发人员友好的环境中完成。Amazon CloudFront 可以大幅扩容，并在全球范围内分布。CloudFront 网络拥有 225 个以上的存在点 (PoP)，这些存在点通过 AWS 主干网相互连接，为最终用户提供超低延迟性能和高可用性。

## 架构说明
<img src="https://user-images.githubusercontent.com/75667661/128048056-824ffd31-e223-4c96-9930-79cb7c5a1c22.png" width="500" height="300"/><br/>

## 功能说明

-具备文件同步功能

-可改造多线程并发下载和上传

-具备文件同步状态对比功能

-具备遗漏文件重新同步功能


## 部署说明
compare_bucket.py    ：用于对比两边存储桶的差异，定时调度

uploadfile.py        ：调度lambda，用于判断同步文件，触发其他lambda下载文件

uploadfile_worker.py ：下载文件执行程序


## 使用说明

### 1、创建CloudFront分配，分配源指向源S3桶

### 2、创建lambda函数 uploadfile
部署脚本参考uploadfile.py 

修改配置文件中的SrcBucket(源S3桶) 

DesBucket（目标S3桶）

S3_Prefix(同步文件在S3中的前缀)

SrcBucket = 'quandata1'

DesBucket = 'httpdnsnlbtest'

S3_Prefix = 'www'

### 3、部署lambda函数upload_worker
部署脚本参考 uploadfile_worker.py，修改脚本中的DesBucket（目标S3桶）和srcurl（使用CloudFront创建分配，CloudFront分配的域名例如： 'http://d1zi40b7x5dwgb.cloudfront.net/'）

### 4、配置cloudwatch event，定时触发lambda函数 uploadfile

按实际需要定期进行文件同步，周期通过cloudwatch event控制

### 5、同步状态对比和监控

可以通过单独部署compare_bucket.py来对比同步状态，上传同步状态文件
脚本通过cloudwatch event来调度，定时进行对比
