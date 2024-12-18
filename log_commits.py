import requests
from datetime import datetime
import os

# GitHub username and token
GITHUB_USERNAME = os.getenv("USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# WakaTime API endpoint for fetching stats
WAKATIME_API_URL = "https://wakatime.com/api/v1/users/current/stats"

# Log file for storing commit history
LOG_FILE = "activity_log.md"

# GitHub API endpoint for fetching repos
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?type=public&per_page=100"

# Fetch repositories
def fetch_repositories():
    response = requests.get(GITHUB_API_URL, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code}")
        return []

# Fetch commits for each repository
def fetch_commits(repo_name):
    commits_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits?per_page=5"
    response = requests.get(commits_url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching commits for {repo_name}: {response.status_code}")
        return []

# Fetch WakaTime stats
def fetch_wakatime_stats():
    response = requests.get(WAKATIME_API_URL, headers={"Authorization": f"Bearer {os.getenv('WAKATIME_API_KEY')}"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching WakaTime stats: {response.status_code}")
        return {}

# Main function to log commits
def generate_log():
    repositories = fetch_repositories()
    log_entries = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Fetch WakaTime stats
    wakatime_stats = fetch_wakatime_stats()
    total_time = wakatime_stats.get("data", {}).get("grand_total", {}).get("text", "0 hours")
    
    # Process each repository
    for repo in repositories:
        repo_name = repo["name"]
        print(f"Processing {repo_name}...")
        commits = fetch_commits(repo_name)

        if commits:
            log_entries.append(f"## {repo_name} ({today})")
            for commit in commits:
                commit_message = commit["commit"]["message"]
                commit_author = commit["commit"]["author"]["name"]
                commit_date = commit["commit"]["author"]["date"]
                languages_used = ", ".join([language["name"] for language in repo["languages"]])  # Add languages later
                log_entries.append(f"- {commit_message} by {commit_author} on {commit_date}. Languages: {languages_used}")
            log_entries.append("")  # Add empty line between repositories

    # Write logs to the file
    with open(LOG_FILE, "w") as log_file:
        log_file.write("\n".join(log_entries))
        log_file.write(f"\n### Total Coding Time: {total_time}\n")
        print(f"Logs written to {LOG_FILE}")

# Run the script
if __name__ == "__main__":
    generate_log()
