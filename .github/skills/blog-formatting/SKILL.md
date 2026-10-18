---
name: blog-formatting
description: "Format and clean up a blog post markdown file before publishing. Use when the user wants to 排版、格式化、整理、polish a blog post, or says things like '帮我排版博客', 'format my blog post', '发布前排版', or passes a rough draft. Normalizes headings, spacing, lists, code blocks, inline formatting, and frontmatter in blog/posts/*.md without changing meaning or code."
argument-hint: "Post file or slug to format, e.g. my-new-post"
user-invocable: true
---

# Blog Post Formatting

Formats a draft blog post in `blog/posts/<slug>.md` into clean, consistently
styled Markdown that matches this site's rendering (client-side `marked.js`).
Formatting only — never rewrites the author's ideas, wording, code, or URLs.

## When to Use

- User finished writing a post and wants it "排版" / formatted before publishing.
- User invokes this skill as a slash command or in natural language
  (e.g. "format my blog post", "帮我排版这篇文章").

## Site Conventions (must preserve)

- Post file is `blog/posts/<slug>.md`; slug matches `^[a-zA-Z0-9_-]+$`.
- Frontmatter uses `title:` and `date:` (date format `Month Day, Year`,
  e.g. `August 15, 2026`).
- `blog/post.html` renders the title from frontmatter, so the body must
  **not** contain a top-level `#` heading.
- Content is English on this site. Keep the post in its original language;
  do not translate.

## Formatting Rules

### Frontmatter
- Must start the file with a valid block and exactly these keys (both required):
  ```markdown
  ---
  title: <Title>
  date: <Month Day, Year>
  ---
  ```
- If `date` is missing, insert the current date in `Month Day, Year` format.
- If `title` is missing, derive it from the first line of the draft.

### Headings
- Use `##` for sections, `###` for subsections, `####` for deeper levels.
- No `#` (H1) in the body — the title already comes from frontmatter.
- One blank line before and after every heading.
- Keep heading text concise; sentence case preferred for English.

### Paragraphs & spacing
- One blank line between blocks (paragraphs, headings, lists, code, quotes).
- Collapse 2+ blank lines into 1; remove trailing whitespace on every line.
- File ends with exactly one trailing newline.
- No indentation at top level.

### Lists
- Unordered lists use `- ` (single space after the dash).
- Ordered lists use `1. `, `2. `, … (keep the author's numbering).
- Nested items indented 2 spaces; code blocks inside a list indented to align
  with the list item text.
- One blank line before and after a list (except when a list immediately
  follows a heading — still add one blank line after the heading, then the list).

### Code blocks
- Fenced with triple backticks and a language tag when known
  (` ```python `, ` ```bash `, …).
- Blank line before and after the fence.
- **Never modify code inside the fence** (no re-indent, no renaming).

### Inline formatting
- Inline code with single backticks for identifiers, paths, commands, and
  file names (`marked.js`, `blog/posts/`).
- Bold key terms with `**term**`; italics with `*term*` (sparingly).
- Links as `[text](https://...)`; keep existing URLs unchanged.
- Images as `![alt](url)` on their own line, blank line before and after.

### Tables (if any)
- Header row, separator row of `---` (aligned pipes optional), then body rows.
- Blank line before and after the table.

## Procedure

1. Identify the target file(s): the file open in the editor, files the user
   names, or a draft pasted into chat.
2. Read the current content.
3. Parse and normalize the frontmatter (title + date).
4. Apply the formatting rules above; write the result back to the same file
   (in place). Preserve code blocks, URLs, and the author's meaning exactly.
5. Do **not** change wording, facts, or structure intent — only presentation.
6. Summarize what changed as a short bullet list, and:
   - If this is a **new** post, remind the user to add an entry in `blog.html`
     (`<li class="post-item">…</li>`, newest first) with the same slug.
   - If the post was renamed, mention that the slug must match the filename.

## Example

Before:

````markdown
Post title

intro paragraph no space
##Why this matters
- point one
- point two with **bold**
```python
x = 1
```
````

After:

````markdown
---
title: Post title
date: August 15, 2026
---

Intro paragraph, with blank lines around everything.

## Why this matters

- point one
- point two with **bold**

```python
x = 1
```
````
