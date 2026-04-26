#!/usr/bin/env python
import os
import re
import zipfile
import urllib.request
import shutil

# Condensed repo containing all styles
ZIP_URL = "https://github.com/marella/material-design-icons/archive/refs/heads/main.zip"
ZIP_FILE = "material_icons_small.zip"
EXTRACT_DIR = "material_icons_small_temp"
OUTPUT_DIR = "src"

def to_pascal_case(name):
    return ''.join(word.capitalize() for word in re.split(r'[-_]', name))

def generate_icons():
    # 1. Download
    if not os.path.exists(ZIP_FILE):
        print(f"Downloading {ZIP_URL}...")
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(ZIP_URL, ZIP_FILE)
    
    # 2. Extract
    if not os.path.exists(EXTRACT_DIR):
        print(f"Extracting {ZIP_FILE}...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

    # 3. Find svg directory
    base_svg_dir = ""
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if root.endswith("svg") and os.path.isdir(root):
            base_svg_dir = root
            break
            
    if not base_svg_dir:
        print("Error: Could not find svg directory")
        return

    styles = ["filled", "outlined", "round", "sharp", "two-tone"]
    total_count = 0

    for style in styles:
        style_src = os.path.join(base_svg_dir, style)
        if not os.path.exists(style_src):
            continue
            
        style_out = os.path.join(OUTPUT_DIR, style)
        if not os.path.exists(style_out):
            os.makedirs(style_out)

        print(f"Generating '{style}' icons...")
        style_suffix = to_pascal_case(style) if style != "filled" else ""
        
        count = 0
        for filename in os.listdir(style_src):
            if filename.endswith(".svg"):
                icon_name = filename[:-4]
                svg_path = os.path.join(style_src, filename)
                
                with open(svg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                inner_match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
                if inner_match:
                    inner_content = inner_match.group(1).strip()
                    # Remove explicit fills to allow 'currentColor' to work
                    inner_content = re.sub(r' fill="[^"]*"', '', inner_content)
                    
                    pascal_name = to_pascal_case(icon_name) + style_suffix
                    if pascal_name[0].isdigit():
                        pascal_name = "Icon" + pascal_name

                    component_code = f"""public #universal {pascal_name}(props) {{
    return <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" {{...props}}>
        {inner_content}
    </svg>
}}
"""
                    output_file = os.path.join(style_out, f"{to_pascal_case(icon_name)}.ch")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(component_code)
                    count += 1
        
        print(f"Generated {count} {style} icons.")
        total_count += count

    print(f"Successfully generated {total_count} icons in {OUTPUT_DIR}/")

if __name__ == "__main__":
    generate_icons()
