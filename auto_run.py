# automatically run untils it ends normally.

import subprocess
import random
import time 
import os 
from dotenv import load_dotenv
load_dotenv()
commands = [
    # command1
    [
        "python", "bitbucket_with_check_progress_with_zip2jsonl_with_nontext_check.py",
        "-u", "ziweicen",
        "-p", os.getenv('Atlassian_API_Token'),
        "-i", "clone_urls_1000_5000"
    ]
]

for command in commands:
    while True:
        result = subprocess.run(command)
        if result.returncode == 0:
            print(f"\033[1;32mcommand {command} excuted successfully\033[0m", flush=True)
            break
        else:
            print(f"\033[1;33mfailed {command}, retrying...\033[0m", flush=True)
            time.sleep(random.randint(1,10))