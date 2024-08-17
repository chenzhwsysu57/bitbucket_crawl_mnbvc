# bitbucket_crawl_mnbvc
## Introduction


这份代码用来从bitbucket（一个代码托管平台）下载代码，提取文本到jsonl，并进行压缩。主要参考自： https://github.com/L1aoXingyu/bitbucket_download_mnbvc。



## 用法
```
python3 bitbucket_with_check_progress_with_zip2jsonl_with_nontext_check.py 
-u USERNAME
-p BITbucket_APP_TOKEN
-o OUTPUT_DIR
-i INPUT_FILE
--debug False # 默认是True，只下载前1000个链接的仓库。
```


* USERNAME: 你的bitbucket用户名。
* BITbucket_APP_TOKEN: 在 [app-password](https://bitbucket.org/account/settings/app-passwords/) 进行设置。[tutorial](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/). 这是bitbucket的token。
* OUTPUT_DIR: 临时下载的仓库存放到 `./bitbucket`, 处理成jsonl之后会被删除。
* 除此之外，zip 文件会写入到 `jsonl_output` 下。




