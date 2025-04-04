# mkwww.sh v2.1 for [fortc.com](https://fortc.com)

## Description

A minimal static Markdown-to-HTML blog generator.

It's the dumbest thing that could possibly work.

- Converts Markdown in `/posts` to static HTML in `/output`
- Sorts the posts in reverse order from the frontmatter date
- Undated posts render at the end of the list in whatever order
- Subtitles are optional frontmatter
- Designed to deploy at Cloudflare

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

`mkwww.sh`, and the contents of `/static` and `/templates` are [MIT license](./LICENSE).

[fortc.com](https://fortc.com) blog content is Copyright (c) 2025 David Finster
