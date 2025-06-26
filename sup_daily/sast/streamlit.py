import json
import pandas as pd
import streamlit as st


# 路徑設定
CHECKOV_INDEX_PATH = "checkov_index.json"
SKIPPED_CHECKS_PATH = "skipped_checks.json"
OUTPUT_CSV_PATH = "scanned_result.csv"


# 讀取 JSON
def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# 輸出 csv
def save_to_csv(df, output_path):
    df.to_csv(output_path, index=False)


# 資料處理
def process_data():
    checkov_index = load_json(CHECKOV_INDEX_PATH)
    skipped_checks = load_json(SKIPPED_CHECKS_PATH)

    # JSON 檔案轉成 DataFrame
    df_checkov_index = pd.DataFrame(checkov_index).rename(columns={"Id": "check_id"})
    df_skipped_checks = pd.DataFrame(skipped_checks)

    # 合併 DataFrame
    merged_df = df_skipped_checks.merge(df_checkov_index, on="check_id", how="left")

    # 整理 DataFrame: 設定欄位 title, 排序, 移除資料重複項目
    final_df = merged_df[
        ["check_id", "Policy", "resource", "suppress_comment", "file_path"]
    ]
    final_df = final_df.sort_values(
        by=["check_id", "Policy", "resource", "suppress_comment", "file_path"]
    )
    final_df = final_df.drop_duplicates(
        subset=["check_id", "Policy", "resource", "suppress_comment", "file_path"]
    )

    save_to_csv(final_df, OUTPUT_CSV_PATH)

    return final_df


# 輸出到 streamlit 上
def main():
    st.set_page_config(layout="wide")

    final_df = process_data()

    st.title("以下為 ESB gitlab repo 所有 skipped 項目")
    st.dataframe(final_df, hide_index=True)


if __name__ == "__main__":
    main()
