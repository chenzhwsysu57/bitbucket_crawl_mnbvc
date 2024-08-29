from requests.auth import HTTPBasicAuth
import os
import requests
import csv
import argparse
import urllib3
import time
from pathlib import Path
from converter import Zipfile2JsonL  # 假设你的Zipfile2JsonL类代码在这个模块中
from http import HTTPStatus 
from requests.exceptions import HTTPError

import requests
import os 
def get_url_size(url: str) -> str:
    try:
        # 发送HEAD请求以获取头信息
        response = requests.head(url, allow_redirects=True)
        # 获取Content-Length头信息
        # content_length = response.headers.get('Content-Length')
        
        cmd = """curl --head -s {{url}} | grep -i Content-Length | awk '{print $2}' | awk '{print $1}'"""
        content_length = os.system(cmd)
        if content_length is None:
            return "Content-Length not found."

        # 将Content-Length转换为字节数
        size_in_bytes = int(content_length)

        # 根据文件大小选择合适的单位
        if size_in_bytes >= 1024**3:  # 如果文件大小大于或等于1 GB
            size = size_in_bytes / (1024**3)
            return f"{size:.2f} GB"
        elif size_in_bytes >= 1024**2:  # 如果文件大小小于1 GB
            size = size_in_bytes / (1024**2)
            return f"{size:.2f} MB"
        else:
            size = size_in_bytes / (1024**1)
            return f"{size:.2f} KB"
    except requests.RequestException as e:
        return f"Error: {e}"

# 示例使用
# url = "https://example.com/file.zip"
# print(get_url_size(url))


retries = 3 
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]
def get_with_max_tries(zip_url, allow_redirects=True, verify=False, timeout=60):
    retries = 3
    retry_codes = [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]
    for n in range(retries):
        try:
            response = requests.get(zip_url, allow_redirects=True, verify=False, timeout=60)
        except HTTPError as exc:
            code = exc.response.status_code
            
            if code in retry_codes:
                # retry after n seconds
                time.sleep(3)
                continue
        return response

def load_repos(input):
    debug = os.environ.get('DEBUG', 'False')
    if debug.lower() in ('true', '1'):
        debug = True
    else:
        debug = False
    if debug:
        urls = [
            "https://bitbucket.org/michalbel/saxs-mlv.git",
            'https://bitbucket.org/kmccall_appacademy/3d8e2e08-william.lemus-data-structure-exercises.git',
            'https://bitbucket.org/ammppp/edb_examples.git',
            'https://bitbucket.org/lerzinski1969l9/albert1969besides.git',
            'https://bitbucket.org/isysd/dotfiles-lele85.git'
        ]
        return urls
    print(f"reading urls {input}")
    with open(input, 'r') as f:
        urls = f.readlines()
    return urls

def login(user, pwd):
    roles = 'owner member contributor admin'.split()
    for role in roles:
        print(f'Checking role {role}')
        url = f'https://api.bitbucket.org/2.0/repositories?pagelen=100&role={role}'
        rs = requests.get(url, auth=HTTPBasicAuth(user, pwd)).json()
        if 'values' not in rs:
            print(f'Role {role} is invalid')
            continue
        else:
            print(f'Role {role} is valid')
            return True
    return False

def initialize_csv(urls, csv_path):
    """初始化CSV文件，并为每个URL设置状态为'init'"""
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['url', 'status', 'jsonl'])
        for url in urls:
            writer.writerow([url.strip(), 'init', 'none'])

def load_csv(csv_path):
    """加载CSV文件并返回数据"""
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

def update_csv_row(csv_path, row):
    # print(f"writing back: {row}")
    """更新CSV文件中的单行数据"""
    data = load_csv(csv_path)
    for i, line in enumerate(data):
        if line[0] == row[0]:
            data[i] = row
            break
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def download_repo(csv_path, output, jsonl_output):
    if not os.path.exists(output):
        os.makedirs(output)

    # 创建Zipfile2JsonL实例
    chunk_counter = 0  # 可以从0开始计数
    converter = Zipfile2JsonL(jsonl_output, chunk_counter)

    # 加载CSV文件数据
    data = load_csv(csv_path)
    total_jobs = len(data) - 1  # 总任务数（跳过header）
    
    remaining_jobs = sum(1 for row in data[1:] if row) - sum(1 for row in data[1:] if row[1] in ['success', '404', '403', '410', '443'])
    while remaining_jobs > 0:
        remaining_jobs = sum(1 for row in data[1:] if row) - sum(1 for row in data[1:] if row[1] in ['success', '404', '403', '410', '443'])

        if remaining_jobs <= 0:
            print("process done.")
            break

        max_url_len = max(len(row[0]) for row in data[1:]) + 10

        # 遍历CSV中的每个URL
        for row in data[1:]:  # 跳过header
            url, status, jsonl = row
            if status not in ['success', '404', '403', '410', '443']:
            # if status != 'success' and status != '404' and status != '403' and status != '410': # 只下载不包括这些的

                # 格式化URL为ZIP文件的下载链接
                zip_url = url.replace('.git', '/get/master.zip')
                filename = url.split('/')[-1].replace('.git', '.zip')
                file_path = os.path.join(output, filename)

                try:
                    # 发出请求下载ZIP文件
                    msg = f"request {zip_url} of size {get_url_size(zip_url)}"
                    print(f"{msg:<{max_url_len}}", end=' ',flush=True)
                    # r = get_with_max_tries(zip_url, allow_redirects=True, verify=False, timeout=60)
                    r = requests.get(zip_url, allow_redirects=True, verify=False, timeout=60)
                    r.raise_for_status()
                    print(f"{r.status_code}", end=' ',flush=True)
                    # 将下载的内容保存为ZIP文件
                    with open(file_path, 'wb') as f:
                        f.write(r.content)

                    # 调用Zipfile2JsonL实例进行JSONL转换
                    # 任务重启后防止jsonl重复写入。
                    if row[2] != 'exists':
                        print(f"converting..", end=' ',flush=True)
                        try:
                            converter(file_path)
                        except Exception as e:
                            pass  # 解压错误直接全部跳过。
                        row[2] = 'exists'
                        os.remove(file_path)
                    # 更新CSV中的状态为'success'
                    row[1] = 'success'
                    
                    update_csv_row(csv_path, row)
                    remaining_jobs -= 1
                    print(f"\033[1;32msuccess\033[0m [{remaining_jobs}/{total_jobs}]",flush=True)
                    if remaining_jobs <= 0:
                        print("process done.")
                        break

                except Exception as e:
                    
                    print(f"\033[1;31mfailed\033[0m [{remaining_jobs}/{total_jobs}], \033[0;33m{e}\033[0m",flush=True)
                    try:
                        row[1] = f'{e.response.status_code}'
                    except Exception as e2: # AttributeError: 'NoneType' object has no attribute 'status_code'
                        print(e2)
                        row[1] = "443"
                    update_csv_row(csv_path, row)
                    

        # 重新加载数据以检查是否还有未处理的URL
        data = load_csv(csv_path)

        if not remaining_jobs <= 0:
            print("Retrying failed downloads...")
            time.sleep(1)  # 可以设置一定的等待时间以避免频繁请求

    print("All URLs processed.")

import os 
from dotenv import load_dotenv
load_dotenv()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--user", help="Bitbucket username", type=str, default=os.getenv('username'))
    ap.add_argument("-p", "--password", help="Bitbucket app password", type=str, default=os.getenv('Atlassian_API_Token'))

    ap.add_argument( "--start", help="start idx from a list of repos", type=int, default=0)
    ap.add_argument( "--end", help="end idx from a list of repos", type=int, default=1000)
    ap.add_argument("-o", "--output", help="Output directory", type=str, default='./bitbucket')

    args = vars(ap.parse_args())

    user = args['user']
    pwd = args['password']
    # input = args['input']
    
    # 增加input文件：
    
    output = args['output']
    start = args['start']
    end = args['end']

    csv_path = f"download_status_{start}_{end}.csv"
    jsonl_output = f"jsonl_output_{start}_{end}"
    input = f"clone_urls_{start}_{end}"
    if not os.path.exists(input):
        cmd = f"sed -n '{start},{end}p' clone_urls > clone_urls_{start}_{end}"
        os.system(cmd)
    # jsonl_output = args['jsonl_output']

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    login_flag = False
    while not login_flag:
        print(user, pwd)
        login_flag = login(user, pwd)

    urls = load_repos(input)
    print("urls file loaded.")
    # 如果CSV文件不存在，初始化它
    if not os.path.exists(csv_path):
        print("initialize status csv...")
        initialize_csv(urls, csv_path)

    # 开始下载和处理
    print("start processing urls")
    download_repo(csv_path, output, jsonl_output)

if __name__ == "__main__":
    main()
