import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# read .env 文件
load_dotenv()
URL = os.getenv("URL")
AI_FLOW_TOKEN = os.getenv("AI_FLOW_TOKEN")


def run_flow(message):
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {
        "Authorization": f"Bearer {AI_FLOW_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(URL, json=payload, headers=headers, timeout=300)

    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")

    return response


def main():
    st.title("在一片陰暗的迷霧中 ...")

    message = st.text_area("想從喉嚨裡擠出一點話 ...", placeholder="嘗試說點什麼")

    if st.button("說話"):
        if not message.strip():
            st.error("沒有傳達出去 ... 請再試一次 ...")
            return

        try:
            with st.spinner("說出的話，變成回音，不斷在空間中迴盪 ..."):
                response = run_flow(message)

            # 確保回應是列表
            if isinstance(response, list):
                for step in response:
                    st.markdown(f"- {step}")
            else:
                st.error("API 回應格式不符合預期，請檢查服務端邏輯。")
        except Exception as e:
            st.error(str(e))


if __name__ == "__main__":
    main()
