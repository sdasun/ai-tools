import os
import requests
import openai
import subprocess
import re
from rich import print as rprint
from dotenv import load_dotenv
import typer

load_dotenv()

# Constants
GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4-turbo-preview")

app = typer.Typer()

def get_issue_details(issue_number):
    url = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/issues/{issue_number}"
    headers = {"PRIVATE-TOKEN": GITLAB_API_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def generate_branch_name(issue_number, issue_title, issue_description):
    client = openai.Client(api_key=CHATGPT_API_KEY)
    system_message = """
    You are a helpful assistant that generates Git branch names. 
    The branch name should be lowercase, use hyphens instead of spaces, 
    and be no longer than 40 characters (excluding the issue number prefix).
    Do not include any issue numbers in your generated name.
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Generate a concise Git branch name based on this issue:\nTitle: {issue_title}\nDescription: {issue_description}"}
    ]

    try:
        response = client.chat.completions.create(
            model=CHATGPT_MODEL,
            messages=messages,
            max_tokens=50,
            temperature=0.7
        )
        generated_name = response.choices[0].message.content.strip()
        # Remove any numbers from the generated name
        generated_name = re.sub(r'\d+', '', generated_name)
        # Remove any potential "issue-" prefix
        generated_name = re.sub(r'^issue-', '', generated_name)
        # Clean up any double hyphens and leading/trailing hyphens
        generated_name = re.sub(r'-+', '-', generated_name).strip('-')
        return f"{issue_number}-{generated_name}"
    except openai.APIError as e:
        rprint(f"[bold red]An error occurred while generating the branch name: {e}[/bold red]")
        return None

def create_local_branch(branch_name):
    try:
        # Fetch the latest changes from the remote
        subprocess.run(["git", "fetch", "origin"], check=True)
        
        # Create and checkout a new branch
        subprocess.run(["git", "checkout", "-b", branch_name, "origin/main"], check=True)
        
        return f"Local branch '{branch_name}' created and checked out successfully."
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e}")

@app.command()
def create_issue_branch(issue_number: int):
    try:
        # Get issue details
        issue = get_issue_details(issue_number)
        rprint(f"[bold green]Issue details retrieved:[/bold green] {issue['title']}")

        # Generate branch name
        branch_name = generate_branch_name(issue_number, issue['title'], issue['description'])
        if branch_name:
            rprint(f"[bold green]Generated branch name:[/bold green] {branch_name}")

            # Create local branch
            result = create_local_branch(branch_name)
            rprint(f"[bold green]{result}[/bold green]")
        else:
            rprint("[bold red]Failed to generate branch name. Aborting branch creation.[/bold red]")

    except requests.exceptions.HTTPError as e:
        rprint(f"[bold red]HTTP Error occurred:[/bold red] {e}")
    except Exception as e:
        rprint(f"[bold red]An unexpected error occurred:[/bold red] {e}")

if __name__ == "__main__":
    app()