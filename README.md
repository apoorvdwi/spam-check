![spam-check](https://socialify.git.ci/apoorvdwi/spam-check/image?description=1&descriptionEditable=Spam%20Check%20leverages%20the%20GitHub%20Actions%20platform%20to%20scan%20incoming%20pull%20requests%20for%20signs%20of%20spam.&font=Inter&language=1&name=1&owner=1&pattern=Plus&theme=Light)

# Spam Check GitHub Action

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/apoorvdwi/spam-check/.github%2Fworkflows%2Fbuild-image.yml)
![GitHub License](https://img.shields.io/github/license/apoorvdwi/spam-check)

This GitHub Action, named **Spam Check**, is designed to help maintainers identify and filter out spam pull requests (PRs) in their repositories. By integrating this action into their GitHub workflows, maintainers can automatically flag potential spam, allowing them to focus on legitimate contributions.

## Description

Spam Check leverages the GitHub Actions platform to scan incoming pull requests for signs of spam. It utilizes a Docker container to run the spam checking logic. This action is essential for open-source projects that receive a high volume of PRs and need a way to quickly sift through them to maintain project integrity.

## Features

- Automatic scanning of pull requests for spam content.
- Utilizes a Docker container to isolate the checking process.
- Easy integration with existing GitHub workflows.

## Usage

Create an OPENAI API key and add it to repository secrets.

To use this action in your GitHub repository, create a workflow file (e.g., `.github/workflows/spam-check.yml`) and include the following configuration:

```yaml
name: Spam Check Workflow

on:
  pull_request:
    types: [opened, edited, reopened, synchronize]

jobs:
  spam-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Run Spam Checker
        uses: apoorvdwi/spam-check@v3.0
        with:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          MAX_FILES: 5
          FILES_TO_EXCLUDE: ''
          USE_GPT4: false
```

## Examples
- PR with failed check - https://github.com/apoorvdwi/spam-check/pull/3
- PR with success check - https://github.com/apoorvdwi/spam-check/pull/4
