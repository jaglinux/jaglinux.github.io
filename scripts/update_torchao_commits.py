#!/usr/bin/env python3
"""Fetch all TorchAO commits authored by Jagadish and regenerate torchao-commits.html."""

import html
import json
import os
import re
import time
from datetime import date
from urllib.error import HTTPError
from urllib.request import Request, urlopen

AUTHOR_EMAILS = [
    "jagadish.krishnamoorthy@amd.com",
    "jagdish.krishna@gmail.com",
]

# Co-authored PRs that cannot be found via author-email search.
COAUTHORED_PRS = {}

GH_TOKEN = os.environ.get("GH_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GH_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def gh_get(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f"HTTP {e.code} for {url}: {e.read().decode()}")
        raise


def search_commits_by_email(email):
    commits = []
    page = 1
    while True:
        url = (
            "https://api.github.com/search/commits"
            f"?q=repo:pytorch/ao+author-email:{email}"
            f"&per_page=100&page={page}"
        )
        data = gh_get(url)
        items = data.get("items", [])
        commits.extend(items)
        print(f"  page {page}: {len(items)} results (total so far: {len(commits)})")
        if len(items) < 100:
            break
        page += 1
        time.sleep(2)  # stay within 30 req/min search rate limit
    return commits


def extract_pr(message):
    m = re.search(r'\(#(\d+)\)\s*$', message.split('\n')[0].strip())
    return int(m.group(1)) if m else None


def clean_title(message):
    first_line = message.split('\n')[0].strip()
    return re.sub(r'\s*\(#\d+\)\s*$', '', first_line)


def build_html(sorted_prs, today):
    total = len(sorted_prs)
    author_count = sum(1 for _, (_, role) in sorted_prs if role == "Author")
    coauthor_count = total - author_count

    rows = []
    for i, (pr, (title, role)) in enumerate(sorted_prs, 1):
        safe_title = html.escape(title)
        rows.append(
            f'                <tr>'
            f'<td style="padding:5px 10px;border:1px solid #ddd;">{i}</td>'
            f'<td style="padding:5px 10px;border:1px solid #ddd;white-space:nowrap;">'
            f'<a href="https://github.com/pytorch/ao/pull/{pr}">#{pr}</a></td>'
            f'<td style="padding:5px 10px;border:1px solid #ddd;">{safe_title}</td>'
            f'<td style="padding:5px 10px;border:1px solid #ddd;">{role}</td>'
            f'</tr>'
        )

    return f"""<!DOCTYPE HTML>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>TorchAO GitHub Commits – Jagadish Krishnamoorthy</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="../stylesheet.css">
  </head>

  <body>
    <table style="width:100%;max-width:800px;border:0px;border-spacing:0px;border-collapse:separate;margin-right:auto;margin-left:auto;">
      <tbody>
        <tr>
          <td style="padding:20px;vertical-align:top;">
            <h2>TorchAO GitHub commits</h2>

            <h3>Author information</h3>
            <p>
              <strong>Name:</strong> Jagadish Krishnamoorthy<br>
              <strong>Emails:</strong><br>
              &ensp;- <a href="mailto:jagadish.krishnamoorthy@amd.com">jagadish.krishnamoorthy@amd.com</a> (recent)<br>
              &ensp;- <a href="mailto:jagdish.krishna@gmail.com">jagdish.krishna@gmail.com</a> (older)<br>
              <strong>Commits till:</strong> {today}
            </p>

            <h3>Commit history</h3>
            <p>Total: {total} commits ({author_count} as primary author, {coauthor_count} co-authored)</p>
            <table style="width:100%;border-collapse:collapse;font-size:0.9em;">
              <thead>
                <tr style="background:#f2f2f2;">
                  <th style="padding:6px 10px;text-align:left;border:1px solid #ddd;">#</th>
                  <th style="padding:6px 10px;text-align:left;border:1px solid #ddd;">PR</th>
                  <th style="padding:6px 10px;text-align:left;border:1px solid #ddd;">Title</th>
                  <th style="padding:6px 10px;text-align:left;border:1px solid #ddd;">Role</th>
                </tr>
              </thead>
              <tbody>
{chr(10).join(rows)}
              </tbody>
            </table>

            <p>
              <a href="../index.html">Back to home</a>
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>"""


def main():
    pr_map = {}

    for email in AUTHOR_EMAILS:
        print(f"Fetching commits for {email} ...")
        commits = search_commits_by_email(email)
        print(f"  Total: {len(commits)}")
        for item in commits:
            msg = item["commit"]["message"]
            pr = extract_pr(msg)
            if pr and pr not in pr_map:
                pr_map[pr] = (clean_title(msg), "Author")
        time.sleep(1)

    for pr, title in COAUTHORED_PRS.items():
        if pr not in pr_map:
            pr_map[pr] = (title, "Co-author")

    sorted_prs = sorted(pr_map.items(), key=lambda x: x[0], reverse=True)

    today = date.today().strftime("%m/%d/%Y")
    content = build_html(sorted_prs, today)

    out = os.path.join(os.path.dirname(__file__), "..", "data", "torchao-commits.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {os.path.normpath(out)} — {len(sorted_prs)} commits total.")


if __name__ == "__main__":
    main()
