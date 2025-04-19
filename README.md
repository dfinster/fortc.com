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
- v4.0: Convert to pure Python
- v3.1: Dev server
- v2.5: Pretty URLs
- v2.x: Templating
- v1.x: Pandoc
- v0.0: An idea in the shower