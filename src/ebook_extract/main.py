import os
import sys
import json
from ebooklib import epub
from bs4 import BeautifulSoup

# Optional: pretty printing with colors
from datetime import datetime

def log(msg, icon="📘", color="\033[94m"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {icon} {msg}\033[0m")

def success(msg):
    log(msg, icon="✅", color="\033[92m")

def warn(msg):
    log(msg, icon="⚠️", color="\033[93m")

def error(msg):
    log(msg, icon="❌", color="\033[91m")

def extract_epub_metadata(epub_path):
    log(f"Opening EPUB file: {epub_path}", icon="📂")

    try:
        book = epub.read_epub(epub_path)
        success("EPUB file successfully loaded!")
    except Exception as e:
        error(f"Failed to open EPUB: {e}")
        sys.exit(1)

    metadata = {}
    log("Extracting standard metadata (Dublin Core)...", icon="🧾")

    # Standard metadata
    for namespace, meta_dict in book.metadata.items():
        log(f"Found metadata namespace: {namespace}", icon="📚")
        for key, values in meta_dict.items():
            for v in values:
                val = str(v)
                log(f"  - {key}: {val}", icon="🔹")
                metadata.setdefault(key, []).append(val)

    # Custom <meta> tags
    log("Looking for embedded <meta> tags in content...", icon="🔍")
    metadata['custom_meta'] = []
    for item in book.get_items_of_type(epub.EpubHtml):
        if item.file_name.endswith('.opf') or 'content.opf' in item.file_name:
            log(f"  - Parsing OPF file: {item.file_name}", icon="📄")
            soup = BeautifulSoup(item.get_content(), 'xml')
            for meta in soup.find_all('meta'):
                metadata['custom_meta'].append(meta.attrs)
                log(f"    + Meta tag: {meta.attrs}", icon="🧷")

    if not metadata['custom_meta']:
        warn("No custom <meta> tags found.")

    # Extract cover image
    log("Checking for cover image...", icon="🖼️")
    cover_item = None
    try:
        cover_item = book.get_item_with_id('cover')
    except:
        pass

    if cover_item:
        cover_filename = os.path.basename(epub_path).replace('.epub', '_cover.jpg')
        with open(cover_filename, 'wb') as f:
            f.write(cover_item.get_content())
        success(f"Cover image extracted to {cover_filename}")
        metadata['cover_image'] = cover_filename
    else:
        warn("No cover image found in EPUB.")

    return metadata

if __name__ == "__main__":
    if len(sys.argv) != 2:
        error("Usage: python extract_metadata.py your_book.epub")
        sys.exit(1)

    epub_path = sys.argv[1]
    if not os.path.exists(epub_path):
        error(f"File not found: {epub_path}")
        sys.exit(1)

    meta = extract_epub_metadata(epub_path)
    output_file = os.path.splitext(epub_path)[0] + "_metadata.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    success(f"Metadata saved to {output_file}")

