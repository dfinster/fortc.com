#!/usr/bin/env bash
# MIT License (c) 2025 David Finster

# Set up environment and logging
set -euo pipefail
trap 'log_error "Build interrupted or error occurred."; exit 1' ERR INT

init_script() {
  source config.sh
}
log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}
log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
}

# Check if running on Cloudflare Pages
is_cloudflare() {
  [ "${CF_PAGES:-}" = "true" ]
}

# Cross-platform sed replacement
replace_in_file() {
  local filepath="$1"
  local search="$2"
  local replace="$3"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|$search|$replace|g" "$filepath"
  else
    sed -i "s|$search|$replace|g" "$filepath"
  fi
}

# {{youtube:VIDEO_ID}} shortcode
youtube_shortcode() {
  local file="$1"
  local pattern='\{\{youtube:([a-zA-Z0-9_-]+)\}\}'
  local video_shortcode video_id template replacement
  # Loop while a YouTube shortcode exists in the file
  while video_shortcode=$(grep -Eo "$pattern" "$file" | head -n 1); do
    # Extract the video ID from the shortcode
    video_id=$(echo "$video_shortcode" | sed -E 's/\{\{youtube:([a-zA-Z0-9_-]+)\}\}/\1/')
    template=$(cat templates/youtube-shortcode.tmpl)
    replacement=$(echo "$template" | sed "s/%%YOUTUBE_ID%%/$video_id/g")
    replace_in_file "$file" "$video_shortcode" "$replacement"
  done
}

# Create links to posts
build_index_item() {
  local file="$1"
  local title="$2"
  local date="$3"
  local template
  template=$(cat templates/index-item.tmpl)
  local link_path="${file%.html}"
  template=$(echo "$template" | sed "s|%%FILE%%|$link_path|g")
  template=$(echo "$template" | sed "s|%%TITLE%%|$title|g")
  template=$(echo "$template" | sed "s|%%DATE%%|$date|g")
  echo "$template"
}

# Find Pandoc or install if is_cloudflare()
detect_pandoc() {
  if command -v pandoc >/dev/null 2>&1; then
    PANDOC_BIN="pandoc"
  elif is_cloudflare; then
    PANDOC_DIR="./pandoc-bin"
    # Latest version as of April 2025
    PANDOC_VER="3.6.4"
    log_info "Running in Cloudflare Pages."
    log_info "Installing Pandoc $PANDOC_VER."
    mkdir -p "$PANDOC_DIR"
    curl -sL https://github.com/jgm/pandoc/releases/download/$PANDOC_VER/pandoc-$PANDOC_VER-linux-amd64.tar.gz | tar xz --strip-components=2 -C "$PANDOC_DIR" "pandoc-$PANDOC_VER/bin/pandoc"
    PANDOC_BIN="$PANDOC_DIR/pandoc"
  else
    log_error "Please install Pandoc for your platform or set var 'CF_PAGES=true' in Cloudflare Pages config."
    exit 1
  fi
}

# Init the build dir
initialize_output() {
  rm -rf output
  mkdir -p output
  cp -r static/* output/
}

# Make temporary list for sorting
create_temp_list() {
  local temp_file
  temp_file=$(mktemp)
  for file in posts/*.md; do
    local date
    date=$(awk '/^date:/ {print $2}' "$file")
    echo "$date|$file" >> "$temp_file"
  done
  echo "$temp_file"
}

# Init index.html and cache bust the CSS
create_index_header() {
  sed "s|style.css|style.css?v=$CACHE_VERSION|g" templates/index-header.tmpl > "$INDEX_FILE"
}

generate_posts() {
  # Get the list of posts
  temp_list=$(create_temp_list)

  # Sort: entries with dates first (descending), then undated
  sort -r -t '|' -k1,1 "$temp_list" | while IFS='|' read -r date file; do
    filename=$(basename "$file" .md)
    output_file="output/$filename.html"

    # Extract title and unlisted flag
    title=$(awk '/^title:/ {print substr($0, index($0,$2))}' "$file")
    unlisted=$(awk '/^unlisted:/ {print $2}' "$file")

    # If it's zeros in the temp file, null it out.
    if [ -z "$date" ]; then
      display_date=""
    else
      display_date="($date)"
    fi
    log_info "Building: $output_file $display_date"

    "$PANDOC_BIN" "$file" --template=templates/post.tmpl -s -o "$output_file"

    # Shortcodes
    youtube_shortcode "$output_file"

    # Variables
    replace_in_file "$output_file" '%%CANONICAL_PAGE%%' "$CANONICAL_HOST$filename"
    replace_in_file "$output_file" '%%CACHE_BUSTER_STYLE%%' "style.css?v=$CACHE_VERSION"
    replace_in_file "$output_file" '%%AUTHOR%%' "$AUTHOR"
    replace_in_file "$output_file" '%%DESCRIPTION%%' "$DESCRIPTION"
    replace_in_file "$output_file" '%%SITE_NAME%%' "$SITE_NAME"
    replace_in_file "$output_file" '%%COPYRIGHT%%' "$COPYRIGHT"

    # Only add to index if not unlisted
    if [ "$unlisted" != "true" ]; then
      index_item=$(build_index_item "$filename" "$title" "$display_date")
      echo "$index_item" >> "$INDEX_FILE"
    else
      log_info "\033[1;90m↳ Unlisted page\033[0m"
    fi
  done
}

create_index_footer() {
  # Write the index footer
  cat templates/index-footer.tmpl >> "$INDEX_FILE"
  # Search and replace vars in index.html
  replace_in_file "$INDEX_FILE" '%%CACHE_BUSTER_STYLE%%' "style.css?v=$CACHE_VERSION"
  replace_in_file "$INDEX_FILE" '%%AUTHOR%%' "$AUTHOR"
  replace_in_file "$INDEX_FILE" '%%DESCRIPTION%%' "$DESCRIPTION"
  replace_in_file "$INDEX_FILE" '%%SITE_NAME%%' "$SITE_NAME"
  replace_in_file "$INDEX_FILE" '%%COPYRIGHT%%' "$COPYRIGHT"
}

# Cleanup
cleanup_after_build() {
  rm "$temp_list"
}

build_site() {
  init_script
  detect_pandoc
  initialize_output
  create_index_header
  generate_posts
  create_index_footer
  cleanup_after_build
}

main() {

  # If Cloudflare Pages, bypass debouncing
  if is_cloudflare; then
      log_info "Starting build in Cloudflare environment."
      build_site
      exit 0
  fi

  # Debouncing logic
  LOCKDIR="./.mkwww.lock"
  PENDINGFILE="./.mkwww.pending"
  DEBOUNCE_DELAY=1

  if mkdir "$LOCKDIR" 2>/dev/null; then
      echo "Lock acquired."
  else
      echo "Build already in progress, marking pending build."
      touch "$PENDINGFILE"
      exit 0
  fi

  # Build loop
  while true; do
      sleep "$DEBOUNCE_DELAY"
      build_site
      if [ -f "$PENDINGFILE" ]; then
          echo "Pending build detected. Restarting build process."
          rm -f "$PENDINGFILE"
      else
          break
      fi
  done

  # Release the lock
  rmdir "$LOCKDIR"
}

main