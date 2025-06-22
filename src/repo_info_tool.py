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
            "name": data.get("name"), # リポジトリ名の取得
            "description": data.get("description"), # リポジトリの説明の取得
            "stars": data.get("stargazers_count"), # スターの数の取得
            "forks": data.get("forks_count"), # フォークの数の取得
            "latest_commit": data.get("updated_at") # 最新のコミット日時の取得
        }
        return repo_info
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository information: {e}")
        return None

def count_workflow_files(owner, repo):
    """
    Count the number of YAML files in the .github/workflows folder of a repository.

    Args:
        owner (str): GitHub username or organization name.
        repo (str): Repository name.

    Returns:
        int: Number of YAML files in the workflows folder.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        yaml_files = [file for file in data if file['name'].endswith('.yml') or file['name'].endswith('.yaml')]
        return len(yaml_files)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflow files: {e}")
        return 0

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

    workflow_count = count_workflow_files(owner, repo)
    print(f"Number of workflow YAML files: {workflow_count}")
