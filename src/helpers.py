import re
from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered_list"
block_type_ulist = "unordered_list"

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    nodes = []
    for node in old_nodes:
        if delimiter not in node.text or node.text_type != TextType.TEXT:
            nodes.append(node)
            continue
        fields = node.text.split(delimiter)
        if len(fields) % 2 == 0:
            print(fields)
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(0, len(fields)):
            if fields[i] == "":
                continue
            if i % 2 == 0:
                nodes.append(TextNode(fields[i], TextType.TEXT))
            else:
                nodes.append(TextNode(fields[i], text_type))
    return nodes

def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        if len(images) == 0:
            nodes.append(node)
            continue
        text = node.text
        for image in images:
            parts = text.split(f"![{image[0]}]({image[1]})")
            for i in range(0, len(parts) - 1):
                if parts[i] != "":
                    nodes.append(TextNode(parts[i], TextType.TEXT))
                nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            text = parts[-1]
        if text != "":
            nodes.append(TextNode(text, TextType.TEXT))
    return nodes

def split_nodes_link(old_nodes):
    nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            nodes.append(node)
            continue
        text = node.text
        for link in links:
            parts = text.split(f"[{link[0]}]({link[1]})")
            for i in range(0, len(parts) - 1):
                nodes.append(TextNode(parts[i], TextType.TEXT))
                nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            text = parts[-1]
        if text != "":
            nodes.append(TextNode(text, TextType.TEXT))
    return nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    new_blocks = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        if block != "":
            new_blocks.append(block.strip())
    return new_blocks

def block_to_block_type(block):
    if block[0:3] == "```" and block[-3:] == "```":
        return block_type_code
    if block[0] == '#' and "# " in block[0:7]:
        return block_type_heading
    lines = block.split("\n")
    if all(line[0] == '>' for line in lines):
        return block_type_quote
    if all(line[0:2] == '* ' or line[0:2] == '- ' for line in lines):
        return block_type_ulist
    olist = True
    for i in range(len(lines)):
        if lines[i][0:3] != f"{i+1}. ":
            olist = False
    if olist:
        return block_type_olist
    return block_type_paragraph

def markdown_to_html_node(markdown):
    children = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        node = ""
        type = block_to_block_type(block)
        match type:
            case "heading":
                node = create_header_node(block)
            case "code":
                node = create_code_node(block)
            case "quote":
                node = create_quote_node(block)
            case "paragraph":
                node = create_paragraph_node(block)
            case "unordered_list":
                node = create_ulist_node(block)
            case "ordered_list":
                node = create_olist_node(block)
            case _:
                raise Exception("Invalid block type!")

        children.append(node)
    return ParentNode("div", children)
            
    
def text_to_children(text):
    nodes = text_to_textnodes(text)
    children = map(lambda a: text_node_to_html_node(a), nodes)
    return children

def create_header_node(block):
    count = 0
    for i in range(len(block)):
        if block[i] != "#":
            break
        count += 1
    if count == 0 or count > 6:
        raise Exception(f"Text is not a valid header: {block[:15]}")
    text = block[count + 1:]

    header_tag = f"h{count}"
    children = text_to_children(text)
    return ParentNode(header_tag, children)

def create_code_node(block):
    text = block.strip("```")
    tag = "code"
    children = text_to_children(text)
    return ParentNode(tag, children)

def create_quote_node(block):
    text = " ".join(map(lambda a: a[2:], block.split("\n")))
    tag = "blockquote"
    children = text_to_children(text.strip())
    return ParentNode(tag, children)

def create_paragraph_node(block):
    text = " ".join(block.split("\n"))
    tag = "p"
    children = text_to_children(text)
    return ParentNode(tag, children)

def create_ulist_node(block):
    lines = map(lambda a: a[2:], block.split("\n"))
    tag = "ul"
    items = []
    for line in lines:
        children = text_to_children(line)
        items.append(ParentNode("li", children))
    return ParentNode(tag, items)

def create_olist_node(block):
    lines = map(lambda a: a[3:], block.split("\n"))
    tag = "ol"
    items = []
    for line in lines:
        children = text_to_children(line)
        items.append(ParentNode("li", children))
    return ParentNode(tag, items)