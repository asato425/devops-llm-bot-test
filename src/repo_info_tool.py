import requests

def get_repo_info(owner, repo):
    """
    Fetch repository information from GitHub API.

    Args:
        owner (str): GitHub username or organization name.
        repo (str): Repository name.

    Returns:
        dict: Repository information including stars, forks, and latest commit.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        repo_info = {
            "name": data.get("name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "latest_commit": data.get("updated_at")
        }
        return repo_info
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository information: {e}")
        return None

if __name__ == "__main__":
    owner = input("Enter the GitHub owner/organization name: ")
    repo = input("Enter the repository name: ")
    info = get_repo_info(owner, repo)
    if info:
        print("Repository Information:")
        print(f"Name: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Stars: {info['stars']}")
        print(f"Forks: {info['forks']}")
        print(f"Latest Commit: {info['latest_commit']}")
    else:
        print("Failed to fetch repository information.")
