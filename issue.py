from github import Github

class IssueManager:
    def __init__(self, access_token, repo_name):
        self.g = Github(access_token)
        self.repo = self.g.get_repo(repo_name)

    def list_issues(self, state="open"):
        print("=== Issue一覧 ===")
        for issue in self.repo.get_issues(state=state):
            print(f"Issue #{issue.number}: {issue.title}")

    def create_issue(self, title, body=None):
        new_issue = self.repo.create_issue(title=title, body=body)
        print(f"\n新しいIssueを作成: #{new_issue.number}")
        return new_issue

    def comment_issue(self, issue, comment_body):
        comment = issue.create_comment(comment_body)
        print(f"Issue #{issue.number} にコメントを追加しました。")
        return comment
    
    def close_issue(self, issue):
        issue.edit(state="closed")
        print(f"Issue #{issue.number}:{issue.title} をクローズしました。")

    def auto_reply_to_new_comments(self, issue_number, reply_text, last_comment_id=None):
        """
        指定したIssueに新しいコメントがあれば自動で返信する
        :param issue_number: 監視するIssue番号
        :param reply_text: 返信するテキスト
        :param last_comment_id: 直前に確認した最新コメントID（初回はNone）
        :return: 最新のコメントID
        """
        issue = self.repo.get_issue(number=issue_number)
        comments = list(issue.get_comments())
        if not comments:
            return last_comment_id  # コメントがなければ何もしない

        latest_comment = comments[-1]
        if last_comment_id is None or latest_comment.id != last_comment_id:
            # 新しいコメントがあれば返信
            self.comment_issue(issue, reply_text)
            return latest_comment.id
        return last_comment_id

if __name__ == "__main__":
    ACCESS_TOKEN = "your_access_token_here"
    REPO_NAME = "asato425/github-learning"
    manager = IssueManager(ACCESS_TOKEN, REPO_NAME)

    # 1. Issue一覧を取得
    manager.list_issues()

    # 2. 新しいIssueを作成
    # new_issue = manager.create_issue(
    #     title="PyGithubから作成したIssue",
    #     body="このIssueはPyGithubのサンプルコードから作成されました。"
    # )

    # # 3. Issueにコメントを追加
    # manager.comment_issue(new_issue, "PyGithubからコメントを追加しました。")
    
    # タイトルが一致する最初のIssueをクローズ
    for issue in manager.repo.get_issues(state="open"):
        if issue.title == "PyGithubから作成したIssue":
            manager.close_issue(issue)