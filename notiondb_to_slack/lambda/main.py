import json
import boto3
from datetime import datetime
from notion_client import Client
import urllib3


# 從 AWS Secrets Manager 獲取機密
def get_secret(secret_name):
    secret_name = "henry_testtf_lambda_secret_v240627"
    region_name = "ap-northeast-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


# 初始化 Notion client，使用從 Secrets Manager 中獲取的機密
def init_notion_client():
    secret = get_secret("henry_testtf_lambda_secret_lastversion")
    notion_token = secret.get("notion-token")
    notion = Client(auth=notion_token)
    return notion


# 設定 Notion Database ID（可選擇從 Secrets Manager 中讀取或硬編碼）
database_id = "14ee8e8ebd6e4dd1b2fdf374d5f8733e"


# 查詢資料庫所有頁面
def get_all_pages(notion, database_id):
    all_pages = []
    has_more = True
    next_cursor = None

    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=next_cursor,
            page_size=100,  # Notion API 一次最多返回 100 頁資料
        )

        all_pages.extend(response["results"])
        has_more = response["has_more"]
        next_cursor = response.get("next_cursor")

    return all_pages


def find_oldest_page(pages):
    oldest_page = None
    oldest_date = None

    for page in pages:
        date_property = page["last_edited_time"]

        if oldest_date is None or date_property < oldest_date:
            oldest_date = date_property
            oldest_page = page

    return oldest_page


def query_oldest_page(page):
    title_data = page.get("properties").get("Name").get("title")[0]
    title = title_data.get("text").get("content")
    url = page.get("url")

    message = f"""Hi teams
每日一篇知識庫 {datetime.today().strftime("%m/%d")}
標題 {title}
連結 {url}"""

    return message


# 發送消息到 Slack
def send_slack_message(message):
    secret = get_secret("henry_testtf_lambda_secret_lastversion")
    webhook_url = secret.get("slack-webhook")

    http = urllib3.PoolManager()

    payload = {"text": message}
    encoded_data = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    response = http.request("POST", webhook_url, body=encoded_data, headers=headers)

    return response.status


# Lambda 入口函數
def lambda_handler(event, context):
    notion = init_notion_client()
    pages = get_all_pages(notion, database_id)
    oldest_page = find_oldest_page(pages)
    message = query_oldest_page(oldest_page)
    send_slack_message(message)

    return {"statusCode": 200, "body": json.dumps("Message sent successfully")}
