import json

import config
from typing import List, Iterator

import github
from github import Github, Repository
from github import Issue
from github import PullRequest


def help(topics=["Python"], organization="airbnb"):
    gh = Github(config.github_oauth)
    repos = gh.get_organization(organization).get_repos()
    topics = [topic.lower() for topic in topics]

    for repo in get_matching_repos(repos, topics):
        stats_contributors = repo.get_stats_contributors()  # This list is always sorted by total commits in ascending order
        if not stats_contributors:
            continue
        for stats_contributor in reversed(stats_contributors):
            return stats_contributor.author


def repo_matches_topic(repo, topic):
    """Checks if a repository matches a certain topic
    Returns true in the following cases:
    * The topic is contained in the repository labels
    * The topic is one of the programming languages used by the repository
    * The topic is one of the libraries used by the repository
    * The topic matches a certain keyword and the repository fulfills the keywords requirements

    Args:
        repo (github.Repository): Github repository object
        topic (str): Topic name

    Returns:
        (bool): True if repository matches the topic, False otherwise
    """

    # True if topic name is contained in a repository label
    labels = repo.get_labels()
    for label in labels:
        if topic in label.name:
            return True

    # True if topic name matches any programming language used in the repository
    languages = [language.lower() for language in list(repo.get_languages())]
    if topic in languages:
        return True

    # True if topic name matches a library used by the project (exemplary implementation)
    root_files = set([file.name for file in repo.get_contents('.')])
    if "requirements.txt" in root_files:
        content = repo.get_file_contents('requirements.txt').decoded_content.decode('utf8')
        libs = [line.split("=")[0] for line in content.split("\n")]
        if topic in libs:
            return True
    if "package.json" in root_files:
        content = json.loads(repo.get_file_contents('package.json').decoded_content)
        libs = list(content.get("dependencies", {})) + list(content.get("devDependencies", {}).keys())
        if topic in libs:
            return True

    # True if topic name matches any key words (exemplary implementation)
    if topic == "docker" and 'Dockerfile' in root_files:
        return True
    if topic in ["travis", "ci", "cd"] and '.travis.yml' in root_files:
        return True
    linters = {'.eslintrc', '.jslintrc ', '.jshintrc', '.pylintrc'}
    if topic == "lint" and linters.intersection(root_files):
        return True
    code_quality_checkers = {'.codacy.yml', '.codeclimate.yml'}
    if topic == "quality" and (code_quality_checkers | linters).intersection(root_files):
        return True

    # False if none of the above match
    return False


def get_matching_repos(repos, topics):
    """Checks a list of repositories and yields those that match all topics in a list

    Args:
        repos (github.PaginatedList): Guthub PaginatedList that yields repositories
        topics list(str): List of topic names

    Yields:
        (github.Repository): Repository that matches all topics
    """
    for repo in repos:
        all_topics_match = all(repo_matches_topic(repo, topic) for topic in topics)
        if all_topics_match:
            yield repo

if __name__ == "__main__":
    help(organization="hashbang")
