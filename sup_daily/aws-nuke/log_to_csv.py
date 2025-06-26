import os
import sys
import csv
import json
import urllib3
import subprocess
import pandas as pd
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from tabulate import tabulate


# load .env
load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
IMAGE_VERSION = os.getenv("IMAGE_VERSION")


# dry run aws-nuke, output rawdata.csv
def dry_run_aws_nuke(account):
    base_dir = os.getcwd()
    config_path = os.path.join(base_dir, account, "config.yaml")

    # docker command
    cmd = f"""
    docker run --rm -i \
      -e AWS_ACCESS_KEY_ID="${{AWS_ACCESS_KEY_ID}}" \
      -e AWS_SECRET_ACCESS_KEY="${{AWS_SECRET_ACCESS_KEY}}" \
      -e AWS_SESSION_TOKEN="${{AWS_SESSION_TOKEN}}" \
      -v "{config_path}:/config.yaml" \
      ghcr.io/ekristen/aws-nuke:{IMAGE_VERSION} \
      run -c /config.yaml  | tee raw_data.csv
    """

    try:
        subprocess.run(cmd, shell=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error , {e.returncode}")


# 將 raw_data.csv 整理成 clean_data.csv
def filter_raw_data():
    raw_data_file = "raw_data.csv"
    clean_data_file = "clean_data.csv"

    # AWS region list
    aws_region_list = [
        "global",
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "ap-south-1",
        "ap-northeast-3",
        "ap-northeast-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ca-central-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-north-1",
        "af-south-1",
        "ap-east-1",
        "ap-south-2",
        "ap-southeast-3",
        "ap-southeast-4",
        "ca-west-1",
        "eu-south-1",
        "eu-south-2",
        "eu-central-2",
        "me-south-1",
        "me-central-1",
        "il-central-1",
    ]

    # 打開輸出 CSV 檔案，並設置 CSV 寫入器
    with open(clean_data_file, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # csv title, pandas title
        csv_writer.writerow(
            ["Region", "Resource Type", "Identifier", "Attributes", "Filter/Action"]
        )

        # 讀取 raw_data.csv
        with open(raw_data_file, mode="r", encoding="utf-8") as log:
            for line in log:
                region = line.split(" - ")[0]
                # 整理
                if region in aws_region_list:
                    parts = line.split(" - ")
                    if len(parts) >= 5:
                        resource_type = parts[1]
                        identifier = parts[2]
                        attributes = parts[3].strip()
                        action = parts[4].strip()

                        # 寫入 clean_data.csv
                        csv_writer.writerow(
                            [region, resource_type, identifier, attributes, action]
                        )


# 將 clean_data.csv 整理成 deleting_data.csv
def filter_clean_data(account):
    clean_data_path = "./clean_data.csv"
    df = pd.read_csv(clean_data_path)

    # filter pandas
    # 條件一: 篩選 Filter/Action 欄位，等於 "would remove"
    condition_1 = df["Filter/Action"] == "would remove"

    # 條件二: 篩選 Attributes欄位，不包含特定值
    condition_2 = df["Attributes"] != "[]"
    exclude_patterns = [
        r'\bDefaultVPC:\s*"true"',
        r'\bIsDefault:\s*"true"',
        r"\bdo-not-delete\b",
        r'\bBusName:\s*"default"',
        r'\bEventBusName:\s*"default"',
    ]
    combined_pattern = "|".join(exclude_patterns)
    condition_2_regex = ~df["Attributes"].str.contains(
        combined_pattern, case=True, na=False, regex=True
    )

    # 條件三: 篩選 Identifier 欄位，不包含 do-not-delete
    condition_3 = ~df["Identifier"].str.contains(r"do-not-delete", case=False, na=False)

    # 輸出成 csv
    df = df[condition_1 & condition_2 & condition_2_regex & condition_3]
    df = df.drop(columns=["Filter/Action"])

    # 輸出 csv
    output_file_name = f"{account}_deleting_data.csv"
    df.to_csv(output_file_name, index=False)


# create Slack SDK client
client = WebClient(token=SLACK_TOKEN)


# 使用 Slack SDK 上傳檔案
def upload_file_to_slack(account, file_path, channel_id):
    try:
        response = client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            title=os.path.basename(file_path),
            initial_comment=f"Hi teams,\n{account} 將刪除的資源過多，請參考 CSV 檔案內容",
        )
        print(
            f"{account} 資源過多, Slack 無法顯示，但 CSV 檔案已上傳成功",
            response["file"]["name"],
        )
    except SlackApiError as e:
        print(f"CSV 上傳失敗: {e.response['error']}")


# 將 csv 內容整理後，檢查字數，決定需要傳送到 slack 的內容
def df_to_slack(account):
    SLACK_WEBHOOK_URL

    df = pd.read_csv(f"{account}_deleting_data.csv")

    output_string = tabulate(
        df,
        headers=["Region", "Resource Type", "Identifier", "Attributes"],
        tablefmt="orgtbl",
        showindex=False,
    )

    message = {
        "text": f"Hi teams,\n{account} 將刪除的 AWS resources 如下:\n```"
        + output_string
        + "\n```"
    }

    # 檢查字數限制
    max_length = 4000
    if len(json.dumps(message)) > max_length:
        csv_file = f"{account}_deleting_data.csv"
        upload_file_to_slack(account, csv_file, SLACK_CHANNEL_ID)
    else:
        # 字數限制通過檢查
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            SLACK_WEBHOOK_URL,
            body=json.dumps(message),
            headers={"Content-Type": "application/json"},
        )
        if response.status == 200:
            print("Message sent to Slack channel!")


def main(account):
    dry_run_aws_nuke(account)
    filter_raw_data()
    filter_clean_data(account)
    df_to_slack(account)


if __name__ == "__main__":
    account = sys.argv[1]
    main(account)
