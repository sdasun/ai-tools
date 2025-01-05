import json
import os
import datetime
import requests
import openai
from rich import print as rprint
from dotenv import load_dotenv
import typer

load_dotenv()

# Constants
GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4-turbo-preview")
GITLAB_USERNAME = os.getenv("GITLAB_USERNAME")
GITLAB_USER_ID = os.getenv("GITLAB_USER_ID")
GITLAB_MR_PREFIX = os.getenv("GITLAB_MR_PREFIX")

# Workflow labels
WORKFLOW_LABELS = [
    "workflow::todo",
    "workflow::done",
    "workflow::draft",
    "workflow::doing",
    "workflow::review",
    "workflow::backlog",
    "workflow::waiting_for_others"
]

app = typer.Typer()

def get_gitlab_data(endpoint: str, params: dict) -> list[dict]:
    headers = {"Private-Token": GITLAB_API_TOKEN}
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_gitlab_merge_requests(period_start: str, period_end: str) -> list[dict]:
    params = {
        "author_username": GITLAB_USERNAME,
        "created_after": period_start,
        "created_before": period_end,
        "state": "all"
    }
    data = get_gitlab_data("merge_requests", params)
    return [
        {
            'id': item['iid'],
            'title': item['title'],
            'state': item['state'],
            'description': item.get('description', ''),
            'reviewers': [reviewer['name'].split()[0] for reviewer in item['reviewers'] if reviewer['username'] != GITLAB_USERNAME],
            'target_branch': item['target_branch'],
            'labels': item['labels'],
            'web_url': item['web_url'],
        }
        for item in data if item['state'] != 'closed'
    ]

def get_gitlab_issues_assigned_to_me(period_start: str, period_end: str) -> list[dict]:
    params = {
        "assignee_id": GITLAB_USER_ID,
        "created_after": period_start,
        "state": "all"
    }
    data = get_gitlab_data("issues", params)
    return [
        {
            'id': item['iid'],
            'title': item['title'],
            'state': item['state'],
            'description': item.get('description', ''),
            'labels': item['labels'],
            'web_url': item['web_url'],
            'issue_type': item['issue_type'],
            'mr_count': item['merge_requests_count'],
        }
        for item in data if item['state'] != 'closed' or item['closed_at'].split('T')[0] >= period_start.split('T')[0]
    ]

def categorize_items(items: list[dict]) -> dict[str, list[dict]]:
    categorized = {label: [] for label in WORKFLOW_LABELS}
    categorized['other'] = []
    
    for item in items:
        categorized_flag = False
        for label in WORKFLOW_LABELS:
            if label in item['labels']:
                categorized[label].append(item)
                categorized_flag = True
                break
        if not categorized_flag:
            categorized['other'].append(item)
    
    return categorized

def summarize_with_chatgpt(activities: list[dict], issues: list[dict], outraw: bool = False) -> str:
    categorized_activities = categorize_items(activities)
    categorized_issues = categorize_items(issues)

    client = openai.Client(api_key=CHATGPT_API_KEY)
    system_message = """
    You are a helpful assistant rewriting GitLab issues/tasks and merge requests for a non-technical person.
    The items are categorized based on their workflow labels. Use this structure to organize your summary:

    *Completed*
    [Include items from workflow::done]

    *In Progress*
    [Include items from workflow::doing and workflow::review]

    *To Do*
    [Include items from workflow::todo]

    *Waiting*
    [Include items from workflow::waiting_for_others]

    *Backlog*
    [Include items from workflow::backlog]

    *Other*
    [Include items from not assigned to a category and workflow::draft]

    For each item:
    - Write responses in past participle tense for completed items, present tense for ongoing items.
    - Provide only a summary if the description is more than 2 lines.
    - Convert commands in the title to a response. (e.g., "Fix user registration issue" to "Fixed user registration issue")
    - Elaborate on details if they are too short.
    - Convert requests to tasks. (e.g., "Please attend to user registration issue" to "Fixing user registration issue")
    - Convert git semantics to non-technical terms.
    - Convert Gherkin format to plain English.
    - If there is a non-zero mr_count on open state, mention that changes are in an MR.
    - Output the response slack friendly markdown without using code blocks. Also include the MR/Issues link if applicable.
    - For MRs, link sudo links as follows: `[MR #943](MR/943)`.
    - Include links to issues and MRs where applicable.

    Abriviations:
    BBW: Big Bad Wolf
    MS: Microsoft
    KT: Knowledge Transfer
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Merge Requests:\n\n{categorized_activities}\n\nIssues:{categorized_issues}"}
    ]
    if outraw:
        return json.dumps(messages)
    try:
        response = client.chat.completions.create(
            model=CHATGPT_MODEL,
            messages=messages,
            max_tokens=2000,
            temperature=0.5
        )
        result = response.choices[0].message.content
        return result.replace("(MR/", f"({GITLAB_MR_PREFIX}")
    except openai.APIError as e:
        rprint(f"[bold red]An error occurred: {e}[/bold red]")
        return None

@app.command()
def generate_report(days: int = typer.Option(1, help="Number of days to include in the report")):
    rprint("[bold]Generating Daily Standup Report[/bold]")
    
    today = datetime.date.today()
    period_end = today.strftime("%Y-%m-%dT12:30:00Z")
    period_start = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%dT06:30:00Z")
    
    activities = get_gitlab_merge_requests(period_start, period_end)
    issues = get_gitlab_issues_assigned_to_me(period_start, period_end)
    summary = summarize_with_chatgpt(activities, issues)
    
    if summary:
        with open("daily_standup_report.md", "w") as f:
            f.write(summary)
        rprint("[bold green]Summary generated successfully:[/bold green]")
        rprint(summary)
        rprint("\n[bold green]Report saved to daily_standup_report.md[/bold green]")
    else:
        rprint("[bold red]Failed to generate summary.[/bold red]")


@app.command()
def generate_git_repo_name(workflows: list[str] = typer.Option(['todo'], help="List of workflows to include in the report"), use_daily_report: bool = typer.Option(False, help="Use the daily report to generate the repository name")):
    rprint("[bold]Generating Git Repository Name[/bold]")
    if not use_daily_report:
        generate_git_repo_name_from_issues(workflows)
    else:
        generate_git_repo_name_from_daily_report()

if __name__ == "__main__":
    app()