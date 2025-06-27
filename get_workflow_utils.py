# このスクリプトは、GitHubリポジトリ内のワークフローYAMLファイルを検索・分析するための機能を提供します。
# 主に、特定のトリガーイベントや言語に基づいてワークフローファイルを検索し、重複ファイルを削除するための関数が含まれています。
# また、ワークフローの数を表示する機能もあります。
# さらに、ワークフローのトリガーごとのファイル数を集計し、結果を表示する機能も含まれています。

from collections import defaultdict
import os
import yaml

def search_workflows_trigger(trigger_event, workflows_dir = "workflows"):
    """
    workflowsフォルダ内のYAMLファイルから指定したトリガーイベントを含むワークフローファイル名を出力する
    Args:
        trigger_event (str): 検索するトリガーイベント名（例: push, pull_request など）
    """
    if not os.path.exists(workflows_dir):
        print(f"{workflows_dir}フォルダが存在しません")
        return
    matched_files = []
    for fname in os.listdir(workflows_dir):
        if fname.endswith(('.yml', '.yaml')):
            # どのファイルでもトリガーイベントを検索するかログを表示したい
            #print(f"Checking file: {fname}")
            fpath = os.path.join(workflows_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    # dataの中身を確認するログを出力して
                    #print(f"Data in {fname}: {data}")
                    # print("-" * 40)
                # 'on'キーまたはTrueキーのどちらかが存在するかを判定
                if not data or ('on' not in data and True not in data):
                    continue
                # 'on'またはTrueのどちらかからトリガー情報を取得
                triggers = data.get('on') or data.get(True)
                # triggersの中身を確認するログを出力したい
                #print(f"Triggers in {fname}: {triggers}")
                if isinstance(triggers, dict):
                    if trigger_event in triggers:
                        matched_files.append(fname)
                elif isinstance(triggers, list):
                    if trigger_event in triggers:
                        matched_files.append(fname)
                elif isinstance(triggers, str):
                    if trigger_event == triggers:
                        matched_files.append(fname)
            except Exception as e:
                print(f"{fname} の解析中にエラー: {e}")
    if matched_files:
        print(f"'{trigger_event}': {len(matched_files)}個")
        # for f in matched_files:
        #     print(f)
    else:
        print(f"トリガー '{trigger_event}' を含むワークフローファイルは見つかりませんでした。")
        
def search_workflows_languages(workflows_dir = "workflows"):
    """
    指定されたフォルダ内のすべてのワークフローファイルで主要言語がどのくらい利用されているかを分析します。
    言語が特定できなかったファイルは削除します。
    Args:
        folder_path (str): ワークフローファイルが格納されているフォルダのパス。

    Returns:
        dict: 各言語の利用回数を格納した辞書。
              例: {'Python': 5, 'Node.js': 3, 'Java': 2}
    """
    language_counts = defaultdict(int)
    workflow_extensions = ('.yml', '.yaml') # GitHub Actionsのワークフローファイルの一般的な拡張子

    if not os.path.isdir(workflows_dir):
        print(f"エラー: 指定されたフォルダ '{workflows_dir}' が見つかりません。")
        return {}

    for root, _, files in os.walk(workflows_dir):
        for file_name in files:
            if file_name.lower().endswith(workflow_extensions):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        workflow_content = yaml.safe_load(f)

                    detected_language = None
                    if workflow_content:
                        # ここに主要言語を特定するロジックを記述します。
                        # 例: GitHub Actionsの場合、`uses` キーワードから推測
                        # このロジックはワークフローの内容によって調整が必要です。
                        if 'jobs' in workflow_content:
                            for job_name, job_details in workflow_content['jobs'].items():
                                if 'steps' in job_details:
                                    for step in job_details['steps']:
                                        if 'uses' in step:
                                            action_path = step['uses'].lower()
                                            if 'setup-python' in action_path:
                                                detected_language = 'Python'
                                            elif 'setup-node' in action_path or 'actions/setup-node' in action_path:
                                                detected_language = 'Node.js'
                                            elif 'setup-java' in action_path:
                                                detected_language = 'Java'
                                            elif 'setup-go' in action_path:
                                                detected_language = 'Go'
                                            elif 'actions/checkout' in action_path:
                                                # checkoutアクション自体は言語を特定しないが、
                                                # その後のステップで言語が特定されることが多い
                                                pass
                                            # 他のアクションや言語のパターンを追加
                                            elif 'docker/build-push-action' in action_path:
                                                detected_language = 'Docker/Container'
                                            elif 'ruby/setup-ruby' in action_path:
                                                detected_language = 'Ruby'
                                            elif 'php/setup-php' in action_path:
                                                detected_language = 'PHP'

                                        elif 'run' in step:
                                            # 'run' コマンド内のキーワードから推測
                                            run_command = step['run'].lower()
                                            if 'python' in run_command and 'pip' in run_command:
                                                detected_language = 'Python'
                                            elif 'npm' in run_command or 'node' in run_command:
                                                detected_language = 'Node.js'
                                            elif 'java' in run_command or 'maven' in run_command or 'gradle' in run_command:
                                                detected_language = 'Java'
                                            elif 'go build' in run_command or 'go run' in run_command:
                                                detected_language = 'Go'
                                            elif 'bundle install' in run_command or 'rake' in run_command:
                                                detected_language = 'Ruby'
                                            elif 'composer install' in run_command:
                                                detected_language = 'PHP'
                                            elif 'dotnet' in run_command:
                                                detected_language = 'C#'
                                            elif 'cargo build' in run_command:
                                                detected_language = 'Rust'


                    if detected_language:
                        language_counts[detected_language] += 1
                    else:
                        # 言語を特定できなかった場合はファイルを削除
                        os.remove(file_path)
                        print(f"言語特定不可のため削除: {file_path}")

                except yaml.YAMLError as e:
                    os.remove(file_path)
                    print(f"警告: ファイル '{file_path}' のYAML解析エラー: {e}が発生したため削除")
                except Exception as e:
                    os.remove(file_path)
                    print(f"警告: ファイル '{file_path}' の処理中にエラーが発生したため削除: {e}")


    language_usage = dict(language_counts)
    if language_usage:
        for lang, count in sorted(language_usage.items(), key=lambda item: item[1], reverse=True):
            print(f"- {lang}: {count} ファイル")
    else:
        print("指定されたフォルダでワークフローファイルが見つからなかったか、分析できませんでした。")
def remove_duplicate_files_in_dir(directory, extensions=(".yml", ".yaml")):
    """
    指定ディレクトリ内のYAMLファイルについて、内容が完全一致する重複ファイルを削除する（1つだけ残す）

    Args:
        directory (str): チェックするディレクトリ
        extensions (tuple): 対象とする拡張子
    """
    content_map = {}
    if not os.path.isdir(directory):
        print(f"{directory} は存在しないかディレクトリではありません")
        return
    for fname in os.listdir(directory):
        if fname.endswith(extensions):
            fpath = os.path.join(directory, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                if content in content_map:
                    os.remove(fpath)
                    print(f"重複のため削除: {fpath}")
                else:
                    content_map[content] = fpath
            except Exception as e:
                print(f"{fpath} の処理中にエラー: {e}")

def show_workflows_count(directory="workflows", extensions=(".yml", ".yaml")):
    """
    指定ディレクトリ内のYAMLファイルの数を表示する

    Args:
        directory (str): チェックするディレクトリ
        extensions (tuple): 対象とする拡張子
    """
    if not os.path.isdir(directory):
        print(f"{directory} は存在しないかディレクトリではありません")
        return
    count = 0
    for fname in os.listdir(directory):
        if fname.endswith(extensions):
            count += 1
    print(f"{directory} 内のYAMLファイル数: {count}")

def show_workflows_summary(workflows_dir):
    """
    workflowsディレクトリ内で主要トリガー・主要言語ごとのファイル数を出力する
    """
    major_triggers = ['push', 'pull_request', 'schedule', 'workflow_dispatch']

    print("\n=== 言語ごとのワークフローファイル数 ===")
    search_workflows_languages(workflows_dir)
    print("=== トリガーごとのワークフローファイル数 ===")
    for trigger in major_triggers:
        search_workflows_trigger(trigger, workflows_dir)

    show_workflows_count(workflows_dir)

