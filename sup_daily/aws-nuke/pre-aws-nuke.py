import os
import json
import subprocess
from dotenv import load_dotenv


# load .env
load_dotenv()
ACCOUNT_ALIAS_LIST = json.loads(os.getenv("ACCOUNT_ALIAS_LIST"))
IMAGE_VERSION = os.getenv("IMAGE_VERSION")


# 更新以下資源: docker image version, poetry 套件
def update_image_package():
    update_command = f"""
    docker pull ghcr.io/ekristen/aws-nuke:{IMAGE_VERSION} &&
    poetry install --no-root
    """
    subprocess.run(update_command, shell=True)


def assume_role_and_call_function(account):
    # command
    command_log_to_csv = f"""
    aws-vault exec {account} -- poetry run python log_to_csv.py {account}
    """
    command_unqualified_tag = f"""
    aws-vault exec {account} -- poetry run python unqualified_tag.py {account}
    """

    # 執行 log_to_csv.py
    subprocess.run(command_log_to_csv, shell=True, executable="/bin/bash", check=True)

    # 執行 unqualified_tag.py
    subprocess.run(
        command_unqualified_tag, shell=True, executable="/bin/bash", check=True
    )


# 主邏輯 - 20250619 交接
def main():
    update_image_package()

    # loop through account list
    for account in ACCOUNT_ALIAS_LIST:
        assume_role_and_call_function(account)


if __name__ == "__main__":
    main()
