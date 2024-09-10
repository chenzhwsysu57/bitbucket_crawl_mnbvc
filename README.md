# bitbucket_crawl_mnbvc
## Introduction


这份代码用来从bitbucket（一个代码托管平台）下载代码，提取文本到jsonl，并进行压缩。主要参考自： https://github.com/L1aoXingyu/bitbucket_download_mnbvc。



## 用法

### 下载函数的用法

1. [注册bitbucket账号](https://id.atlassian.com/login?continue=https%3A%2F%2Fwww.atlassian.com%2Ftry%2Fcloud%2Fsignup%3Fbundle%3Dbitbucket)，并且 [获取app password](https://support.atlassian.com/bitbucket-cloud/docs/create-an-app-password/)。然后写入 `.env` 文件内容如下
```
Atlassian_API_Token=你的bitbucket app password
username=你的butbucket用户名
```
2. 执行脚本
```bash
sh auto.sh
```
代码可重复运行，不会重复下载。网络中断、重启等原因直接重新执行即可。如果全部下载完了会有提示。
3. 监听写入json的状态：
```bash
watch -n 1 "du -h jsonl_output/bitbucketcode.* | sort -rV -k2.19"
```


输出形式如下：
```
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
...
```

等到没有新的内容输出，或者总任务数为0说明执行结束。

- 如果网络中断，重新执行：
`sh auto.sh` 
即可。


### 分析函数
statics.py文件：当出现太大的压缩包，希望检查jsonl的文件后缀名可以用：
`python statictics.py --filepath /home/zhiwei/Desktop/bitbucket_crawl_mnbvc/jsonl_output/bitbucketcode.3.jsonl --listhead 10`

输出为：
```
ext                 size
=========================
.js              1.06 MB
.map           853.52 KB
.js            726.75 KB
.js            605.88 KB
.js            531.08 KB
.js            526.94 KB
.js            507.31 KB
.html          503.56 KB
.json          321.81 KB
.js            271.13 KB
```
