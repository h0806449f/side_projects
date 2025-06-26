import os
import json
import subprocess
from dotenv import load_dotenv


# load .env
load_dotenv()
ACCOUNT_ALIAS_LIST = json.loads(os.getenv("ACCOUNT_ALIAS_LIST"))
IMAGE_VERSION = os.getenv("IMAGE_VERSION")


# 正式執行 aws-nuke
def run_aws_nuke(account):
    # assume
    result = subprocess.run(
        f"aws-vault exec {account} -- env",
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True,
    )

    # get assume info
    env_vars = {}
    for line in result.stdout.splitlines():
        if line.startswith("AWS_"):
            key, value = line.split("=", 1)
            env_vars[key] = value

    base_dir = os.getcwd()
    config_path = os.path.join(base_dir, account, "config.yaml")

    # Docker 命令
    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",
        "-e",
        f"AWS_ACCESS_KEY_ID={env_vars.get('AWS_ACCESS_KEY_ID')}",
        "-e",
        f"AWS_SECRET_ACCESS_KEY={env_vars.get('AWS_SECRET_ACCESS_KEY')}",
        "-e",
        f"AWS_SESSION_TOKEN={env_vars.get('AWS_SESSION_TOKEN')}",
        "-v",
        f"{config_path}:/config.yaml",
        f"ghcr.io/ekristen/aws-nuke:{IMAGE_VERSION}",
        "run",
        "-c",
        "/config.yaml",
        "--no-dry-run",
    ]

    try:
        subprocess.run(cmd, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while processing account {account}: {e}")


# 清除 csv 檔案
def delete_csv_files():
    current_dir = os.getcwd()
    for file_name in os.listdir(current_dir):
        if file_name.endswith(".csv"):
            try:
                os.remove(os.path.join(current_dir, file_name))
            except OSError as e:
                print(f"csv 檔案刪除時產生錯誤,請檢查 {e}")


# 主邏輯
def main():
    for account in ACCOUNT_ALIAS_LIST:
        run_aws_nuke(account)


if __name__ == "__main__":
    main()
    delete_csv_files()
