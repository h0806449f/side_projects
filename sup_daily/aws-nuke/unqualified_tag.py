import os
import sys
import json
import boto3
import urllib3
import datetime
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# load .env
load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def get_all_tagged_resources() -> list:
    client = boto3.client("resourcegroupstaggingapi")

    resources = []
    paginator = client.get_paginator("get_resources")

    for page in paginator.paginate():
        resources.extend(page["ResourceTagMappingList"])

    return resources


# retention 天數限制。調整為 100 天，避免大小月誤判
def filter_retention_resources() -> list:
    current_time = datetime.datetime.now(datetime.UTC)
    three_months_later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        days=100
    )

    retained_resources = []
    deleting_resources = []

    all_resources = get_all_tagged_resources()

    for resource in all_resources:
        resource_arn = resource["ResourceARN"]
        tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
        retention_date = (
            tags.get("retention") if tags.get("retention") else tags.get("Retention")
        )
        owner = tags.get("owner") if tags.get("owner") else tags.get("Owner")

        if retention_date:
            try:
                retention_dt = datetime.datetime.strptime(
                    retention_date, "%Y-%m-%d"
                ).replace(tzinfo=datetime.UTC)
                if retention_dt > three_months_later:
                    retained_resources.append(
                        {
                            "ResourceARN": resource_arn,
                            "RetentionDate": retention_date,
                            "Owner": owner,
                        }
                    )
                elif not owner and current_time < retention_dt < three_months_later:
                    deleting_resources.append(
                        {
                            "ResourceARN": resource_arn,
                            "RetentionDate": retention_date,
                        }
                    )
            except ValueError:
                continue  # 忽略無效格式的 retention 日期

    return retained_resources, deleting_resources


# slack_sdk's client
client = WebClient(token=SLACK_TOKEN)


def upload_file_to_slack(account, file_path, channel_id):
    try:
        response = client.files_upload(
            channels=channel_id,
            file=file_path,
            title=os.path.basename(file_path),
            initial_comment=f"{os.path.basename(account)} tag 不合標準的資源過多，請參考 CSV 檔案內容",
        )
        print(f"CSV 文件已成功上傳: {response['file']['name']}")
    except SlackApiError as e:
        print(f"CSV 上傳失敗: {e.response['error']}")


def resources_to_slack(account):
    SLACK_WEBHOOK_URL

    retained_resources, deleting_resources = filter_retention_resources()

    # 第一次檢查：aws resource tag。有資源不符合 tag 標準，進入第二次檢查；都符合 tag 標準，則提前 return
    if not retained_resources and not deleting_resources:
        empty_message = {
            "text": f"Hi teams,\n{account} 中所有 Tag 都符合標準，好棒棒!!"
        }
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            SLACK_WEBHOOK_URL,
            body=json.dumps(empty_message),
            headers={"Content-Type": "application/json"},
        )
        if response.status == 200:
            print("Empty list message sent to slack channel!")
        return

    # 第二次檢查前，先儲存 csv 檔與 message
    combined_resources = retained_resources + deleting_resources
    for resource in combined_resources:
        if "Owner" not in resource:
            resource["Owner"] = "N/A"

    df = pd.DataFrame(combined_resources)
    df = df.sort_values(by="ResourceARN")

    csv_filename = f"{account}_unqualified_tag.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

    output_string = tabulate(
        df, headers=["ARN", "Retention", "Owner"], tablefmt="orgtbl", showindex=False
    )

    message = {
        "text": f"Hi teams,\n{account} tag 不符合標準的 resource 如下:\n```"
        + output_string
        + "\n```"
    }

    # 第二次檢查，檢查 message 字數是否大於 4000。大於時傳送 csv 檔案；小於時傳送 message，避免 Slack message error
    max_length = 4000
    if len(json.dumps(message)) > max_length:
        upload_file_to_slack(account, csv_filename, SLACK_CHANNEL_ID)
    else:
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
    resources_to_slack(account)


if __name__ == "__main__":
    account = sys.argv[1]
    main(account)
