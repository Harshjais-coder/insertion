import os
import sys
from google import genai
from github import Github, Auth

def main():
    
    api_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO")
    pr_number = os.getenv("PR_NUMBER")

    if not all([api_key, github_token, repo_name, pr_number]):
        print("Error: Missing required environment variables.")
        sys.exit(1)

    
    client = genai.Client(api_key=api_key)
    
    model_id = "gemini-2.5-flash" 


    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))

    
    changed_files = pr.get_files()
    diff_sections = []

    for f in changed_files:
        if f.patch:
            diff_sections.append(f"### File: {f.filename}\n```diff\n{f.patch}\n```")

    if not diff_sections:
        print("No text changes found, skipping review.")
        return

    full_diff = "\n\n".join(diff_sections)

    
    prompt = f"Review this PR diff and provide a summary, bugs, and suggestions:\n\n{full_diff}"

    
    try:
        print(f"Generating review for PR #{pr_number} using {model_id}...")
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        review_comment = response.text

        
        pr.create_issue_comment(f"## 🤖 Gemini Code Review\n\n{review_comment}")
        print("Review comment posted successfully.")

    except Exception as e:
        
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
