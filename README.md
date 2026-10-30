# Minimal Jekyll Portfolio (Hacker Theme)

A fast, lightweight, and clean portfolio site built for GitHub Pages (`<username>.github.io`). It features the iconic **Hacker** Jekyll terminal theme (dark `#212121` background, `#b5e853` phosphor green accents, and monospace typography) with a dual-approach GitHub repository showcase.

## Project Structure

```text
.
├── _config.yml               # Jekyll configuration, Hacker theme & GitHub Pages plugin settings
├── _layouts/
│   └── default.html          # Semantic HTML5 layout styled with Hacker theme aesthetics
├── assets/
│   └── css/
│       └── style.css         # Zero-dependency, responsive CSS matching Hacker terminal palette
├── index.html                # Landing page & dual repository showcase
├── Gemfile                   # Ruby gem dependencies for GitHub Pages
└── README.md                 # Setup, local development, and deployment docs
```

---

## Repository Showcase Implementation

This project provides two complementary approaches to display public projects (automatically excluding forks as well as this portfolio repository itself):

### Approach A: Build-Time Static Rendering via Liquid
* **Mechanism**: Uses `site.github.public_repositories` (provided by the `jekyll-github-metadata` plugin).
* **Filtering & Sorting**: Excludes forks and `<username>.github.io`, sorting repositories by star count and activity.
* **Benefits**: Zero client-side JavaScript required for initial page paint; fast, SEO-friendly, fully static HTML generated at build time when deployed on GitHub Pages.

### Approach B: Client-Side Fallback via Vanilla JavaScript
* **Mechanism**: A lightweight script embedded in `index.html` queries the GitHub REST API (`https://api.github.com/users/<username>/repos?per_page=100&sort=updated`).
* **Filtering**: Excludes forks and `<username>.github.io`.
* **Rate-Limit Resilience**: Caches results in browser `localStorage` (`gh_repos_v2_<username>`) with a 1-hour expiration time (TTL) to adhere to GitHub's unauthenticated API rate limit (60 requests/hour).
* **Fallback & Recovery**: If an API call fails or encounters a rate limit (HTTP 403), the script gracefully falls back to stale cache data if available before showing a direct profile link.
* **Why both?**: When testing locally without setting an authenticated `JEKYLL_GITHUB_TOKEN`, Jekyll's `site.github.public_repositories` is empty. The client-side fallback automatically takes over during local development or offline states, ensuring cards always render seamlessly.

---

### Quickstart with Make

Run `make` or `make help` to see all available commands:

```bash
make preview         # Start zero-dependency Python preview server (http://localhost:4000)
make check           # Validate YAML and template configuration
make jekyll-install  # Install Ruby gems to vendor/bundle
make jekyll-serve    # Start native Jekyll server with live reload
make docker-serve    # Start preview in official Jekyll Docker container
make clean           # Remove build caches and artifacts
```

---

## Local Development & Preview

### Option 1: Zero-Dependency Python Server (Recommended & Immediate)

Because you already have Python 3 installed, you can preview the site immediately with **zero installs, zero permissions, and no Ruby or Docker**:

```bash
make preview
# or: python3 preview.py
```

Open `http://localhost:4000` in your browser. The preview server compiles the Jekyll templates dynamically and loads your GitHub repositories via the client API fallback.

### Option 2: Native Jekyll via Bundler

Ensure Ruby (>= 3.0) and Bundler are installed on your system:

```bash
# Configure Bundler to install gems locally into the project (prevents system permission errors)
bundle config set --local path 'vendor/bundle'

# Install dependencies
bundle install

# Run the local development server with live reload
bundle exec jekyll serve --livereload
```

Open your browser at `http://localhost:4000`.

> **Note on Static Metadata locally**: To test Approach A locally with live repository data at build time, export a GitHub personal access token before running Jekyll:
> ```bash
> export JEKYLL_GITHUB_TOKEN="ghp_yourPersonalAccessTokenHere"
> bundle exec jekyll serve
> ```
> Without this token, Approach B (vanilla JS fallback) activates automatically.

### Option 3: Docker Container (No Ruby Setup Required)

If you have Docker installed, you can preview the site with a single command:

```bash
docker run --rm \
  -v "$PWD:/srv/jekyll" \
  -p 4000:4000 \
  -it jekyll/jekyll:pages \
  jekyll serve --watch --force_polling
```

Navigate to `http://localhost:4000` to view the site.

---

## Configuration & Customization

All personal metadata is configured in `_config.yml`:

```yaml
title: "Your Name | Projects & Portfolio"
author: "Your Name"
github_username: "your-github-username"
description: "Brief summary of your work and focus areas."
url: "https://your-github-username.github.io"
baseurl: ""
```

### Color Palette & Theming
Theme variables are defined at the top of `assets/css/style.css` matching the official **Hacker** Jekyll theme:
* **Background**: Classic deep charcoal `#212121` with `#151515` header and panel surfaces.
* **Text**: Crisp `#eaeaea` terminal foreground.
* **Accents**: Signature phosphor green `#b5e853` with glow effects for headings, prompts, links, and borders.
* **Typography**: Pure monospace stack (`Monaco, "Bitstream Vera Sans Mono", "Lucida Console", Terminal, monospace`).

---

## GitHub Pages Deployment

The repository includes a GitHub Actions CI/CD workflow ([.github/workflows/deploy.yml](file:///.github/workflows/deploy.yml)) that automatically tests builds on PRs and builds/deploys the portfolio to GitHub Pages on every push to `main`.

1. **Verify GitHub Pages Source**:
   - Go to your repository on GitHub: `https://github.com/<username>/<username>.github.io`
   - Navigate to **Settings** &rarr; **Pages**
   - Under **Build and deployment**:
     - **Source**: Select **GitHub Actions**

2. **Commit and Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initialize minimal Jekyll portfolio with GitHub Actions CI"
   git push origin main
   ```

3. **Visit Your Site**:
   The workflow will trigger immediately in the **Actions** tab. Once completed, your portfolio is live at:
   `https://<username>.github.io`
