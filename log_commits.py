import os
import requests
import base64

# Load environment variables (replace with your token if not using secrets)
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # GitHub Personal Access Token
LOG_REPO = "Hamzaisadev/coding-actvity-log"  # Replace with your central repo name (username/repo)
LOG_BRANCH = "main"  # Branch of the log repo to update
LOG_FILE = "README.md"  # The file to update in the log repo

# GitHub API endpoint and headers
BASE_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def get_repos():
    """Fetch all repositories for the authenticated user."""
    url = f"{BASE_URL}/user/repos"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code}")
        print(response.json())
        return []


def get_latest_commit(repo_name, branch="main"):
    """Fetch the latest commit for a given repository and branch."""
    url = f"{BASE_URL}/repos/{repo_name}/commits?sha={branch}&per_page=1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        commits = response.json()
        if commits:
            return commits[0]  # Return the latest commit
    else:
        print(f"Error fetching commits for {repo_name}: {response.status_code}")
        print(response.json())
    return None


def get_readme_content():
    """Fetch the current content of the README.md file in the log repo."""
    url = f"{BASE_URL}/repos/{LOG_REPO}/contents/{LOG_FILE}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content = response.json()
        decoded_content = base64.b64decode(content["content"]).decode("utf-8")
        return decoded_content, content["sha"]  # Return the content and its SHA
    elif response.status_code == 404:
        print("README.md not found. A new one will be created.")
        return "", None
    else:
        print(f"Error fetching README.md: {response.status_code}")
        print(response.json())
        return None, None


def update_readme(new_log_entry):
    """Update the README.md file with the new log entry."""
    current_content, sha = get_readme_content()
    if current_content is None:
        return

    updated_content = current_content + "\n" + new_log_entry
    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    url = f"{BASE_URL}/repos/{LOG_REPO}/contents/{LOG_FILE}"
    payload = {
        "message": "Updated Activity Log with new commit details",
        "content": encoded_content,
        "branch": LOG_BRANCH,
    }
    if sha:
        payload["sha"] = sha  # Include the SHA if the file already exists

    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("README.md updated successfully.")
    else:
        print(f"Error updating README.md: {response.status_code}")
        print(response.json())


def log_commit(repo_name, branch, commit):
    """Create a log entry for a given commit."""
    log_entry = (
        f"- **Repository**: [{repo_name}](https://github.com/{repo_name})\n"
        f"  - **Branch**: {branch}\n"
        f"  - **Commit Message**: {commit['commit']['message']}\n"
        f"  - **Author**: {commit['commit']['author']['name']} ({commit['commit']['author']['email']})\n"
        f"  - **Date**: {commit['commit']['author']['date']}\n"
        f"  - **Commit URL**: {commit['html_url']}\n"
    )
    return log_entry


def main():
    """Main script to fetch commits and update the activity log."""
    print("Fetching repositories...")
    repos = get_repos()

    all_logs = []
    for repo in repos:
        repo_name = repo["full_name"]
        default_branch = repo.get("default_branch", "main")
        print(f"Fetching latest commit for {repo_name}...")
        latest_commit = get_latest_commit(repo_name, default_branch)

        if latest_commit:
            log_entry = log_commit(repo_name, default_branch, latest_commit)
            all_logs.append(log_entry)

    if all_logs:
        print("Updating activity log...")
        full_log_entry = "\n".join(all_logs)
        update_readme(full_log_entry)
    else:
        print("No new commits found to log.")


if __name__ == "__main__":
    main()
