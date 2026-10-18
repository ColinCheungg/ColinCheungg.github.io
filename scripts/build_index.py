#!/usr/bin/env python3
"""Build blog/index.json from blog/posts/*.md plus blog/plan.json.

Run locally:  python3 scripts/build_index.py
In CI:        .github/workflows/blog-index.yml runs this on every push that
              touches blog/posts/**, blog/plan.json or this script.

A post is listed (published) when it has BOTH a non-empty ``date`` and some body
content. ``draft: true`` always excludes it. Empty skeleton files stay invisible,
so creating a placeholder file is safe.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "blog" / "posts"
PLAN_FILE = ROOT / "blog" / "plan.json"
OUT_FILE = ROOT / "blog" / "index.json"

FRONT_MATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.S)
KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TRUTHY_RE = re.compile(r"^(true|yes|1)$", re.I)


def is_safe_slug(slug: str) -> bool:
    """True when the filename can be used in a URL without escaping the folder.

    ASCII slugs are recommended (short, readable URLs) but not required — a
    Chinese filename works too, it just shows up percent-encoded in the URL.
    """
    return bool(slug) and "/" not in slug and "\\" not in slug and slug not in {".", ".."}


def parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    """Minimal frontmatter parser mirroring the one in blog/post.html."""
    match = FRONT_MATTER_RE.match(raw)
    if not match:
        return {}, raw

    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        kv = KV_RE.match(line)
        if not kv:
            continue
        value = kv.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[kv.group(1).lower()] = value
    return data, match.group(2)


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text).strip()


def parse_date(text: str) -> datetime | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def display_date(text: str) -> str:
    dt = parse_date(text)
    if dt is None:
        return text
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def read_posts() -> list[dict]:
    if not POSTS_DIR.is_dir():
        return []

    posts: list[dict] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        name = path.name
        if name.startswith("_") or name.startswith("."):
            continue

        slug = path.stem
        if not is_safe_slug(slug):
            print(f"skip {name}: filename must not contain / or \\", file=sys.stderr)
            continue

        data, body = parse_front_matter(path.read_text(encoding="utf-8"))

        if TRUTHY_RE.match(data.get("draft", "")):
            continue
        if not data.get("date"):
            continue
        if not strip_comments(body):
            continue

        posts.append(
            {
                "slug": slug,
                "title": data.get("title") or slug,
                "date": data["date"],
                "display": display_date(data["date"]),
                "summary": data.get("summary", ""),
                "_sort": parse_date(data["date"]),
            }
        )

    # Newest first; undated/invalid dates sink to the bottom.
    posts.sort(key=lambda p: p["slug"])
    posts.sort(key=lambda p: p["_sort"] or datetime.min, reverse=True)

    for post in posts:
        post.pop("_sort", None)
    return posts


def read_post_titles() -> dict[str, str]:
    """Map slug -> title for every post file, published or not.

    Lets the writing plan pick up a renamed title directly from the post's
    frontmatter instead of keeping a second copy in plan.json.
    """
    titles: dict[str, str] = {}
    if not POSTS_DIR.is_dir():
        return titles

    for path in sorted(POSTS_DIR.glob("*.md")):
        name = path.name
        if name.startswith("_") or name.startswith("."):
            continue
        slug = path.stem
        if not is_safe_slug(slug):
            continue
        data, _ = parse_front_matter(path.read_text(encoding="utf-8"))
        if data.get("title"):
            titles[slug] = data["title"]
    return titles


def read_plan(published_slugs: set[str], titles: dict[str, str]) -> dict | None:
    if not PLAN_FILE.is_file():
        return None

    try:
        plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"skip plan.json: {err}", file=sys.stderr)
        return None

    items = []
    for item in plan.get("items", []):
        slug = item.get("slug", "")
        items.append(
            {
                "slug": slug,
                # The post's own frontmatter title wins, so renaming a post in
                # the CMS updates the plan card automatically.
                "title": titles.get(slug) or item.get("title") or slug,
                "done": slug in published_slugs,
            }
        )

    return {
        "title": plan.get("title", ""),
        "description": plan.get("description", ""),
        "items": items,
        "done": sum(1 for item in items if item["done"]),
        "total": len(items),
    }


def main() -> int:
    posts = read_posts()
    plan = read_plan({post["slug"] for post in posts}, read_post_titles())

    payload = {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "plan": plan,
        "posts": posts,
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    plan_note = f"plan {plan['done']}/{plan['total']}" if plan else "plan none"
    print(f"blog/index.json: {len(posts)} published, {plan_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
