#!/usr/bin/env bash
# MIT License (c) 2025 David Finster

# Set up environment and logging
set -euo pipefail
init_script() {
  source config.sh
}
log_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}
log_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
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

# Create links to posts
build_index_item() {
  local file="$1"
  local title="$2"
  local date="$3"
  local template
  template=$(cat templates/index-item.html-tmpl)
  template=$(echo "$template" | sed "s|%%FILE%%|$file|g")
  template=$(echo "$template" | sed "s|%%TITLE%%|$title|g")
  template=$(echo "$template" | sed "s|%%DATE%%|$date|g")
  echo "$template"
}

# Find Pandoc install or install in Cloudflare
detect_pandoc() {
  if command -v pandoc >/dev/null 2>&1; then
    PANDOC_BIN="pandoc"
  elif [ "${CF_PAGES:-}" = "true" ]; then
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
    # if no date in frontmatter, set it to zeros in temp_file.
    if [ -z "$date" ]; then
      date="0000-00-00"
    fi
    echo "$date|$file" >> "$temp_file"
  done
  echo "$temp_file"
}

# Init index.html and cache bust the CSS
create_index_header() {
  sed "s|style.css|style.css?v=$CACHE_VERSION|g" templates/index-header.html-tmpl > "$INDEX_FILE"
}

generate_posts() {
  # Get the list of posts
  temp_list=$(create_temp_list)

  # Sort by date descending (newest first)
  sort -r "$temp_list" | while IFS='|' read -r date file; do
    filename=$(basename "$file" .md)
    output_file="output/$filename.html"

    # Extract title and unlisted flag
    title=$(awk '/^title:/ {print substr($0, index($0,$2))}' "$file")
    unlisted=$(awk '/^unlisted:/ {print $2}' "$file")

    # If it's zeros in the temp file, null it out.
    if [ "$date" = "0000-00-00" ]; then
      display_date=""
    else
      display_date="($date)"
    fi
    log_info "Building: $output_file $display_date"

    # Create the blog post
    "$PANDOC_BIN" "$file" --template=templates/post.html-tmpl -s -o "$output_file"

    # Search and replace vars in each post
    replace_in_file "$output_file" '%%CANONICAL_PAGE%%' "$CANONICAL_HOST$filename.html"
    replace_in_file "$output_file" '%%CACHE_BUSTER_STYLE%%' "style.css?v=$CACHE_VERSION"
    replace_in_file "$output_file" '%%AUTHOR%%' "$AUTHOR"
    replace_in_file "$output_file" '%%DESCRIPTION%%' "$DESCRIPTION"
    replace_in_file "$output_file" '%%SITE_NAME%%' "$SITE_NAME"
    replace_in_file "$output_file" '%%COPYRIGHT%%' "$COPYRIGHT"

    # Only add to index if not unlisted
    if [ "$unlisted" != "true" ]; then
      index_item=$(build_index_item "$filename.html" "$title" "$display_date")
      echo "$index_item" >> "$INDEX_FILE"
    else
      log_info "\033[1;90m↳ Unlisted page\033[0m"
    fi
  done
}

create_index_footer() {
  # Write the index footer
  cat templates/index-footer.html-tmpl >> "$INDEX_FILE"
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

main() {
  init_script
  detect_pandoc
  initialize_output
  create_index_header
  generate_posts
  create_index_footer
  cleanup_after_build
}

main