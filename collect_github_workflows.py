# このファイルの内容をコメントで説明してください。
# このファイルは、GitHubのリポジトリから特定の条件に基づいてワークフローファイルを収集するPythonスクリプト
# です。GitHubのAPIを使用して、指定されたスター数以上のリポジトリから
# `.github/workflows` ディレクトリ内のワークフローファイル（`.yml` または `.yaml`）を取得し、
# それらのメタデータと内容をローカルディレクトリに保存します。
## 収集されたワークフローファイルは、データセットとして利用可能になります。 

import os
import time
from github import Github
from github.GithubException import UnknownObjectException, RateLimitExceededException, BadCredentialsException, GithubException
from typing import List, Dict, Any, Optional

import yaml
from collections import defaultdict

from get_workflow_utils import remove_duplicate_files_in_dir, show_workflows_summary # 分析用にインポート

def get_github_workflow_files(
    github_token: str,
    min_stars: int,
    max_repos: int,
    output_dir: str = "github_workflows_dataset" # このフォルダの中に直接保存
) -> List[Dict[str, Any]]:
    """
    GitHubの指定されたスター数以上のリポジトリから、.github/workflowsフォルダ内の
    ワークフローファイル (.ymlまたは.yaml) をデータセットとして取得します。

    Args:
        github_token (str): GitHub Personal Access Token (PAT)。
        min_stars (int): 検索対象リポジトリの最小スター数。
        max_repos (int): 取得を試みる最大リポジトリ数。
        output_dir (str): 取得したワークフローファイルを保存するディレクトリ名。この中にファイルが直接保存されます。

    Returns:
        List[Dict[str, Any]]: 取得されたワークフローファイルのメタデータと内容のリスト。
                               各辞書には 'repo_full_name', 'file_path', 'file_content' が含まれます。
    """
    
    # PyGithubクライアントの初期化
    try:
        g = Github(github_token)
        # トークンが有効か確認（初回API呼び出しで認証エラーを早期検出）
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
    except BadCredentialsException:
        print("Error: Invalid GitHub token. Please check your token.")
        return []
    except GithubException as e:
        print(f"Error initializing GitHub client: {e}")
        return []

    workflow_data = []
    processed_repos_count = 0

    print(f"Searching for repositories with more than {min_stars} stars...")

    try:
        # スター数でリポジトリを検索
        query = f"stars:>{min_stars}"
        repositories = g.search_repositories(query=query)

        # 出力ディレクトリの作成（ここがファイルの直接保存先になります）
        os.makedirs(output_dir, exist_ok=True)

        for repo in repositories:
            if processed_repos_count >= max_repos:
                print(f"Reached maximum repository limit ({max_repos}). Stopping.")
                break

            print(f"Processing repository: {repo.full_name} (Stars: {repo.stargazers_count})")

            try:
                # .github/workflows ディレクトリの内容を取得
                contents = repo.get_contents(".github/workflows/")
                
                # contents が単一のファイルオブジェクトの場合もあるのでリスト化
                if not isinstance(contents, list):
                    contents = [contents]

                for content_file in contents:
                    if content_file.type == "file" and \
                       (content_file.name.endswith(".yml") or content_file.name.endswith(".yaml")):
                        
                        try:
                            file_content = content_file.decoded_content.decode('utf-8')

                            workflow_info = {
                                "repo_full_name": repo.full_name,
                                "file_path": content_file.path,
                                "file_content": file_content
                            }
                            workflow_data.append(workflow_info)

                            # ファイルを直接 output_dir に保存
                            # ファイル名が重複する場合、後から保存されるファイルで上書きされます
                            file_save_path = os.path.join(output_dir, content_file.name)
                            with open(file_save_path, 'w', encoding='utf-8') as f:
                                f.write(file_content)
                            print(f"  - Saved: {file_save_path}")

                        except UnicodeDecodeError:
                            print(f"  - Warning: Could not decode content of {content_file.path} in {repo.full_name} (possible binary file). Skipping.")
                        except Exception as e:
                            print(f"  - Error reading file {content_file.path} in {repo.full_name}: {e}")

            except UnknownObjectException:
                print(f"  - No .github/workflows directory found in {repo.full_name}")
            except RateLimitExceededException:
                rate_limit = g.get_rate_limit()
                reset_time = rate_limit.core.reset.timestamp()
                sleep_duration = max(0, reset_time - time.time() + 5) # 5秒余裕を持たせる
                print(f"  - Rate limit exceeded. Waiting for {sleep_duration:.0f} seconds until {rate_limit.core.reset}...")
                time.sleep(sleep_duration)
                continue # レートリミット後に現在のリポジトリを再試行するためにループを継続
            except GithubException as e:
                print(f"  - Error accessing {repo.full_name}: {e}")

            processed_repos_count += 1
            time.sleep(0.5) # APIへの負荷を減らすため、リポジトリ処理ごとに少し待つ
            
    except RateLimitExceededException:
        rate_limit = g.get_rate_limit()
        reset_time = rate_limit.search.reset.timestamp() # 検索APIのレートリミットは別
        sleep_duration = max(0, reset_time - time.time() + 5)
        print(f"Global search rate limit exceeded. Waiting for {sleep_duration:.0f} seconds until {rate_limit.search.reset}...")
        time.sleep(sleep_duration)
        print("Please retry running the script after the reset time.")
    except GithubException as e:
        print(f"An unexpected GitHub API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print(f"\nFinished. Total workflow files collected: {len(workflow_data)}")
    print(f"Files saved to: {os.path.abspath(output_dir)}")
    return workflow_data

# --- 使用例 ---
if __name__ == "__main__":
    # GitHub Personal Access Token を環境変数から取得することを強く推奨します
    github_pat = os.environ.get("GITHUB_TOKEN") 
    if not github_pat:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set the GITHUB_TOKEN environment variable with your GitHub Personal Access Token.")
        print("Example: export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'")
        exit()

    # 検索条件の定義
    minimum_stars = 10000  # 例: 10000スター以上のリポジトリを対象
    maximum_repositories = 100 # 例: 最大50個のリポジトリからワークフローファイルを取得

    # print(f"Starting workflow file collection for repos with >{minimum_stars} stars, up to {maximum_repositories} repositories.")

    # ワークフローファイルの収集
    collected_workflows = get_github_workflow_files(
        github_token=github_pat,
        min_stars=minimum_stars,
        max_repos=maximum_repositories
    )
    #remove_duplicate_files_in_dir("github_workflows_dataset", extensions=(".yml", ".yaml")) # 重複ファイルを削除
    show_workflows_summary(workflows_dir="github_workflows_dataset") # 分析結果を表示
    