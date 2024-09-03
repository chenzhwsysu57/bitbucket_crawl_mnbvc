import time
import os
import subprocess
import random
from dotenv import load_dotenv

load_dotenv()

# Mock implementation of the repair function
def repair(start, end):
    print(f"Repairing... Position: {cur_pos}, Filename: {filename}")
    csv_path = f'download_status_{start}_{end}.csv'
    import pandas as pd 
    df = pd.read_csv(csv_path)
    # 找到第一个status为'init'的行的索引
    init_index = df[df['status'] == 'init'].index[0]

    # 更新该行的status和jsonl
    df.at[init_index, 'status'] = 'skip'
    df.at[init_index, 'jsonl'] = 'skip'

    # 写回CSV文件
    df.to_csv(csv_path, index=False)
    print(f"\033[1;36mchanging row {df[df['status'] == 'init'].iloc[0]['url']}.\033[0m")


# Prepare list of commands
commands = [
    # command1 with placeholders `??` for start and end
    [
        "python", "download_bitbucket_repos_from_urls.py",
        "--start", "10000",  # replace with actual start value
        "--end", "30000",      # replace with actual end value
    ]
]

for command in commands:
    while True:
        print(f'excuting {command}')
        result = subprocess.run(command)
        if result.returncode == 0:
            print(f"\033[1;32mcommand {command} executed successfully\033[0m", flush=True)
            break
        else:
            start_index = command.index("--start") + 1
            end_index = command.index("--end") + 1

            # 获取start和end的值
            start = int(command[start_index])
            end = int(command[end_index])
            print(f"\033[1;36mfailed {command}, retrying...\033[0m", flush=True)
            # Call the repair function before retrying
            repair(start, end)
            time.sleep(random.randint(1,10))
