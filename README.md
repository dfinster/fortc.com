# mkwww

A static site generator that converts Markdown `/posts` into HTML `/output`.

## Local development

### Prerequisites

1. Have Python3 on your path.
1. Update `config.py` with your information.
1. Create a Python virtual environment.
    ```bash
    $ python3 -m venv .venv
    ```
1. Activate the virtual environment.
    ```bash
    $ source .venv/bin/activate
    ```
1. Install the requirements.
    ```bash
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    ```

### Usage

1. Activate the virtual environment.
    ```bash
    $ source .venv/bin/activate
    ```
1. Enable the local server environment variable.
    ```bash
    $ export USE_SERVER=true
    ````
1. (Alternative) Skip steps 1 and 2 by installing `direnv`, which runs those steps in `.envrc`.
1. Generate the site.
    ```bash
    $ ./mkwww.py
    ```

## Cloudflare deployment

1. Clone this repo.
1. Delete the content of the `/posts/` directory from your cloned version, because that's my copyrighted content. The rest of this repo is [MIT License](./LICENSE.md).
1. Add your posts to `/posts/`.
1. [Connect a Cloudflare Pages project](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/) to your repo.
1. Use this build command:
    ```bash
    ./mkwww.py
    ```
1. Set the output directory to `/output`.
1. Push commits to GitHub to rebuild the site.

## Post frontmatter

Frontmatter is in [YAML](./posts/wikiwil.md).

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