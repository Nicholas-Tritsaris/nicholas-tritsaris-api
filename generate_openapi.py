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
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?type=public&sort=updated"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_readme(repo_name):
    headers = {"Accept": "application/vnd.github.v3+json"}
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
                "tags": ["Profile"],
                "summary": "Get profile information",
                "description": "Returns my bio, skills, and social links.",
                "operationId": "getProfile",
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Profile"}
                            }
                        }
                    }
                }
            }
        },
        "/repos": {
            "get": {
                "tags": ["Repositories"],
                "summary": "List all public repositories",
                "description": "Returns a list of all public GitHub projects with brief summaries.",
                "operationId": "getRepos",
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Repository"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    repo_list_example = []

    for repo in repos:
        if repo.get("fork"): continue

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
                "tags": ["Repositories"],
                "summary": f"Get details for {name}",
                "description": f"Returns detailed information (summary, tech stack, links) for the '{name}' repository.",
                "operationId": f"getRepo_{name.replace('-', '_')}",
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RepositoryDetail"},
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

            operation_id = f"getRepo{name.replace('-', '_').capitalize()}{sub_path.capitalize()}"
            paths[f"/repos/{name}/{sub_path}"] = {
                "get": {
                    "tags": [name],
                    "summary": sp.get("description", f"{sub_path.capitalize()} for {name}"),
                    "description": f"AI-generated sub-path exploring the '{sub_path}' of project '{name}'.",
                    "operationId": operation_id,
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                    "example": sp.get("mock_response", {})
                                }
                            }
                        }
                    }
                }
            }

    # Inject the actual example into /repos
    paths["/repos"]["get"]["responses"]["200"]["content"]["application/json"]["example"] = repo_list_example

    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Nicholas Tritsaris Virtual Portfolio API",
            "description": "A virtual API representing the portfolio and projects of Nicholas Tritsaris. This is a documentation-only API for presentation in GitBook.",
            "version": "1.0.0",
            "contact": {
                "name": "Nicholas Tritsaris",
                "url": "https://blueboop.is-a.dev/",
                "email": "nicholas.tritsaris13@bk.ru"
            }
        },
        "servers": [
            {"url": "https://api.nicholas-tritsaris.com", "description": "Virtual server for documentation purposes"}
        ],
        "tags": [
            {"name": "Profile", "description": "Personal bio and contact info"},
            {"name": "Repositories", "description": "Public projects and codebases"}
        ],
        "paths": paths,
        "components": {
            "schemas": {
                "Profile": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "bio": {"type": "string"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "socials": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "platform": {"type": "string"},
                                    "url": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "Repository": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "summary": {"type": "string"},
                        "url": {"type": "string"}
                    }
                },
                "RepositoryDetail": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "summary": {"type": "string"},
                        "features": {"type": "array", "items": {"type": "string"}},
                        "tech_stack": {"type": "array", "items": {"type": "string"}},
                        "github_url": {"type": "string"},
                        "mock_api_response": {"type": "object"}
                    }
                }
            }
        }
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
            import traceback
            traceback.print_exc()
