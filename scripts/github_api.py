"""
GitHub API Module
=================
Fetches contribution data from GitHub for the profile SVG generation.

Uses three methods, most-accurate first:
  1. GraphQL contributionsCollection API - the exact calendar GitHub itself
     uses for streak stats and contribution graphs (requires GITHUB_TOKEN)
  2. GitHub Events API - counts recent public events (300-event cap, approximate)
  3. Contribution graph HTML scraping - last-resort fallback

Works without authentication for public profiles, but a GITHUB_TOKEN
unlocks the accurate GraphQL path and higher rate limits.
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

USER_AGENT = "pokemon-contrib-svg/2.0"


def _request(url: str, headers: dict, timeout: int = 15):
    """Perform a GET request, returning the raw body, or raising."""
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _base_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# ---------------------------------------------------------------------------
# Method 1: GraphQL contributionsCollection (exact, token recommended)
# ---------------------------------------------------------------------------

_GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
    repositories(privacy: PUBLIC) { totalCount }
  }
}
"""


def fetch_contributions_graphql(username: str) -> Optional[dict]:
    """
    Fetch exact contribution data via the GraphQL API.

    Returns dict with total_contributions, contributions_today, repos_count,
    or None if the API is unavailable (no token, rate limited, error).
    """
    if not os.environ.get("GITHUB_TOKEN", ""):
        return None

    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": _GRAPHQL_QUERY, "variables": {"login": username}}).encode()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    try:
        req = urllib.request.Request("https://api.github.com/graphql", data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode())

        if payload.get("errors"):
            print(f"  [WARN] GraphQL errors: {payload['errors'][0].get('message', 'unknown')}")
            return None

        user = payload.get("data", {}).get("user")
        if not user:
            return None

        calendar = user["contributionsCollection"]["contributionCalendar"]
        total = calendar.get("totalContributions", 0)

        # "Today" = the last day entry in the calendar with a real count.
        # The calendar spans ~1 year ending this week, so scan from the end.
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today = 0
        for week in reversed(calendar.get("weeks", [])):
            for day in reversed(week.get("contributionDays", [])):
                if day.get("date", "").startswith(today_str):
                    today = day.get("contributionCount", 0)
                    break
            if today or week.get("contributionDays") and week["contributionDays"][-1].get("date", "") < today_str:
                break

        repos_count = user.get("repositories", {}).get("totalCount", 0)

        return {
            "total_contributions": total,
            "contributions_today": today,
            "repos_count": repos_count,
            "source": "graphql",
        }

    except urllib.error.HTTPError as e:
        print(f"  [WARN] GraphQL API error {e.code} - falling back")
    except Exception as e:
        print(f"  [WARN] GraphQL request failed: {e} - falling back")

    return None


# ---------------------------------------------------------------------------
# Method 2: Events API (approximate, capped at 300 recent events)
# ---------------------------------------------------------------------------

def fetch_contributions_from_events(username: str) -> Tuple[int, int]:
    """
    Fetch contribution counts from GitHub's public Events API.

    The Events API returns up to 300 most recent public events.
    We count PushEvents as contributions.

    Args:
        username: GitHub username

    Returns:
        Tuple of (total_contributions_365d, contributions_today)
    """
    total = 0
    today_count = 0
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).replace(tzinfo=None)

    url = f"https://api.github.com/users/{username}/events/public?per_page=100"
    headers = _base_headers()

    try:
        body = _request(url, headers)
        events = json.loads(body.decode())

        for event in events:
            # Count push events (commits) as contributions
            if event.get("type") == "PushEvent":
                created_at = event.get("created_at", "")
                if not created_at:
                    continue

                event_date = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                ).replace(tzinfo=None)

                if event_date >= cutoff:
                    total += len(event.get("payload", {}).get("commits", []))

                if created_at.startswith(today_str):
                    today_count += len(event.get("payload", {}).get("commits", []))

            # Count other contribution types
            elif event.get("type") in ("CreateEvent", "IssuesEvent", "PullRequestEvent", "PullRequestReviewEvent"):
                created_at = event.get("created_at", "")
                if not created_at:
                    continue

                event_date = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                ).replace(tzinfo=None)

                if event_date >= cutoff:
                    total += 1

                if created_at.startswith(today_str):
                    today_count += 1

    except urllib.error.HTTPError as e:
        print(f"  [WARN] GitHub API error for {username}: {e.code}")
    except Exception as e:
        print(f"  [WARN] Failed to fetch events for {username}: {e}")

    return total, today_count


# ---------------------------------------------------------------------------
# Method 3: Contribution graph HTML scraping (last resort)
# ---------------------------------------------------------------------------

def fetch_contributions_from_graph(username: str) -> Optional[int]:
    """
    Fallback: Parse the contribution graph page HTML to extract daily counts.

    This scrapes the contribution calendar from the GitHub profile page.

    Args:
        username: GitHub username

    Returns:
        Total contributions in the last year, or None on failure
    """
    url = f"https://github.com/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; pokemon-contrib-svg/2.0)",
    }

    try:
        body = _request(url, headers)
        html = body.decode("utf-8")

        # Parse contribution counts from the contribution graph
        # Pattern: data-date="YYYY-MM-DD" data-count="N"
        pattern = r'data-date="(\d{4}-\d{2}-\d{2})"\s+data-count="(\d+)"'
        matches = re.findall(pattern, html)

        if not matches:
            # Try alternative pattern used by GitHub
            pattern = r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-count="(\d+)"'
            matches = re.findall(pattern, html)

        if matches:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).replace(tzinfo=None)
            total = 0
            for date_str, count in matches:
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    if date >= cutoff:
                        total += int(count)
                except ValueError:
                    continue
            return total

        # Try yet another pattern (level-based contribution graph)
        pattern = r'(\d+) contributions? on (\w+ \d+, \d{4})'
        matches = re.findall(pattern, html)
        if matches:
            return sum(int(m[0]) for m in matches)

    except urllib.error.HTTPError as e:
        print(f"  [WARN] Failed to scrape contribution graph: {e.code}")
    except Exception as e:
        print(f"  [WARN] Failed to scrape contribution graph: {e}")

    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def get_contribution_data(username: str) -> dict:
    """
    Get complete contribution data for a user.

    Tries GraphQL first (exact), then Events API, then scraping.

    Args:
        username: GitHub username

    Returns:
        Dictionary with contribution statistics
    """
    print(f"  Fetching contribution data for '{username}'...")

    # Method 1: GraphQL (exact - same numbers as the GitHub profile page)
    result = fetch_contributions_graphql(username)
    if result:
        print(f"  Source: GraphQL contributionsCollection (exact)")
        print(f"  Total contributions (365d): {result['total_contributions']}")
        print(f"  Contributions today: {result['contributions_today']}")
        print(f"  Public repos: {result['repos_count']}")
        return result

    # Method 2: Events API
    total, today = fetch_contributions_from_events(username)

    # Method 3: Fallback to graph scraping if Events API returned nothing
    if total == 0:
        print("  Events API returned 0, trying graph scrape fallback...")
        graph_total = fetch_contributions_from_graph(username)
        if graph_total is not None:
            total = graph_total

    # Fetch total public repos count for display
    repos_count = 0
    try:
        headers = _base_headers()
        body = _request(f"https://api.github.com/users/{username}", headers, timeout=10)
        repos_count = json.loads(body.decode()).get("public_repos", 0)
    except Exception:
        pass

    data = {
        "total_contributions": total,
        "contributions_today": today,
        "repos_count": repos_count,
        "source": "events/scrape",
    }

    print(f"  Source: Events API / scrape (approximate)")
    print(f"  Total contributions (365d): {total}")
    print(f"  Contributions today: {today}")
    print(f"  Public repos: {repos_count}")

    return data
