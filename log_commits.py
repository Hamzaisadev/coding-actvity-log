import requests
from datetime import datetime
import os

# Environment variables
GITHUB_USERNAME = ("hamzisdev")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
WAKATIME_API_KEY = os.getenv("WAKATIME_API_KEY")

# API URLs
WAKATIME_API_URL = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?type=public&per_page=100"

print("USERNAME:", os.getenv("USERNAME"))
print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN"))
print("WAKATIME_API_KEY:", os.getenv("WAKATIME_API_KEY"))

# Log file
LOG_FILE = "activity_log.md"

# Fetch repositories
def fetch_repositories():
    response = requests.get(GITHUB_API_URL, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code} - {response.text}")
        return []

# Fetch commits
def fetch_commits(repo_name):
    commits_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits?per_page=100"
    response = requests.get(commits_url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching commits for {repo_name}: {response.status_code} - {response.text}")
        return []

# Fetch repository languages
def fetch_languages(repo):
    languages_url = repo["languages_url"]
    response = requests.get(languages_url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return ", ".join(response.json().keys())
    else:
        print(f"Error fetching languages for {repo['name']}: {response.status_code} - {response.text}")
        return "Unknown"

# Fetch WakaTime stats
def fetch_wakatime_stats():
    response = requests.get(WAKATIME_API_URL, headers={"Authorization": f"Bearer {WAKATIME_API_KEY}"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching WakaTime stats: {response.status_code} - {response.text}")
        return {}

# Generate log
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
        languages_used = fetch_languages(repo)
        commits = fetch_commits(repo_name)
        
        if commits:
            log_entries.append(f"## {repo_name} ({today})")
            for commit in commits:
                commit_message = commit["commit"]["message"]
                commit_author = commit["commit"]["author"]["name"]
                commit_date = commit["commit"]["author"]["date"]
                log_entries.append(f"- {commit_message} by {commit_author} on {commit_date}. Languages: {languages_used}")
            log_entries.append("")  # Add empty line between repositories
        else:
            print(f"No commits found for {repo_name}.")

    # Write logs to the file
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write("\n".join(log_entries))
            log_file.write(f"\n### Total Coding Time: {total_time}\n")
            print(f"Logs written to {LOG_FILE}")
    except Exception as e:
        print(f"Error writing to log file: {e}")

# Run the script
if __name__ == "__main__":
    generate_log()
