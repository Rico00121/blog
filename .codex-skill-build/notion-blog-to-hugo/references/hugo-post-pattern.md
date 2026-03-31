# Hugo Bilingual Post Pattern

Use this reference when the target repository already contains bilingual Hugo posts.

## Expected Folder Layout

```text
content/post/<slug>/
  index.zh.md
  index.en.md
  images/
```

Create `images/` even when images are not downloaded yet if the article references local images.

## Minimal Front Matter Checklist

Match the repository's actual field names and ordering, but this is the common pattern:

```yaml
---
title: "..."
date: 2026-03-23T00:00:00+02:00
Description: ""
Tags: []
Categories: ["..."]
summary: "..."
DisableComments: false
draft: false
---
```

## Recommended Steps

1. Read 1-3 existing posts under `content/post/`.
2. Match the front matter style exactly.
3. Infer a slug from the article topic.
4. Create `index.zh.md` from the Notion source.
5. Create `index.en.md` as a publishable translation.
6. Replace remote image URLs with local `images/<filename>` references.
7. Leave image downloading to the user unless explicitly requested.
8. Run `hugo` to verify the site still builds.

## Title and Slug Heuristics

- Prefer short topic slugs such as `dcgm`, `prometheus-core-mechanism`, or `aws-elb`.
- Prefer reader-facing titles over internal draft titles.
- If the Chinese title follows a repository pattern like `一文读懂 X`, keep the English title equally editorial instead of overly literal.
