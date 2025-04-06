# mkwww.sh v2.1 for [fortc.com](https://fortc.com)

## Description

A minimal static Markdown-to-HTML blog generator in bash, awk, sed, and Pandoc.

_It's the dumbest thing that could possibly work._ [WIKIWIL](https://fortc.com/wikiwil)

`mkwww.sh` converts Markdown `/posts` to static HTML `/output`. It's designed to run locally in macOS, or at Cloudflare.

### Frontmatter

Frontmatter is yaml.

| Key        | Description                         | Required? |
| ---------- | ------------------------------------| ----------|
| `title`    | Page title                          | Yes       |
| `unlisted` | `true` suppresses the index listing | No        |
| `subtitle` | Page subtitle                       | No        |
| `date`     | Publication date                    | No        |

Posts (other than `unlisted: true`) are in `index.html`, sorted with newest on top and undated posts at the bottom in filesystem order.

## Prerequisites

1. Set `config.sh` to your values.
1. Install [Pandoc](https://github.com/jgm/pandoc).
1. Use a `bash` shell with `awk`, `sed`, and other other typical GNU tools.
1. Set `"$CF_PAGES" = "true"` in Cloudflare's build configuration.

## Usage

1. Run the script in the repo's root.

    ```bash
    $ ./mkwww.sh
    ```

1. Preview the output: `./output/index.html`
1. Deploy to Cloudflare Pages.

## License

See [LICENSE.md](LICENSE.md) for details.
