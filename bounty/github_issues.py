from github import Github

def import_github_issues(owner, repo, access_token):
    # Create a PyGithub Github object with the provided access token
    g = Github(access_token)

    # Get the repository object
    repo_obj = g.get_repo(f"{owner}/{repo}")

    # Get all open issues for the repository
    issues = repo_obj.get_issues(state="open")

    # Extract relevant information from each issue
    issue_data = []
    for issue in issues:
        issue_data.append({
            "title": issue.title,
            "body": issue.body,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "url": issue.html_url
        })

    return issue_data

def search_issues(owner, repo, access_token):
        # Create a PyGithub Github object with the provided access token
    g = Github(access_token)

    # Get the repository object
    repo_obj = g.get_repo(f"{owner}/{repo}")

    # Get all open issues for the repository
    issues = repo_obj.get_issues(state="open")

    # Extract relevant information from each issue
    issue_data = []
    for issue in issues:
        issue_data.append({

            "title": issue.title,
            "body": issue.body,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "url": issue.html_url
        })
    
    return issue_data
