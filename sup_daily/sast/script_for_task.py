import subprocess


def run_task():
    # update checkov's readme file
    print("updating checkov's index")
    command_update_checkov_doc = "poetry run python get_checkov_index.py"
    subprocess.run(
        command_update_checkov_doc, shell=True, executable="/bin/bash", check=True
    )

    # clone Going Cloud repo
    command_clone_repo = "poetry run python clone_esb.py"
    subprocess.run(command_clone_repo, shell=True, executable="/bin/bash", check=True)

    # checkov's command and query
    print("scanning each repo")
    command_checkov_scan = (
        "GIT_TERMINAL_PROMPT=0 checkov -d . --framework terraform "
        "--download-external-modules true --output json | "
        "jq '[.results.skipped_checks[] | {check_id, resource, suppress_comment, file_path}]' > skipped_checks.json"
    )
    subprocess.run(command_checkov_scan, shell=True, executable="/bin/bash", check=True)

    # streamlit
    print("exporting to streamlit")
    command_streamlit = "nohup streamlit run  streamlit.py &"
    subprocess.Popen(command_streamlit, shell=True, executable="/bin/bash")

    # 清除 clone 的檔案
    print("deleting git clone repo")
    command_clean = "poetry run python clean_sast.py"
    subprocess.run(command_clean, shell=True, executable="/bin/bash", check=True)


if __name__ == "__main__":
    run_task()
