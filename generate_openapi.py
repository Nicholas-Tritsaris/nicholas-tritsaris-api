import os
import requests
import yaml
from groq import Groq
import json

# Configuration
GITHUB_USERNAME = "Nicholas-Tritsaris"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
MODEL = "llama3-70b-8192"

# Profile Data
PROFILE = {
    "name": "Nicholas Tritsaris",
    "bio": "Expert Backend Developer and Documentation Specialist with a focus on building robust APIs and comprehensive technical documentation. Passionate about automating workflows and creating seamless developer experiences.",
    "skills": ["Python", "OpenAPI/Swagger", "Backend Development", "GitHub Actions", "CI/CD", "Technical Writing", "API Design"],
    "socials": [
        {"platform": "Email", "url": "mailto:nicholas.tritsaris13@bk.ru"},
        {"platform": "Website", "url": "https://blueboop.is-a.dev/"},
        {"platform": "TikTok", "url": "https://www.tiktok.com/@sourgtus4c4"},
        {"platform": "Handle", "url": "@blueboop.is-a.dev"}
    ]
}

client = Groq(api_key=GROQ_API_KEY)

def fetch_repos():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_readme(repo_name):
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/readme"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        download_url = response.json().get("download_url")
        readme_content = requests.get(download_url).text
        return readme_content
    return "No README available."

def analyze_repo(repo_name, readme_content):
    prompt = f"""
    Analyze the following README content for a GitHub repository named '{repo_name}'.

    README Content:
    {readme_content[:4000]}

    Generate a JSON object with the following fields:
    - summary: A professional one-sentence summary of the project.
    - features: A list of 3-5 key features.
    - tech_stack: A list of technologies used.
    - mock_response: A sample JSON response that this project's API might return (be creative and specific to the project).
    - sub_paths: A list of 1-2 additional sub-paths (e.g., "features", "usage", "stats") that would be relevant for this project, including a brief description and a mock response for each.

    Example format:
    {{
      "summary": "...",
      "features": ["...", "..."],
      "tech_stack": ["...", "..."],
      "mock_response": {{ "key": "value" }},
      "sub_paths": [
        {{ "path": "features", "description": "Returns a detailed list of features", "mock_response": {{ ... }} }}
      ]
    }}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes code repositories and outputs valid JSON."},
            {"role": "user", "content": prompt}
        ],
        model=MODEL,
        response_format={"type": "json_object"}
    )

    return json.loads(chat_completion.choices[0].message.content)

def generate_openapi():
    repos = fetch_repos()

    paths = {
        "/profile": {
            "get": {
                "summary": "Get profile information",
                "responses": {
                    "200": {
                        "description": "Profile information",
                        "content": {
                            "application/json": {
                                "example": PROFILE
                            }
                        }
                    }
                }
            }
        },
        "/repos": {
            "get": {
                "summary": "List all public repositories",
                "responses": {
                    "200": {
                        "description": "A list of repositories",
                        "content": {
                            "application/json": {
                                "example": []
                            }
                        }
                    }
                }
            }
        }
    }

    repo_list_example = []

    for repo in repos:
        if repo["fork"]: continue

        name = repo["name"]
        print(f"Processing {name}...")
        readme = fetch_readme(name)
        analysis = analyze_repo(name, readme)

        repo_list_example.append({
            "name": name,
            "summary": analysis.get("summary", ""),
            "url": repo["html_url"]
        })

        # Detail path
        paths[f"/repos/{name}"] = {
            "get": {
                "summary": f"Get details for {name}",
                "responses": {
                    "200": {
                        "description": f"Details for {name}",
                        "content": {
                            "application/json": {
                                "example": {
                                    "name": name,
                                    "summary": analysis.get("summary", ""),
                                    "features": analysis.get("features", []),
                                    "tech_stack": analysis.get("tech_stack", []),
                                    "github_url": repo["html_url"],
                                    "mock_api_response": analysis.get("mock_response", {})
                                }
                            }
                        }
                    }
                }
            }
        }

        # Sub-paths
        for sp in analysis.get("sub_paths", []):
            sub_path = sp.get("path", "").strip("/")
            if not sub_path: continue

            paths[f"/repos/{name}/{sub_path}"] = {
                "get": {
                    "summary": sp.get("description", f"{sub_path.capitalize()} for {name}"),
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "example": sp.get("mock_response", {})
                                }
                            }
                        }
                    }
                }
            }

    paths["/repos"]["get"]["responses"]["200"]["content"]["application/json"]["example"] = repo_list_example

    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Nicholas Tritsaris Virtual Portfolio API",
            "description": "A virtual API representing the portfolio and projects of Nicholas Tritsaris. Designed for GitBook integration.",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://api.nicholas-tritsaris.com", "description": "Virtual server for documentation purposes"}
        ],
        "paths": paths
    }

    with open("openapi.yaml", "w") as f:
        yaml.dump(openapi_spec, f, sort_keys=False)

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in environment.")
    else:
        try:
            generate_openapi()
            print("openapi.yaml generated successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")
