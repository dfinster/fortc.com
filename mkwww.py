#!/usr/bin/env python3
# MIT License (c) 2025 David Finster

import os
import sys
import logging
import shutil
import re
import mimetypes
from datetime import datetime
from glob import glob
from urllib.parse import unquote
import subprocess

# External configuration
import config

# Detect Cloudflare Pages environment
CF_PAGES = os.environ.get('CF_PAGES', 'false').lower() == 'true'

# Compute variables
INDEX_FILENAME = os.path.join(config.OUTPUT_DIR, 'index.html')
CACHE_VERSION = datetime.now().strftime('%Y%m%d%H%M%S')

# Markdown renderer: ensure markdown-it-py
try:
    from markdown_it import MarkdownIt
except ImportError:
    if not CF_PAGES:
        logging.info('markdown-it-py not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'markdown-it-py'])
    from markdown_it import MarkdownIt
md = MarkdownIt('commonmark', {'html': True, 'linkify': True, 'typographer': True})

# Only import and install livereload if not on CF_PAGES
global Server
if not CF_PAGES:
    try:
        from livereload import Server
    except ImportError:
        logging.info('livereload not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'livereload'])
        from livereload import Server

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log_info = logging.info
log_error = logging.error

# Prepare output directory
def initialize_output():
    if os.path.exists(config.OUTPUT_DIR):
        shutil.rmtree(config.OUTPUT_DIR)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    if os.path.isdir(config.STATIC_DIR):
        shutil.copytree(config.STATIC_DIR, config.OUTPUT_DIR, dirs_exist_ok=True)

# Index header/footer

def create_index_header():
    path = os.path.join(config.TEMPLATES_DIR, 'index-header.tmpl')
    text = open(path, 'r', encoding='utf-8').read()
    for key, val in {
        '%%CACHE_BUSTER_STYLE%%': f'style.css?v={CACHE_VERSION}',
        '%%CANONICAL_HOST%%': config.CANONICAL_HOST,
        '%%AUTHOR%%': config.AUTHOR,
        '%%SITE_DESCRIPTION%%': config.SITE_DESCRIPTION,
        '%%SITE_NAME%%': config.SITE_NAME,
        '%%COPYRIGHT%%': config.COPYRIGHT,
    }.items():
        text = text.replace(key, val)
    os.makedirs(os.path.dirname(INDEX_FILENAME), exist_ok=True)
    with open(INDEX_FILENAME, 'w', encoding='utf-8') as f:
        f.write(text)


def create_index_footer():
    path = os.path.join(config.TEMPLATES_DIR, 'index-footer.tmpl')
    text = open(path, 'r', encoding='utf-8').read()
    for key, val in {
        '%%CACHE_BUSTER_STYLE%%': f'style.css?v={CACHE_VERSION}',
        '%%AUTHOR%%': config.AUTHOR,
        '%%SITE_DESCRIPTION%%': config.SITE_DESCRIPTION,
        '%%SITE_NAME%%': config.SITE_NAME,
        '%%COPYRIGHT%%': config.COPYRIGHT,
    }.items():
        text = text.replace(key, val)
    with open(INDEX_FILENAME, 'a', encoding='utf-8') as f:
        f.write(text)

# YouTube shortcode
YOUTUBE_PATTERN = re.compile(r'\{\{youtube:([A-Za-z0-9_-]+)\}\}')

def youtube_shortcode(html_path):
    tmpl = open(os.path.join(config.TEMPLATES_DIR, 'youtube-shortcode.tmpl'), encoding='utf-8').read()
    content = open(html_path, encoding='utf-8').read()
    new = YOUTUBE_PATTERN.sub(lambda m: tmpl.replace('%%YOUTUBE_ID%%', m.group(1)), content)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new)

# Frontmatter parser
def parse_frontmatter_and_content(fp):
    lines = open(fp, encoding='utf-8').read().splitlines()
    meta = {}
    content_lines = []
    if lines and lines[0].strip() == '---':
        idx = 1
        while idx < len(lines) and lines[idx].strip() != '---':
            if ':' in lines[idx]:
                k, v = lines[idx].split(':', 1)
                meta[k.strip()] = v.strip()
            idx += 1
        content_lines = lines[idx+1:]
    else:
        content_lines = lines
    return meta, '\n'.join(content_lines)

from os.path import basename, splitext

def build_index_item(fp, meta):
    templ = open(os.path.join(config.TEMPLATES_DIR, 'index-item.tmpl'), encoding='utf-8').read()
    name = splitext(basename(fp))[0]
    templ = templ.replace('%%FILE%%', name)
    templ = templ.replace('%%TITLE%%', meta.get('title', name))
    date = meta.get('date', '')
    templ = templ.replace('%%DATE%%', f'({date})' if date else '')
    return templ

# Generate posts
def generate_posts():
    posts = []
    for mdfile in glob(os.path.join(config.POSTS_DIR, '*.md')):
        meta, content = parse_frontmatter_and_content(mdfile)
        posts.append((meta.get('date', ''), mdfile, meta, content))
    posts.sort(key=lambda x: x[0], reverse=True)
    for _, fp, meta, content in posts:
        name = splitext(basename(fp))[0]
        out = os.path.join(config.OUTPUT_DIR, f'{name}.html')
        html = md.render(content)
        page = open(os.path.join(config.TEMPLATES_DIR, 'post.tmpl'), encoding='utf-8').read()
        for key, val in {
            '$body$': html,
            '$title$': meta.get('title', ''),
            '$subtitle$': meta.get('subtitle', ''),
            '$date$': meta.get('date', ''),
            '$author$': config.AUTHOR,
            '%%CANONICAL_PAGE%%': config.CANONICAL_HOST + name,
            '%%CACHE_BUSTER_STYLE%%': f'style.css?v={CACHE_VERSION}',
            '%%AUTHOR%%': config.AUTHOR,
            '%%DESCRIPTION%%': meta.get('description', ''),
            '%%SITE_NAME%%': config.SITE_NAME,
            '%%COPYRIGHT%%': config.COPYRIGHT,
        }.items():
            page = page.replace(key, val)
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page)
        youtube_shortcode(out)
        if meta.get('unlisted', 'false').lower() != 'true':
            with open(INDEX_FILENAME, 'a', encoding='utf-8') as idx:
                idx.write(build_index_item(fp, meta))
        else:
            log_info(f'Skipping unlisted: {name}')

# Build site workflow
def build_site():
    log_info('Building site...')
    initialize_output()
    create_index_header()
    generate_posts()
    create_index_footer()
    log_info('Build complete.')

# If CF_PAGES, only build and exit
if __name__ == '__main__':
    if CF_PAGES:
        build_site()
        sys.exit(0)

    # Development: live reload and server
    server = Server()  # uses default app
    server.watch(config.POSTS_DIR + '/*.md', build_site)
    server.watch(config.TEMPLATES_DIR + '/*.tmpl', build_site)
    build_site()
    server.serve(host='0.0.0.0', port=config.PORT, open_url_delay=1)
