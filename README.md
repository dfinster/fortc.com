# mkwww.sh v2.1 for [fortc.com](https://fortc.com)

## Description

A minimal static Markdown-to-HTML blog generator in bash, awk, sed, and Pandoc.

_It's the dumbest thing that could possibly work._ [WIKIWIL](https://fortc.com/wikiwil)

- Converts Markdown `/posts` to static HTML `/output`.
- `title:` frontmatter is required.
- `unlisted: true` frontmatter suppresses the listing.
- `subtitle:` and `date:` frontmatter are optional.
- Posts are sorted in reverse date order in `index.html`. Undated posts appear last in filesystem order.
- Designed for deployment at Cloudflare.

## Prerequisites

To run `mkwww.sh`:

- Set `config.sh` to your values
- Install [Pandoc](https://github.com/jgm/pandoc)
- Have a `bash` shell with `awk`, `sed`, and other other typical GNU tools
- Set `"$CF_PAGES" = "true"` in Cloudflare build configuration to auto-install Pandoc in the build container.

## Usage

Run the script in the repo's root:

```bash
$ ./mkwww.sh
```

View the local output in a browser: `./output/index.html`

## License

See [LICENSE.md](LICENSE.md) for details.
