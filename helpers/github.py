import requests
import json


def fetch_latest_commit_sha(url: str) -> str:
    commit_sha = None

    response = requests.get(url)
    if response and response.text:
        commit = json.loads(response.text)[0]
        if commit:
            commit_sha = commit["sha"]

    if commit_sha:
        return commit_sha
    else:
        raise Exception("Could not fetch latest commit sha")
