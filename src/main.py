from pathlib import Path
import shutil
import re
from textnode import markdown_to_html_node


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path) -> None:
    # delete public folder and recreate an empty one
    print(f"Deleting folder: {dest_dir_path}")
    shutil.rmtree(dest_dir_path, ignore_errors=True)
    print(f"Creating folder: {dest_dir_path}")
    dest_dir_path.mkdir()  # dest_dir_path

    static_dir_contents = list(dir_path_content.rglob('*'))
    src_dst_list = []
    # create destination paths from source directory
    for path in static_dir_contents:
        src_dst_list.append(
            (path,
             dest_dir_path / path.relative_to(dir_path_content))
        )

    # create destination folders and generate html files
    for src, dst in src_dst_list:
        if src.is_dir():
            dst.mkdir(exist_ok=True, parents=True)
            print(f"Creating folder: {dst}")
        else:
            if src.suffix == '.md':
                dst = dst.with_suffix('.html')
                generate_page(src, template_path, dst)
            else:
                print(f"Copying {src} to {dst}")
                shutil.copy2(src, dst)

    pass


def extract_title(markdown: str) -> str:
    title_regex = re.compile(r"^(#) (?!#).*$", re.MULTILINE)
    title = re.search(title_regex, markdown)

    if title:
        return title.group().strip('# ')
    else:
        raise ValueError("Title not found")


def generate_page(from_path: Path, template_path: Path, dest_path: Path) -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, 'r', encoding="utf-8") as f:
        markdown = f.read()
    with open(template_path, 'r', encoding="utf-8") as f:
        template = f.read()

    title = extract_title(markdown)
    content = markdown_to_html_node(markdown).to_html()

    html_page = template.replace("{{ Title }}", title).replace("{{ Content }}", content)

    dest_path.touch()
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html_page)

    pass


def main():
    public_dir_path = Path("../public")
    content_dir_path = Path("../content")
    html_template_file = Path("../template.html")
    generate_pages_recursive(content_dir_path, html_template_file, public_dir_path)


main()
