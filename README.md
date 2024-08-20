# bitbucket_crawl_mnbvc
## Introduction


这份代码用来从bitbucket（一个代码托管平台）下载代码，提取文本到jsonl，并进行压缩。主要参考自： https://github.com/L1aoXingyu/bitbucket_download_mnbvc。



## 用法

### 下载函数
1. 检查 jsonl_output 文件夹，如果有内容重命名为其他文件名
2. 检查download_status.csv 文件，如果有内容重命名为其他文件夹
3. `sed -n '1000,5000p' clone_urls > clone_urls_1000_5000` ，用类似的命令，把文件第1000行到5000行之间的内容写入到文件，这是接下来希望下载的文件。（总共有 794057 行）
4.  [注册bitbucket账号](https://id.atlassian.com/login?continue=https%3A%2F%2Fwww.atlassian.com%2Ftry%2Fcloud%2Fsignup%3Fbundle%3Dbitbucket)，并且 [获取app password](https://support.atlassian.com/bitbucket-cloud/docs/create-an-app-password/)。然后写入 `.env` 文件内容如下
```
Atlassian_API_Token=你的bitbucket app password
username=你的butbucket用户名
```
5. `python bitbucket_with_check_progress_with_zip2jsonl_with_nontext_check.py --input 刚生成的新文件`



输出形式如下：
```
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
request https://bitbucket.org/username/repo/get/master.zip            仓库处理状态 [剩余任务数/总任务数]
...
```

等到没有新的内容输出，或者总任务数为0说明执行结束。

- 如果网络中断，重新执行：
`python bitbucket_with_check_progress_with_zip2jsonl_with_nontext_check.py  --input 刚生成的新文件` 
即可。
- 如果一个仓库等很久都没下载下来，可以手动去 download_status.csv把那个状态改成已执行完毕，跳过它。参考：bug汇总。

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
### 自动运行

`auto_run.py` 文件可以在你写好的命令里自动运行脚本，直到结束。例如，写好命令到 `auto run.py` 文件，
然后执行： `python auto_run.py` ，进程如果终止，会自动重新启动任务直到进程正常结束。 为了正常运行 `auto_run.py` 文件，需要写一个.env文件存放key。但是可能存在没处理好的错误，导致一直死循环处理一个仓库。目前需要手动跳过。参考《bug汇总》。

> 执行auto run之前，记得先修改input文件为你要处理的仓库列表。






#### bug汇总

由于 try except 块捕获太多，代码有些bug还没有来得及修改，但不是第一优先级。因此可以手动修改。
1. `https://bitbucket.org/hansthexon/141020161.git,init,none` 这条记录，仓库能成功下载下来，但解析的时候不报错为什么直接结束了代码进程。有待考察。
    目前解决方法；把这条记录手动改成 `https://bitbucket.org/hansthexon/141020161.git,success,exists`

