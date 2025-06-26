import os
import json
import shutil
from dotenv import load_dotenv


# 刪除 folder 內容
def delete_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error deleting folder {folder_path}: {e}")
    return


# 獲取 .env 中的 base_dir 並刪除
def delete_folders_in_env():
    load_dotenv()
    base_dir = os.getenv("GROUPS_AND_DIRS", "[]")

    try:
        base_dir = json.loads(base_dir)
        all_base_dir = [entry["base_dir"] for entry in base_dir]
    except json.JSONDecodeError as e:
        print(f"Failed to parse GROUPS_AND_DIRS: {e}")
        return

    base_path = os.getcwd()
    for dir in all_base_dir:
        dir_path = os.path.join(base_path, dir)
        delete_folder(dir_path)


if __name__ == "__main__":
    delete_folders_in_env()
