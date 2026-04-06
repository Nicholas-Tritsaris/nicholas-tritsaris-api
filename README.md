# nicholas-tritsaris-api

A Virtual Portfolio API that generates an `openapi.yaml` file in OpenAPI 3.0.3 format from my public GitHub repositories and README files.

This repository is designed for **GitBook URL import** so the spec can render as a polished, interactive developer portal and refresh automatically as projects change.

## What this repo does

- Fetches all public repositories for `Nicholas-Tritsaris` using the GitHub API.
- Fetches each repository's `README.md`.
- Uses the Groq API (`llama3-70b-8192`) to analyze each project and generate:
  - A professional summary.
  - Key features.
  - Tech stack used.
  - Mock "API responses" for each project.
  - Suggested project-specific subpaths.
- Builds a single `openapi.yaml` file compliant with **OpenAPI 3.0.3**.
- Updates the spec automatically with GitHub Actions every 6 hours.

## Generated API structure

The generated OpenAPI spec documents a portfolio as if it were an API.

### Core endpoints

- `GET /profile` — bio, skills, social links (hardcoded in the script).
- `GET /repos` — all public repositories with brief summaries.
- `GET /repos/{name}` — detailed information (summary, tech stack, links) for a specific repo.
- `GET /repos/{name}/*` — (e.g., `/repos/{name}/features`, `/repos/{name}/usage`) AI-generated specific sub-paths for each project based on its README content.

## Repository layout

```text
.
├── .github/
│   └── workflows/
│       └── update-api.yml
├── generate_openapi.py
├── openapi.yaml
├── requirements.txt
├── .gitignore
└── README.md
```

## Required secrets

Add the following repository secrets in: **Settings -> Secrets and variables -> Actions**

### Required

- `GROQ_API_KEY` — your Groq API key.

### Provided automatically in GitHub Actions

- `GITHUB_TOKEN` — GitHub Actions provides this automatically to workflows to fetch repositories and push updates.

## Local usage

To run the generator locally, you'll need to set the environment variables:

```bash
export GROQ_API_KEY="your_key_here"
export GITHUB_TOKEN="your_token_here" # optional for public repos, but recommended for rate limits
python generate_openapi.py
```

This will create or update: `openapi.yaml`

## GitHub Actions automation

The workflow runs every 6 hours using this cron schedule: `0 */6 * * *`. It will check out the repository, install dependencies, run `generate_openapi.py`, and commit and push any updated `openapi.yaml`.

## Connect to GitBook

GitBook supports adding an OpenAPI specification by **URL**, and when the spec is linked to a URL, GitBook checks for updates automatically every 6 hours.

### Steps

1. Push this repository to GitHub.
2. Open `openapi.yaml` in the repository.
3. Click **Raw**.
4. Copy the raw file URL.
5. In GitBook, open the **OpenAPI** section.
6. Click **Add specification**.
7. Give it a name.
8. Choose **URL**.
9. Paste the raw `openapi.yaml` URL.

After that, GitBook will generate the API reference from your spec.

### Example raw URL format

```text
https://raw.githubusercontent.com/Nicholas-Tritsaris/nicholas-tritsaris-api/main/openapi.yaml
```

## Notes

- This repository generates an API specification, not a live backend service.
- The OpenAPI document is intended for documentation and presentation purposes.
- The quality of project summaries and generated subpaths depends on the available README content.
- GitBook can also be refreshed manually with **Check for updates** if you do not want to wait for the next sync cycle.

## License

This project is open-source. Choose the license that fits your portfolio and reuse goals.
