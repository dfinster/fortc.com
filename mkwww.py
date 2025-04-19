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

# Detect Cloudflare Pages from environment variable
CF_PAGES = os.environ.get('CF_PAGES', 'false').lower() == 'true'

# Paths and cache
OUTPUT_DIR = config.OUTPUT_DIR
INDEX_FILENAME = config.INDEX_FILENAME
INDEX_FILE = os.path.join(OUTPUT_DIR, INDEX_FILENAME)
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

# LiveReload only for dev
Server = None
if not CF_PAGES:
    try:
        from livereload import Server
    except ImportError:
        logging.info('livereload not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'livereload'])
        from livereload import Server

# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log_info = logging.info
log_error = logging.error

# Utility: initialize output
def initialize_output():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if os.path.isdir(config.STATIC_DIR):
        shutil.copytree(config.STATIC_DIR, OUTPUT_DIR, dirs_exist_ok=True)

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
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
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
    with open(INDEX_FILE, 'a', encoding='utf-8') as f:
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
    if lines and lines[0].strip() == '---':
        idx = 1
        while idx < len(lines) and lines[idx].strip() != '---':
            if ':' in lines[idx]:
                k, v = lines[idx].split(':', 1)
                meta[k.strip()] = v.strip()
            idx += 1
        content = '\n'.join(lines[idx+1:])
    else:
        content = '\n'.join(lines)
    return meta, content

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
    items = []
    for mdfile in glob(os.path.join(config.POSTS_DIR, '*.md')):
        meta, content = parse_frontmatter_and_content(mdfile)
        items.append((meta.get('date', ''), mdfile, meta, content))
    items.sort(key=lambda x: x[0], reverse=True)
    for _, fp, meta, content in items:
        name = splitext(basename(fp))[0]
        out = os.path.join(OUTPUT_DIR, f'{name}.html')
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
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page)
        youtube_shortcode(out)
        if meta.get('unlisted', 'false').lower() != 'true':
            with open(INDEX_FILE, 'a', encoding='utf-8') as idx:
                idx.write(build_index_item(fp, meta))
        else:
            log_info(f'Skipping unlisted: {name}')

# Build workflow

def build_site():
    log_info('Building site...')
    initialize_output()
    create_index_header()
    generate_posts()
    create_index_footer()
    log_info('Build complete.')

# WSGI application for pretty URLs
def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    # strip leading slash
    rel = path.lstrip('/')
    local = os.path.join(OUTPUT_DIR, unquote(rel))
    if os.path.isdir(local):
        local = os.path.join(local, 'index.html')
    elif not os.path.splitext(local)[1] and os.path.exists(local + '.html'):
        local += '.html'
    if not os.path.exists(local):
        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'404 Not Found']
    content_type = mimetypes.guess_type(local)[0] or 'application/octet-stream'
    data = open(local, 'rb').read()
    start_response('200 OK', [('Content-Type', content_type)])
    return [data]

# Entrypoint
if __name__ == '__main__':
    if CF_PAGES:
        build_site()
        sys.exit(0)

    # Dev server with live reload and pretty URLs
    server = Server(application)
    server.watch(config.POSTS_DIR + '/*.md', build_site)
    server.watch(config.TEMPLATES_DIR + '/*.tmpl', build_site)
    server.watch(config.STATIC_DIR + '/**/*', build_site)
    build_site()
    server.serve(host='0.0.0.0', port=config.PORT, root=None, open_url_delay=1)
