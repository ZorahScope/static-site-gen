from enum import Enum
from htmlnode import LeafNode
import re


class TextNode:
    def __init__(self, text, text_type, url=None):

        if text_type == TextType.LINK and (url is None or url == ""):
            raise ValueError("URL must be provided for link TextNode")
        if text_type == TextType.IMAGE and (url is None or url == ""):
            raise ValueError("URL must be provided for image TextNode")

        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
                isinstance(other, TextNode) and
                self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url
        )

    def __repr__(self):
        if self.url is None:
            return f'TextNode("{self.text}", {self.text_type}, None)'
        return f'TextNode("{self.text}", {self.text_type}, "{self.url}")'


class TextType(Enum):
    TEXT = 1
    BOLD = 2
    ITALIC = 3
    CODE = 4
    LINK = 5
    IMAGE = 6

    def __eq__(self, other):
        if isinstance(other, TextType):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            return self.name.lower() == other.lower()
        return super().__eq__(other)


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(text_node.text)
        case TextType.BOLD:
            return LeafNode(text_node.text, "b")
        case TextType.ITALIC:
            return LeafNode(text_node.text, "i")
        case TextType.CODE:
            return LeafNode(text_node.text, "code")
        case TextType.LINK:
            return LeafNode(text_node.text, "a", {'href': text_node.url})
        case TextType.IMAGE:
            return LeafNode('', "img", {'src': text_node.url, 'alt': text_node.text})
        case _:
            raise TypeError(f'Invalid text type')


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    def validate_delimiter_balance(node):
        delimiter_count = node.text.count(delimiter)
        if delimiter_count % 2 != 0:
            raise Exception('Odd or missing amount of delimiters')

    def parse_old_nodes(node):
        validate_delimiter_balance(node)
        new_text_nodes = node.text.split(delimiter)
        result = []

        for idx, text in enumerate(new_text_nodes):
            if idx % 2 == 0:  # outside of delimiter
                result.append(TextNode(text, TextType.TEXT))
            if idx % 2 == 1:  # Inside of delimiter
                result.append(TextNode(text, text_type))
        return result

    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
        else:
            new_nodes.extend(parse_old_nodes(old_node))
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    delimiter_template = "![{}]({})"

    def split_nodes(node: TextNode):
        images = extract_markdown_images(node.text)
        if images:
            split_text = node.text.split(delimiter_template.format(images[0][0], images[0][1]))
            first_string = split_text.pop(0)
            first_img = images.pop(0)
            new_nodes.append(TextNode(first_string, TextType.TEXT))
            new_nodes.append(TextNode(text=first_img[0], text_type=TextType.IMAGE, url=first_img[1]))

            if split_text[0]:
                remainder = TextNode(split_text[-1], TextType.TEXT)
                split_nodes(remainder)
            return
        else:
            new_nodes.append(node)

    for old_node in old_nodes:
        split_nodes(old_node)
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    delimiter_template = "[{}]({})"

    def split_nodes(node: TextNode):
        links = extract_markdown_links(node.text)
        if links:
            split_text = node.text.split(delimiter_template.format(links[0][0], links[0][1]))
            first_string = split_text.pop(0)
            first_link = links.pop(0)
            new_nodes.append(TextNode(first_string, TextType.TEXT))
            new_nodes.append(TextNode(text=first_link[0], text_type=TextType.LINK, url=first_link[1]))

            if split_text[0]:
                remainder = TextNode(split_text[-1], TextType.TEXT)
                split_nodes(remainder)
            return
        else:
            new_nodes.append(node)

    for old_node in old_nodes:
        split_nodes(old_node)
    return new_nodes


def extract_markdown_images(text):
    img_regex = re.compile(r"!\[(.*?)]\((.*?)\)")
    return re.findall(img_regex, text)


def extract_markdown_links(text):
    link_regex = re.compile(r"[^!]\[(.*?)]\((.*?)\)")
    return re.findall(link_regex, text)
