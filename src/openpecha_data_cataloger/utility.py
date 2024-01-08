from pathlib import Path

import requests
from github import Github

from openpecha_data_cataloger.github_token import GITHUB_TOKEN


def fetch_all_repos(token: str, org: str):
    g = Github(token)
    repos = g.get_organization(org).get_repos()
    return repos


def write_repos_to_file(token: str, org: str, file_name: str):
    repos = fetch_all_repos(token, org)
    with open(file_name, "w") as file:
        for repo in repos:
            file.write(repo.name + "\n")


def download_github_file(
    token, org: str, repo_name: str, file: str, destination_folder_path: Path
):
    if not destination_folder_path.exists():
        destination_folder_path.mkdir(parents=True)
    try:
        g = Github(token)
        repo = g.get_repo(f"{org}/{repo_name}")
        file_names = repo.get_contents("")
        for file_name in file_names:
            if file_name.name == file:
                download_file(
                    file_name.download_url, destination_folder_path / file_name.name
                )
    except Exception as e:
        print(e)


def download_file(url: str, destination_folder_path: Path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination_folder_path, "w", newline="", encoding="utf-8") as file:
            file.write(response.text)
        print(f"file downloaded: {destination_folder_path.name}")
    else:
        print(f"Failed to download: {response.status_code}")


if __name__ == "__main__":
    write_repos_to_file(GITHUB_TOKEN, "OpenPecha-Data", "repos.txt")
