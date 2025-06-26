import json
import subprocess


def download_checkov():
    url = "https://raw.githubusercontent.com/bridgecrewio/checkov/main/docs/5.Policy%20Index/terraform.md"
    output_file = "terraform.md"
    try:
        subprocess.run(
            ["curl", "-o", output_file, url],
            check=True,
            text=True,
            capture_output=True,
        )
        print(f"Successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed: {e.stderr}")


# 從 .md  拿出 ID，Policy 並轉成 json 供後續使用
def sort_md_info():
    md_file_path = "./terraform.md"
    json_file_path = "checkov_index.json"

    content = []
    try:
        with open(md_file_path, "r") as file:
            in_table = False
            for line in file:
                if "|------" in line:
                    in_table = True
                    continue
                if in_table and line.strip():
                    content.append(line.strip())

        # 分割每行並提取所需欄位
        table_data = [row.split("|")[1:-1] for row in content if row.startswith("|")]
        result = [
            {"Id": row[1].strip(), "Policy": row[4].strip()} for row in table_data
        ]

        # 儲存為 JSON 檔案
        with open(json_file_path, "w") as json_file:
            json.dump(result, json_file, indent=4)

        print(f"done: {json_file_path}")

    except Exception as e:
        print(f"error: {e}")


def main():
    download_checkov()
    sort_md_info()


if __name__ == "__main__":
    main()
