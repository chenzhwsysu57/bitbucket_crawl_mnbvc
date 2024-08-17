from requests.auth import HTTPBasicAuth
import os
import requests
import csv
import argparse
import urllib3
import time
from pathlib import Path
from converter import Zipfile2JsonL  # 假设你的Zipfile2JsonL类代码在这个模块中

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
    
    remaining_jobs = 999
    while remaining_jobs > 0:
        remaining_jobs = sum(1 for row in data[1:] if row) - sum(1 for row in data[1:] if row[1] == 'success' or row[1] == '404')

        if remaining_jobs <= 0:
            print("process done.")
            break

        max_url_len = max(len(row[0]) for row in data[1:])

        # 遍历CSV中的每个URL
        for row in data[1:]:  # 跳过header
            url, status, jsonl = row
            if status != 'success' and status != '404':

                # 格式化URL为ZIP文件的下载链接
                zip_url = url.replace('.git', '/get/master.zip')
                filename = url.split('/')[-1].replace('.git', '.zip')
                file_path = os.path.join(output, filename)

                try:
                    # 发出请求下载ZIP文件
                    print(f"request {zip_url:<{max_url_len}}", end=' ')
                    r = requests.get(zip_url, allow_redirects=True, verify=False, timeout=60)
                    r.raise_for_status()

                    # 将下载的内容保存为ZIP文件
                    with open(file_path, 'wb') as f:
                        f.write(r.content)

                    # 调用Zipfile2JsonL实例进行JSONL转换
                    # 任务重启后防止jsonl重复写入。
                    if row[2] != 'exists':
                        converter(file_path)
                        row[2] = 'exists'
                        os.remove(file_path)
                    # 更新CSV中的状态为'success'
                    row[1] = 'success'
                    
                    update_csv_row(csv_path, row)
                    remaining_jobs -= 1
                    print(f"\033[1;32msuccess\033[0m [{remaining_jobs}/{total_jobs}]")
                    if remaining_jobs <= 0:
                        print("process done.")
                        break

                except Exception as e:
                    
                    print(f"\033[1;31mfailed\033[0m [{remaining_jobs}/{total_jobs}], \033[0;33m{e}\033[0m")
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--user", help="Bitbucket username", type=str, required=True)
    ap.add_argument("-p", "--password", help="Bitbucket app password", type=str, required=True)
    ap.add_argument("-i", "--input", help="Bitbucket URLs file path", type=str, default='./clone_urls_1000')
    ap.add_argument("-o", "--output", help="Output directory", type=str, default='./bitbucket')
    ap.add_argument("-c", "--csv", help="CSV file to track download status", type=str, default='./download_status.csv')
    ap.add_argument("-j", "--jsonl_output", help="Output directory for JSONL files", type=str, default='./jsonl_output')
    args = vars(ap.parse_args())

    user = args['user']
    pwd = args['password']
    input = args['input']
    output = args['output']
    csv_path = args['csv']
    jsonl_output = args['jsonl_output']

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    login_flag = False
    while not login_flag:
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
