# mkwww

A static site generator that converts `/posts` into `/output`.

## Prerequisites

Use macOS for local development and Cloudflare for deployment.

### Local

- Install [Pandoc](https://github.com/jgm/pandoc)
- Update `config.sh`

### Cloudflare

Cloudflare Pages build configuration:

- Set variable `CF_PAGES` to `true`
- Build command: `./mkwww.sh`
- Output: `/output`

## Usage

For a one-time local build, run `./mkwww.sh` directly. For a hot-rebuilding development server, run `./dev-server.py`.

## Post frontmatter

Page frontmatter is in [YAML](./posts/wikiwil.md).

| Key        | Description                       | Required? |
| ---------- | ----------------------------------| ----------|
| `title`    | Page title                        | Yes       |
| `date`     | Publication date                  | No        |
| `subtitle` | Page subtitle                     | No        |
| `unlisted` | `true` suppress the index listing | No        |

Posts are listed in `index.html`, newest first. Undated posts appear last.

## Changelog

- v3.1: Dev server
- v2.5: Pretty URLs
- v2.x: Templating
- v1.x: Pandoc
- v0.0: An idea in the shower