# Transformer QKV Notion-to-Hugo Design

## Goal

Convert the Notion page “对于 Transformer 的 QKV 机制的思考” into the blog's existing bilingual Hugo post format while preserving the author's original argument and personal learning-note tone.

Source page: `https://www.notion.so/Transformer-QKV-3b9068df012c800d8c0ddfa9cd0afbca?source=copy_link`

Retrieve the source with the Notion MCP `fetch` operation before writing. The fetched page content is the authority for the article wording, sequence, and absence of image references.

## Publishing Structure

- Post directory: `content/post/transformer-qkv/`
- Chinese article: `index.zh.md`
- English article: `index.en.md`
- Image placeholder directory: `images/`
- Add `images/.gitkeep` so the required empty placeholder directory is represented in Git.
- The Notion page contains no image references, so no other assets will be downloaded or linked.

## Front Matter

- Chinese title: `理解 Transformer 的 QKV：为什么注意力机制需要 Key 和 Value`
- English title: `Understanding Transformer QKV: Why Attention Needs Both Keys and Values`
- Date: `2026-08-11`
- Category: `Machine Learning`
- Draft status: `false`
- Use the field names and ordering found in nearby bilingual posts.
- Write one concise, concrete summary for each language.

## Editorial Treatment

Use the user-selected near-verbatim approach:

- Preserve the original sequence of ideas and conclusions.
- Retain the first-person, exploratory voice.
- Fix punctuation, spacing, obvious grammar problems, and Markdown structure.
- Do not add formulas, external research, new examples, or tutorial sections.
- Do not substantially expand or fact-check the author's claims.
- Where literal wording would be hard to read, make the smallest rephrasing that preserves the intended claim.

The English version will be a natural publication-quality translation rather than a sentence-by-sentence mechanical translation, but it will not introduce material absent from the Chinese source.

## Article Structure

Both language versions will follow the Notion page's structure:

1. Opening reflection on studying Transformer QKV
2. Division of responsibilities among Query, Key, and Value
3. Why Query does not directly match Value
4. Three ways Transformer represents multiple attributes:
   - Key vector dimensions
   - Multi-Head Attention
   - Stacked Transformer layers/blocks
5. Short conclusion

## Verification

- Read both generated Markdown files back after writing.
- Confirm the expected front matter and matching bilingual section structure.
- Run the local `hugo` build.
- Report any failure and distinguish pre-existing warnings from new content problems.
