#!/usr/bin/env python

import os
import sys
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER')
repo_name = os.getenv('GITHUB_REPOSITORY')
pr_number = os.getenv('PR_NUMBER')


def fetch_commit_diff(commit_url, token):
    """
    Fetch the commit diff from GitHub API.
    """
    headers = {'Authorization': f'token {token}'}
    response = requests.get(commit_url, headers=headers)
    response.raise_for_status()
    commit_data = response.json()
    files = commit_data.get('files', [])

    commit_details = {}
    for file in files:
        commit_details[file['filename']] = {
            "additions": file['additions'], "deletions": file['deletions'], "changes": file['changes']}

    return json.dumps(commit_details)


def get_pr_commits(owner, repo, pr_num, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/commits"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    commits = response.json()
    return commits


def is_spammy_commit(commit, openai_api_key, github_token):
    """
    Determine if a commit is spammy using OpenAI.
    """
    llm = ChatOpenAI(api_key=openai_api_key)

    commit_url = commit['url']

    content_to_analyze = fetch_commit_diff(commit_url, github_token)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly experienced open source contributor. You are responsible for analyzing the content of a commit and determining whether it is spammy or not. You are not responsible for any actions taken by the user. You should only respond with 'spam' if the content is spammy."),
        ("user",
         "analyze the following content and determine if it is spammy: \n\n{input}")
    ])

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    response = chain.invoke({"input": content_to_analyze})

    return 'spam' in response.lower()


def main():
    commits = get_pr_commits(repo_owner, repo_name, pr_number, GITHUB_TOKEN)
    spammy_commits_detected = False

    for commit in commits:
        if is_spammy_commit(commit, OPENAI_API_KEY, GITHUB_TOKEN):
            print(f"Commit {commit['sha']} looks spammy.")
            spammy_commits_detected = True
        else:
            print(f"Commit {commit['sha']} looks good.")

    if spammy_commits_detected:
        sys.exit(1)  # Exit with a non-zero status code to fail the CI


if __name__ == "__main__":
    main()
