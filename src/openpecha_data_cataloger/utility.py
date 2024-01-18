import json
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml
from github import Github


def load_yaml(fn: Path):
    # use yaml.CSafeLoader / if available but don't crash if it isn't
    try:
        yaml_loader = yaml.CSafeLoader
    except (ImportError, AttributeError):
        yaml_loader = yaml.SafeLoader  # type: ignore
    return yaml.load(fn.open(encoding="utf-8"), Loader=yaml_loader)


def merge_two_dictionary(dict1, dict2):
    for key, value in dict2.items():
        if key not in dict1:
            dict1[key] = value
    return dict1


def get_all_repos(org_name, token):
    repos = []
    page = 1
    per_page = 100  # Number of repositories to retrieve per page

    while True:
        # Make a request to the GitHub API to retrieve repositories for the organization
        url = f"https://api.github.com/orgs/{org_name}/repos?page={page}&per_page={per_page}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }
        response = requests.get(url, headers=headers)

        # Handle rate limit exceeded error
        if response.status_code == 403 and "rate limit exceeded" in response.text:
            reset_time = datetime.fromtimestamp(
                int(response.headers["X-RateLimit-Reset"])
            )
            sleep_seconds = (
                reset_time - datetime.now()
            ).total_seconds() + 10  # Add extra time buffer
            print(f"Rate limit exceeded. Sleeping for {sleep_seconds} seconds.")
            time.sleep(sleep_seconds)
            continue

        # Handle other errors
        if response.status_code != 200:
            print(f"Error occurred while fetching repositories: {response.status_code}")
            break

        # Retrieve repositories from the response
        repositories = response.json()

        # Add repositories to the list
        repos.extend([repo["name"] for repo in repositories])
        print(f"Number of repos:{len(repos)}")

        # Check if there are more pages to retrieve
        if len(repositories) < per_page:
            break
        # Increment the page number for the next request
        page += 1
        time.sleep(5)

    return repos


def write_repos_to_file(org: str, token: str, file_name: str):
    repos = get_all_repos(org, token)
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


def combine_json_files(directory):
    dir_path = Path(directory)
    combined_data = {}

    count = 0
    for file_path in dir_path.glob("*.json"):
        with open(file_path) as file:
            data = json.load(file)

            # Merge data
            for key, value in data.items():
                combined_data[key] = value
                count += 1
    print(count)
    return combined_data


def download_file(url: str, destination_folder_path: Path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination_folder_path, "w", newline="", encoding="utf-8") as file:
            file.write(response.text)
        print(f"file downloaded: {destination_folder_path.name}")
    else:
        print(f"Failed to download: {response.status_code}")
