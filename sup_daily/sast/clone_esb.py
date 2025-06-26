import os
import json
import click
import requests
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_API_URL = "https://gitlab.kkinternal.com/api/v4"
HEADERS = {"Private-Token": TOKEN}
GROUPS_AND_DIRS = json.loads(os.getenv("GROUPS_AND_DIRS"))


# 獲取 subgroup
def get_subgroups(group_id):
    url = f"{BASE_API_URL}/groups/{group_id}/subgroups"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


# 獲取 project
def get_projects(group_id):
    url = f"{BASE_API_URL}/groups/{group_id}/projects"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


# "git clone" 各個 repo
def clone_repo(repo_url, local_path, max_retries=2):
    retries = 0  # 初始化重試次數

    while retries < max_retries:
        try:
            if not os.path.exists(local_path):
                os.makedirs(local_path, exist_ok=True)

            # 跳過 LFS 檔案（內容非檢查對象，且檔案過大，會噴 error）
            env = os.environ.copy()
            env["GIT_LFS_SKIP_SMUDGE"] = "1"

            subprocess.run(["git", "clone", repo_url, local_path], check=True)
            click.secho(f"Successfully cloned {repo_url} to {local_path}", fg="green")

            # 成功後，等 1.5 秒，避免太頻繁 request 造成 error
            time.sleep(1.5)
            return

        except subprocess.CalledProcessError as e:
            retries += 1
            click.secho(
                f"Failed to clone {repo_url} (Attempt {retries}/{max_retries}): {e}",
                fg="blue",
            )

            # 失敗後，等待 3 秒重新嘗試
            if retries < max_retries:
                click.secho("Retrying after 3 seconds...", fg="yellow")
                time.sleep(3)
            else:
                click.secho(
                    f"Failed to clone {repo_url} after {max_retries} attempts.",
                    fg="red",
                )
                return


# 處理 group 和其子 group
def process_group(group_id, base_dir, parent_path=""):
    # 拿到 subgroup 的 ssh_url (只能用 ssh 不確定是不是因為 ESB 自己跑 gitlab server)
    projects = get_projects(group_id)
    for project in projects:
        repo_url = project.get("ssh_url_to_repo")
        if repo_url:
            project_name = project["name"]
            local_path = os.path.join(base_dir, parent_path, project_name)
            clone_repo(repo_url, local_path)

    # 處理當前 group 的 subgroups
    subgroups = get_subgroups(group_id)
    for subgroup in subgroups:
        subgroup_name = subgroup["name"]
        subgroup_id = subgroup["id"]
        print(f"Processing subgroup: {subgroup_name} (ID: {subgroup_id})")
        process_group(subgroup_id, base_dir, os.path.join(parent_path, subgroup_name))


# 主函數
def main():
    for group_config in GROUPS_AND_DIRS:
        group_id = group_config["group_id"]
        base_dir = group_config["base_dir"]
        print(f"Processing main group (ID: {group_id}, Base Dir: {base_dir})...")
        process_group(group_id, base_dir)


# 執行程式
if __name__ == "__main__":
    main()
