# nicholas-tritsaris-api

A Virtual Portfolio API that generates an `openapi.yaml` file in OpenAPI 3.0.3 format from my public GitHub repositories and README files.

This repository is designed for **GitBook URL import** so the spec can render as a polished, interactive developer portal and refresh automatically as projects change.

## What this repo does

- Fetches all public repositories for `Nicholas-Tritsaris` using the GitHub API
- Fetches each repository's `README.md`
- Uses the Groq API to analyze each project and generate:
  - A professional summary
  - Key features
  - Tech stack
  - Mock API-style responses
  - Suggested project-specific subpaths
- Builds a single `openapi.yaml` file compliant with **OpenAPI 3.0.3**
- Updates the spec automatically with GitHub Actions every 6 hours

## Generated API structure

The generated OpenAPI spec documents a portfolio as if it were an API.

### Core endpoints

- `GET /profile` — bio, skills, social links
- `GET /repos` — all public repositories with summaries
- `GET /repos/{name}` — detailed information for one repository
- `GET /repos/{name}/*` — AI-generated subpaths such as features, usage, architecture, setup, or showcase routes based on README content

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

Add the following repository secrets in:

**Settings -> Secrets and variables -> Actions**

### Required

- `GROQ_API_KEY` — your Groq API key

### Provided automatically in GitHub Actions

- `GITHUB_TOKEN` — GitHub Actions provides this automatically to workflows, and it can be explicitly passed into the job environment when needed

## Local usage

Run the generator locally:

```bash
python generate_openapi.py
```

This will create or update:

```text
openapi.yaml
```

## GitHub Actions automation

The workflow runs every 6 hours using this cron schedule:

```yaml
0 */6 * * *
```

It will:

- Check out the repository
- Install dependencies
- Run `generate_openapi.py`
- Commit and push any updated `openapi.yaml`

## Connect to GitBook

GitBook supports adding an OpenAPI specification by **URL**, and when the spec is linked to a URL, GitBook checks for updates automatically every 6 hours.

### Steps

1. Push this repository to GitHub
2. Open `openapi.yaml` in the repository
3. Click **Raw**
4. Copy the raw file URL
5. In GitBook, open the **OpenAPI** section
6. Click **Add specification**
7. Give it a name
8. Choose **URL**
9. Paste the raw `openapi.yaml` URL

After that, GitBook will generate the API reference from your spec.

## Example raw URL format

```text
https://raw.githubusercontent.com/Nicholas-Tritsaris/nicholas-tritsaris-api/main/openapi.yaml
```

## Notes

- This repository generates an API specification, not a live backend service
- The OpenAPI document is intended for documentation and presentation
- The quality of project summaries and generated subpaths depends on the available README content
- GitBook can also be refreshed manually with **Check for updates** if you do not want to wait for the next sync cycle

## Next steps

- Create the repository on GitHub
- Add the `GROQ_API_KEY` secret
- Commit the generated files
- Push to `main`
- Connect the raw `openapi.yaml` URL to GitBook

## Why this approach works

GitBook supports OpenAPI specs from a hosted URL, and URL-linked specs are automatically checked for updates every 6 hours, which matches the scheduled GitHub Actions sync model for this repository.

## License

Choose the license that fits your portfolio and reuse goals.
