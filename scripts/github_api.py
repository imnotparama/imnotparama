"""
GitHub API Module
=================
Fetches contribution data from GitHub for the profile SVG generation.

Uses two methods:
  1. GitHub Events API (primary) - counts contributions from public events
  2. Contribution graph HTML scraping (fallback) - parses the SVG contribution graph

No authentication required for public profiles.
"""

import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


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
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "pokemon-contrib-svg",
    }

    # Add token if available for higher rate limits
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            events = json.loads(resp.read().decode())

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
        "User-Agent": "Mozilla/5.0 (compatible; pokemon-contrib-svg/1.0)",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")

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


def get_contribution_data(username: str) -> dict:
    """
    Get complete contribution data for a user.

    Tries the Events API first, falls back to scraping.

    Args:
        username: GitHub username

    Returns:
        Dictionary with contribution statistics
    """
    print(f"  Fetching contribution data for '{username}'...")

    # Method 1: Events API
    total, today = fetch_contributions_from_events(username)

    # Method 2: Fallback to graph scraping if Events API returned nothing
    if total == 0:
        print("  Events API returned 0, trying graph scrape fallback...")
        graph_total = fetch_contributions_from_graph(username)
        if graph_total is not None:
            total = graph_total

    # Fetch total public repos count for display
    repos_count = 0
    try:
        url = f"https://api.github.com/users/{username}"
        headers = {"User-Agent": "pokemon-contrib-svg"}
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            headers["Authorization"] = f"token {token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            user_data = json.loads(resp.read().decode())
            repos_count = user_data.get("public_repos", 0)
    except Exception:
        pass

    data = {
        "total_contributions": total,
        "contributions_today": today,
        "repos_count": repos_count,
    }

    print(f"  Total contributions (365d): {total}")
    print(f"  Contributions today: {today}")
    print(f"  Public repos: {repos_count}")

    return data
