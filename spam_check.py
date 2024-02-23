#!/usr/bin/env python

import os
import sys
import requests
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_GPT4 = os.getenv('USE_GPT4')

REPO_NAME = os.getenv('GITHUB_REPOSITORY')
PR_NUMBER = os.getenv('PR_NUMBER')

FILES_TO_EXCLUDE = os.getenv('FILES_TO_EXCLUDE').split(',')
MAX_FILES = int(os.getenv('MAX_FILES'))

def format_commit_details(commit_details):
    """
    Formats commit details and returns a dictionary with 'additions', 'deletions', and 'patch' keys.
    
    Parameters:
    - commit_details: dictionary containing 'additions', 'deletions', and 'patch' keys
    
    Returns: 
    - dict: with formatted commit details
    """

    formatted_commit_details = {
        "additions": commit_details['additions'], "deletions": commit_details['deletions']
    }
    cleaned_patch_str = re.sub(r"@@.*?@@", '', commit_details['patch'])
    cleaned_patch = []
    for line in cleaned_patch_str.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            cleaned_patch.append(stripped_line)
    
    formatted_commit_details['patch'] = cleaned_patch
    return formatted_commit_details


def fetch_commit_diff(commit_url: str):
    """
    Fetches the commit difference using the provided commit URL.

    Parameters:
    - commit_url (str): The URL of the commit.

    Returns:
    - str: A JSON string containing the details of the commit files.
    """

    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(commit_url, headers=headers)
    response.raise_for_status()
    commit_data = response.json()
    files = commit_data.get('files', [])

    for file in files:
        if file['filename'] in FILES_TO_EXCLUDE:
            files.remove(file)

    if len(files) > int(MAX_FILES):
        files = files[:int(MAX_FILES)]

    commit_details = {}
    for file in files:
        commit_details[file['filename']] = format_commit_details(file)

    return json.dumps(commit_details, indent=0)

def is_spammy_commit(commit):
    """
    Function to analyze a commit and determine if it is spammy or not.

    Parameters:
    - commit: the commit to be analyzed

    Returns:
    - True if the commit is identified as spam, False otherwise
    """
    model="gpt-4" if USE_GPT4 == "true" else "gpt-3.5-turbo"
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=model)

    commit_url = commit['url']

    content_to_analyze = fetch_commit_diff(commit_url)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly experienced open source contributor. You are responsible for analyzing the content of a commit and determining whether it is spammy or not. You are not responsible for any actions taken by the user. You should only respond with 'spam' or 'good'."),
        ("system", "Some examples of spammy contribution can be addition of text or code which is malicious or does not make sense at that place like random usernames, links, comments, changing case of text or any other similar additions"),
        ("user",
         "analyze the following content and determine if it is spammy: \n\n{input}")
    ])

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    response = chain.invoke({"input": content_to_analyze})

    return 'spam' in response.lower()


def get_pr_commits():
    """
    This function makes a GET request to the GitHub API to retrieve the commits associated with a specific pull request.
 
    Parameters:
    None
    
    Returns: 
    - list: a list of commits in JSON format.
    """
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{PR_NUMBER}/commits"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    commits = response.json()
    return commits


def main():
    commits = get_pr_commits()
    spammy_commits_detected = False

    for commit in commits:
        if commit['parents'] and len(commit['parents']) > 1:
            print(f"Commit {commit['sha']} is a merge commit. Skipping.")
            continue
        if is_spammy_commit(commit):
            print(f"Commit {commit['sha']} looks spammy.")
            spammy_commits_detected = True
        else:
            print(f"Commit {commit['sha']} looks good.")

    if spammy_commits_detected:
        sys.exit(1)  # Exit with a non-zero status code to fail the CI


if __name__ == "__main__":
    main()
