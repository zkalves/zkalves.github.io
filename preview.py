#!/usr/bin/env python3
"""
Zero-dependency local preview server for Jekyll portfolio.
Uses Python standard library (no Ruby, Bundler, or Docker required).
"""

import http.server
import socketserver
import os
import re
import datetime

PORT = 4000
SITE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(config_path):
    """Load configuration from _config.yml using PyYAML if available or fallback parser."""
    if not os.path.exists(config_path):
        return {}
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        data = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line and not line.startswith('-'):
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.split('#')[0].strip().strip('"').strip("'")
                    data[k] = v
        return data

def resolve_val(var_str, ctx):
    var_str = var_str.strip()
    if (var_str.startswith('"') and var_str.endswith('"')) or (var_str.startswith("'") and var_str.endswith("'")):
        return var_str[1:-1]
    if var_str == 'now':
        return 'now'
    parts = var_str.split('.')
    curr = ctx
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return ''
    return str(curr) if curr is not None else ''

def eval_liquid_expr(expr, ctx):
    pipe_parts = [p.strip() for p in expr.split('|')]
    base = pipe_parts[0]
    val = resolve_val(base, ctx)

    for filter_part in pipe_parts[1:]:
        if ':' in filter_part:
            fname, farg = filter_part.split(':', 1)
            fname, farg = fname.strip(), farg.strip()
        else:
            fname, farg = filter_part.strip(), ''

        if fname == 'default':
            if not val or val == '':
                val = resolve_val(farg, ctx)
        elif fname == 'relative_url':
            if val in ('/', './', ''):
                val = './'
            else:
                val = val.lstrip('/')
        elif fname == 'date':
            val = str(datetime.datetime.now().year)

    return val

def load_data_repos():
    """Load repositories from _data/repositories.yml if present."""
    data_file = os.path.join(SITE_DIR, '_data', 'repositories.yml')
    if not os.path.exists(data_file):
        return []
    try:
        import yaml
        with open(data_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or []
    except Exception:
        return []

def build_html():
    config_path = os.path.join(SITE_DIR, '_config.yml')
    layout_path = os.path.join(SITE_DIR, '_layouts', 'default.html')
    index_path = os.path.join(SITE_DIR, 'index.html')

    config = load_config(config_path)

    with open(layout_path, 'r', encoding='utf-8') as f:
        layout = f.read()

    with open(index_path, 'r', encoding='utf-8') as f:
        index_raw = f.read()

    # Strip Jekyll YAML Front Matter
    parts = re.split(r'^---\s*$', index_raw, flags=re.MULTILINE)
    body = parts[2] if len(parts) >= 3 else index_raw

    # Render template body into layout
    html = layout.replace('{{ content }}', body)

    username = config.get('github_username', 'zkalves')
    repos = load_data_repos()

    if repos:
        cards_html = []
        for r in repos:
            name = r.get('name', '')
            url = r.get('html_url', f"https://github.com/{username}/{name}")
            desc = r.get('description', 'No description provided.')
            lang = r.get('language', 'Other')
            stars = r.get('stargazers_count', 0)
            cards_html.append(f'''
        <article class="repo-card" data-repo="{name}">
          <div class="repo-card-top">
            <h3 class="repo-title">
              <a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>
            </h3>
            <span class="repo-stars" title="{stars} stars">
              <span class="star-icon">&#9733;</span> {stars}
            </span>
          </div>
          <p class="repo-desc">{desc}</p>
          <div class="repo-card-bottom">
            <span class="repo-lang">
              <span class="lang-dot" data-lang="{lang}"></span>
              {lang}
            </span>
            <a href="{url}" class="repo-link" target="_blank" rel="noopener noreferrer" aria-label="Visit {name} repository">
              View Repository &rarr;
            </a>
          </div>
        </article>''')

        grid_html = f'''  <div class="repo-grid" id="repo-grid" data-username="{username}">
{''.join(cards_html)}
  </div>'''
    else:
        grid_html = f'''  <div class="repo-grid" id="repo-grid" data-username="{username}">
    <div class="repo-state repo-loading" id="repo-loading">
      <div class="spinner" aria-hidden="true"></div>
      <p>Retrieving repositories from GitHub...</p>
    </div>
  </div>'''

    html = re.sub(
        r'<div class="repo-grid"[^>]*>.*?</div>\s*</section>',
        grid_html + '\n</section>',
        html,
        flags=re.DOTALL
    )

    ctx = {
        'site': config,
        'page': {
            'title': config.get('title', 'Portfolio'),
            'description': config.get('description', '')
        }
    }

    # Clean out Jekyll plugin tags
    html = re.sub(r'\{%\s*(seo|feed_meta)\s*%\}', '', html)

    # Process conditional blocks like {% if site.var %}...{% endif %}
    def handle_if_block(match):
        cond = match.group(1).strip()
        inner = match.group(2)
        val = resolve_val(cond, ctx)
        return inner if val else ''

    html = re.sub(r'\{%\s*if\s+([a-zA-Z0-9_\.]+)\s*%\}(.*?)\{%\s*endif\s*%\}', handle_if_block, html, flags=re.DOTALL)

    # Evaluate all Liquid expressions: {{ var | filter: arg }}
    html = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: eval_liquid_expr(m.group(1), ctx), html)

    # Remove any remaining Liquid control tags
    html = re.sub(r'\{%.*?%\}', '', html)

    # Clean up page title tag
    html = re.sub(r'<title>.*?</title>', f"<title>{config.get('title', 'Portfolio')}</title>", html, count=1)

    return html

class PortfolioHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent browser caching during local development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        req_path = self.path.split('?')[0]
        if req_path in ('/', '/index.html'):
            try:
                content = build_html().encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Build error: {e}'.encode('utf-8'))
                return

        return super().do_GET()

def main():
    os.chdir(SITE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioHandler) as httpd:
        print("=======================================================")
        print(f" Portfolio Preview Server running at:")
        print(f"   http://localhost:{PORT}")
        print(" Press Ctrl+C to stop.")
        print("=======================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down preview server.")

if __name__ == '__main__':
    main()
