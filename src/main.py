import os
import shutil
from helpers import markdown_to_html_node
from htmlnode import LeafNode
from textnode import TextNode, TextType


def main():
    copy_to("static", "public")
    generate_pages_recursive("content", "template.html", "public")

def copy_to(source, destination):
    list = os.listdir(destination)
    for i in list:
        path = os.path.join(destination, i)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    
    list = os.listdir(source)
    for i in list:
        path = os.path.join(source, i)
        if os.path.isfile(path):
            print(f"copying file {i} from {source} to {destination}")
            shutil.copy(path, destination)
        else:
            dest_path = os.path.join(destination, i)
            os.mkdir(dest_path)
            copy_to(path, dest_path)

def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No title found")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path)as f:
        from_file = f.read()
    with open(template_path)as f:
        template = f.read()
    html = markdown_to_html_node(from_file).to_html()
    title = extract_title(from_file)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    with open(dest_path, 'x') as f:
        f.write(template)
    
def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    list = os.listdir(dir_path_content)
    for i in list:
        from_file_path = os.path.join(dir_path_content, i)
        if os.path.isfile(from_file_path):
            if i.endswith(".md"):
                dest_file_path = os.path.join(dest_dir_path, i.replace(".md", ".html"))
                print(f"generating html file from file {from_file_path} to {dest_file_path} using {template_path}")
                generate_page(from_file_path, template_path, dest_file_path)
        else:
            dest_file_path = os.path.join(dest_dir_path, i)
            generate_pages_recursive(from_file_path, template_path, dest_file_path)


main()