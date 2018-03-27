import json


def ask_for_help(user, topics, organization="LaraTUB"):
    """Example implementation of the "Ask for help" feature

    This method needs to send a lot of queries to Github and is not yet making use of any concurrency, which is why it
    is using heuristics to improve the overall response time. It is not necessarialy returning the best match possible,
    but the person with the most commits on the first repository found that is matching all provided topics.
    """
    assert len(topics) >= 1

    repos = user.get_organization(organization).get_repos()
    topics = [topic.lower() for topic in topics]

    for repo in get_matching_repos(repos, topics):
        stats_contributors = repo.get_stats_contributors()  # This list is always sorted by total commits in ascending order
        if not stats_contributors:
            continue
        for stats_contributor in reversed(stats_contributors):
            author = stats_contributor.author
            if organization in list(author.get_organizations()):
                if len(topics) == 1:
                    topics_string = topics[0]
                else:
                    topics_string = "{} and {}".format(', '.join(topics[:-1]), topics[-1])
                return (f"You should ask ({author.name})[{author.url}] for help. He/She has the most contributions at "
                        f"the repository ({repo.name})[{repo.url}], which is related to the topics {topics_string}")   # TODO Slack links
    return ("Sorry, I did not find anyone in your organization that can help you with that.\n"
            "Consider rephrasing or reducing the amount of the topics.")


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


if __name__ == "__main__":
    from github import Github
    from feature_prototypes import config
    user = Github(config.github_oauth).get_user()
    ask_for_help(user, ["Python"], "airbnb")
