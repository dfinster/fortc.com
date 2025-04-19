# mkwww

A static site generator that converts `/posts` into `/output`.

## Prerequisites

Use macOS with Python installed for local development. Use Cloudflare for deployment.

### Local

- Update `config.py` with your information

### Cloudflare

Cloudflare Pages build configuration:

- Set variable `CF_PAGES` to `true`
- Build command: `./mkwww.py`
- Output: `/output`

## Usage

Launch the hot-rebuilding development server with `./mkwww.py`.

## Post frontmatter

Page frontmatter is in [YAML](./posts/wikiwil.md).

| Key           | Description                       | Required? |
| ------------- | ----------------------------------| ----------|
| `title`       | Page title                        | Yes       |
| `description` | The OpenGraph description         | Yes       |
| `date`        | Publication date                  | No        |
| `subtitle`    | Page subtitle                     | No        |
| `unlisted`    | `true` suppress the index listing | No        |

Posts are listed in `index.html`, newest first. Undated posts appear last.

## Changelog

- v4.0: Okay, this is getting silly. Convert everything to Python and remove Pandoc.
- v3.0: Add Dev server in Python, which calls Bash script for hot reloading.
- v2.5: Add Pretty URLs to Bash script
- v2.0: Add Templating to Bash script
- v1.0: Use Pandoc in Bash script
- v0.0: An idea in the shower: Can I make an SSG in Bash?