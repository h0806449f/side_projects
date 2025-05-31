from datetime import datetime
import asyncio
import aiohttp
import urllib3
import base64
import json
import os


# credentials
USERNAME = "henrylee@going.cloud"
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
DATABASE_PAGE_ID = "532742726"
SPACE_KEY = "esbrd"


# api token check
def get_auth_header(username, api_token):
    token = f"{username}:{api_token}"
    token_bytes = token.encode("utf-8")
    base64_token = base64.b64encode(token_bytes).decode("utf-8")
    return {"Authorization": f"Basic {base64_token}"}


AUTH_HEADER = get_auth_header(USERNAME, CONFLUENCE_API_TOKEN)
API_BASE = "https://kkcompany.atlassian.net/wiki/rest/api"


async def fetch(session, url, params=None):
    async with session.get(url, params=params) as response:
        response.raise_for_status()
        return await response.json()


# 只撈出 page 在 confluence database 中的資料
async def get_all_child_pages(session, parent_id):
    url = f"{API_BASE}/content/{parent_id}/child/page"
    params = {"limit": 50, "expand": "version"}
    all_pages = []
    start = 0
    while True:
        params["start"] = start
        data = await fetch(session, url, params)
        all_pages.extend(data.get("results", []))
        size = data.get("size", 0)
        total = data.get("totalSize", 0)
        if size + start >= total:
            break
        start += size
    return all_pages


# 進一步找 page 的 detail 資料
async def get_page_detail(session, page_id):
    url = f"{API_BASE}/content/{page_id}"
    params = {"expand": "version"}
    data = await fetch(session, url, params)
    return {
        "id": data["id"],
        "title": data["title"],
        "updated": datetime.fromisoformat(
            data["version"]["when"].replace("Z", "+00:00")
        ),
        "link": f"https://kkcompany.atlassian.net/wiki/spaces/{SPACE_KEY}/pages/{data['id']}",
    }


# 錯誤處理
async def safe_get_page_detail(session, page_id):
    try:
        return await get_page_detail(session, page_id)
    except Exception as e:
        print(f"Failed to fetch details for page {page_id}: {e}")
        return None


def send_slack_message(message):
    webhook_url = SLACK_WEBHOOK

    http = urllib3.PoolManager()
    payload = {"text": message}
    encoded_data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    response = http.request("POST", webhook_url, body=encoded_data, headers=headers)
    return response.status


# 主邏輯
async def main():
    async with aiohttp.ClientSession(headers=AUTH_HEADER) as session:
        pages = await get_all_child_pages(session, DATABASE_PAGE_ID)
        page_count = len(pages)

        tasks = [safe_get_page_detail(session, p["id"]) for p in pages]
        details = [d for d in await asyncio.gather(*tasks) if d is not None]

        oldest_detail = min(details, key=lambda p: p["updated"])

        page_title = oldest_detail["title"]
        page_link = oldest_detail["link"]

        message = f"""Hi teams
每週一篇 sup km {datetime.today().strftime("%m/%d")}
標題: {page_title}
連結: {page_link}"""

        return message


def lambda_handler(event, context):
    message = asyncio.run(main())
    send_slack_message(message)

    return {"statusCode": 200, "body": json.dumps("Message sent successfully")}
