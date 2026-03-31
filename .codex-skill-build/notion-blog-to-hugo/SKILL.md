---
name: notion-blog-to-hugo
description: Use when a user wants to convert a Notion page into a Hugo blog post, especially for bilingual Chinese and English publishing, title and slug generation, image placeholder handling, and creating paired `index.zh.md` and `index.en.md` files under a Hugo `content/post/slug/` folder.
---

# Notion Blog To Hugo

## Overview

Convert a Notion blog page into a Hugo post folder with bilingual Markdown files. Use this when the repository already follows a Hugo content layout and the user wants the page turned into publishable Chinese and English posts without manually copying content.

## Workflow

1. Confirm the repository is a Hugo blog and inspect existing post structure.
2. Fetch the Notion page content with the Notion MCP tools.
3. Read a few nearby posts to match front matter, tone, and folder conventions.
4. Infer a concise title and slug from the article topic instead of copying generic Notion page titles such as `正文`.
5. Create `content/post/<slug>/`.
6. Write `index.zh.md` and `index.en.md`.
7. Create an `images/` directory placeholder, but do not download images unless the user explicitly asks for that.
8. Run a local Hugo build to verify the new content does not break the site.

## Repository Discovery

Inspect the local repository before writing anything.

- Prefer `rg --files content/post` to understand the post layout.
- Open 1-3 existing bilingual posts to copy the exact front matter style.
- Check whether the repo uses `index.zh.md` and `index.en.md` in a folder, or another naming pattern.
- Reuse the existing category style instead of inventing a new taxonomy without evidence.

If the repository is not Hugo-based, stop and adapt only after verifying the real content system.

## Notion Intake

Fetch the Notion page directly.

- Use `notion_fetch` on the user-provided page URL or page ID.
- Treat the Notion page title as a weak hint only. Many blog drafts use placeholders like `正文`, which should not become the published title.
- Extract the real topic, structure, and any image references from the body.
- Preserve the article's argument and technical intent instead of compressing it into a shallow summary.

If the page includes images:

- Keep Markdown image references local, using `images/<filename>`.
- Infer stable filenames from the image meaning when possible.
- Do not download remote assets unless the user explicitly asks for that.
- If the user says they will download images themselves, create the `images/` directory and leave placeholders only.

## Naming Rules

Generate a better publishing title and slug from the content.

- Prefer titles that match the site's existing editorial style, such as `一文读懂 X` or `Understanding X` when that fits the repository.
- Keep the slug short, concrete, and topic-based.
- Avoid generic slugs like `blog-post`, `notion-post`, or date-only names.
- Avoid transliterated Chinese pinyin slugs when an obvious English technical term exists.

Good examples:

- Topic: DCGM architecture and tooling
- Slug: `dcgm`
- Chinese title: `一文读懂 DCGM：从 NVML 到 HostEngine 的 GPU 管理体系`
- English title: `Understanding DCGM: The GPU Management Stack from NVML to HostEngine`

## Writing Rules

Produce two files in the same post folder.

- `index.zh.md`: polished Chinese article based on the original Notion content
- `index.en.md`: faithful English version, rewritten naturally rather than line-by-line literal translation

Keep these rules:

- Match the repository's front matter field names and ordering.
- Preserve the article structure unless there is a clear readability issue.
- Write a real `summary` for both languages.
- Keep `draft: false` unless the user explicitly wants a draft.
- Use relative image links like `![caption](images/file.png)`.
- Do not mention internal workflow details inside the article body.

Use the repository timezone/date style if it is visible in existing posts.

## Front Matter and Structure

Follow the repo's existing pattern exactly. In many bilingual Hugo repos, the expected layout is:

- `content/post/<slug>/index.zh.md`
- `content/post/<slug>/index.en.md`
- `content/post/<slug>/images/`

If needed, read [references/hugo-post-pattern.md](references/hugo-post-pattern.md) for a compact checklist and example front matter.

## Translation Guidance

Translate for publication quality, not sentence mirroring.

- Preserve technical correctness of tool names, APIs, product names, and architecture terms.
- Keep terms like `HostEngine`, `NVML`, `DCGM Exporter`, `NVIDIA-SMI`, `GPU Group`, and `Field Group` in their standard English forms.
- Translate explanatory prose naturally for the target language.
- Preserve headings, lists, and code identifiers.

The English version should read like a native technical blog post, not like machine-translated notes.

## Verification

Before claiming completion:

- Read the generated files back once.
- Run `hugo`.
- Report build failures if they exist.
- If the build passes with pre-existing warnings, say so clearly and distinguish them from new issues.

## Common Mistakes

- Using the raw Notion page title as the blog title when it is only a placeholder.
- Writing into a single Markdown file when the repo expects a folder with bilingual `index.*.md`.
- Downloading images even though the user explicitly said they will handle images themselves.
- Translating file names or tool names inconsistently across the two language versions.
- Skipping a Hugo build and then claiming the post is ready.
