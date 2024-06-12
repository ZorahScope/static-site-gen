from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode
import re


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


class BlockType(Enum):
    PARAGRAPH = 1
    HEADING = 2
    CODEBLOCK = 3
    QUOTE = 4
    UNORDERED_LIST = 5
    ORDERED_LIST = 6

    def __eq__(self, other):
        if isinstance(other, BlockType):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            return self.name.lower() == other.lower()
        return super().__eq__(other)


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):

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


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
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


def text_to_textnodes(text: str) -> list[TextNode]:
    node = TextNode(text, TextType.TEXT)
    temp = split_nodes_delimiter([node], '**', TextType.BOLD)
    temp1 = split_nodes_delimiter(temp, '*', TextType.ITALIC)
    temp2 = split_nodes_delimiter(temp1, '`', TextType.CODE)
    temp3 = split_nodes_link(temp2)
    return split_nodes_image(temp3)


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    def validate_delimiter_balance(node: TextNode) -> None:
        delimiter_count = node.text.count(delimiter)
        if delimiter_count % 2 != 0:
            raise Exception('Odd or missing amount of delimiters')

    def parse_old_nodes(node: TextNode) -> list[TextNode]:
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

    remove_empty_values = lambda node: node.text != ''
    return list(filter(remove_empty_values, new_nodes))


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    delimiter_template = "![{}]({})"

    def split_nodes(node: TextNode) -> None:
        images = extract_markdown_images(node.text)
        if images:
            split_text = node.text.split(delimiter_template.format(images[0][0], images[0][1]), maxsplit=1)
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


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    delimiter_template = "[{}]({})"

    def split_nodes(node: TextNode) -> None:
        links = extract_markdown_links(node.text)
        if links:
            split_text = node.text.split(delimiter_template.format(links[0][0], links[0][1]), maxsplit=1)
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


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    img_regex = re.compile(r"!\[(.*?)]\((.*?)\)")
    return re.findall(img_regex, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    link_regex = re.compile(r"[^!]\[(.*?)]\((.*?)\)")
    return re.findall(link_regex, text)


def markdown_to_blocks(markdown: str) -> list[str]:
    block_regex = re.compile(r"\n{2,}")
    blocks = re.split(block_regex, markdown)
    while '' in blocks:
        blocks.remove('')
    if blocks == []:
        raise Exception('Empty blocks: Invalid Markdown')

    return list(map(lambda x: x.strip(), blocks))


def block_to_block_type(block: str) -> BlockType:
    header_regex = re.compile(r"^(#{1,6}) (?!#).*$")
    code_regex = re.compile(r"`{3}[\s\S]+?`{3}")
    quote_block_regex = re.compile(r"^>.*(\n>.*)*", re.MULTILINE)
    unordered_list_regex = re.compile(r"^[*-] .*(\n[*-] .*)*$", re.MULTILINE)
    ordered_list_regex = re.compile(r"^\d\. .*(\n\d\. .*)*$", re.MULTILINE)

    def contains_pattern(pattern: re.Pattern, block: str) -> bool:
        search_result = re.search(pattern, block)
        return bool(search_result)

    def is_valid_pattern(pattern: re.Pattern, block: str) -> bool:
        check_line = lambda block: contains_pattern(pattern, block)
        block_list = block.strip().splitlines()
        if pattern == ordered_list_regex:
            return all(list(map(check_line, block_list))) and is_valid_ordered_list(block)
        return all(list(map(check_line, block_list)))

    def is_valid_ordered_list(block: str) -> bool:
        result = []
        split_ordered_list = block.strip().splitlines()
        ordered_list = list(enumerate(split_ordered_list, start=1))
        valid_list_item = lambda li: li[0] == int(li[1][0])
        return all(list(map(valid_list_item, ordered_list)))

    if contains_pattern(header_regex, block):
        return BlockType.HEADING
    if contains_pattern(code_regex, block):
        return BlockType.CODEBLOCK
    if contains_pattern(quote_block_regex, block) and is_valid_pattern(quote_block_regex, block):
        return BlockType.QUOTE
    if contains_pattern(unordered_list_regex, block) and is_valid_pattern(unordered_list_regex, block):
        return BlockType.UNORDERED_LIST
    if contains_pattern(ordered_list_regex, block) and is_valid_pattern(ordered_list_regex, block):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str) -> ParentNode:
    def header_block_to_html_node(markdown: str) -> ParentNode:
        header_count = markdown.count('#')
        header_text = markdown.lstrip('# ')
        html_node = ParentNode(
            f"h{header_count}",
            [LeafNode(header_text)]
        )
        return html_node

    def code_block_to_html_node(markdown: str) -> ParentNode:
        raw_code = markdown.strip('`\n ')  # removes sorrounding backticks, whitespace and new lines
        code_leaf_node = LeafNode(raw_code, "code")
        html_node = ParentNode(
            "pre",
            [code_leaf_node]
        )
        return html_node

    def quote_block_to_html_node(markdown: str) -> ParentNode:
        strip_quote_markdown = lambda qt: qt.lstrip('> ')
        quote_text = markdown.splitlines()
        stripped_quote_text = '\n'.join(list(map(strip_quote_markdown, quote_text)))
        text_nodes = text_to_textnodes(stripped_quote_text)
        quote_leaf_nodes = list(map(text_node_to_html_node, text_nodes))
        html_node = ParentNode(
            "blockquote",
            quote_leaf_nodes
        )
        return html_node

    def ordered_list_block_to_html_node(markdown: str) -> ParentNode:
        remove_number = lambda li: li.split(' ', maxsplit=1)[1]
        markdown_list = list(map(remove_number, markdown.splitlines()))
        list_nodes = []
        for li in markdown_list:
            leaf_nodes = list(map(text_node_to_html_node, text_to_textnodes(li)))
            node = ParentNode(
                "li",
                leaf_nodes
            )
            list_nodes.append(node)

        html_list_node = ParentNode(
            "ol",
            list_nodes
        )
        return html_list_node

    def unordered_list_block_to_html_node(markdown: str) -> ParentNode:
        remove_bullet = lambda li: li.split(' ', maxsplit=1)[1]
        markdown_list = list(map(remove_bullet, markdown.splitlines()))
        list_nodes = []
        for li in markdown_list:
            leaf_nodes = list(map(text_node_to_html_node, text_to_textnodes(li)))
            node = ParentNode(
                "li",
                leaf_nodes
            )
            list_nodes.append(node)

        html_list_node = ParentNode(
            "ul",
            list_nodes
        )
        return html_list_node

    def paragraph_block_to_html_node(markdown: str) -> ParentNode:
        leaf_nodes = list(map(text_node_to_html_node, text_to_textnodes(markdown)))
        html_node = ParentNode(
            'p',
            leaf_nodes
        )

        return html_node

    def markdown_router(block: str, type: BlockType) -> ParentNode:
        match type:
            case BlockType.HEADING:
                return header_block_to_html_node(block)
            case BlockType.CODEBLOCK:
                return code_block_to_html_node(block)
            case BlockType.QUOTE:
                return quote_block_to_html_node(block)
            case BlockType.ORDERED_LIST:
                return ordered_list_block_to_html_node(block)
            case BlockType.UNORDERED_LIST:
                return unordered_list_block_to_html_node(block)
            case BlockType.PARAGRAPH:
                return paragraph_block_to_html_node(block)

    html_nodes = []
    blocks = markdown_to_blocks(markdown)

    for block in blocks:
        block_type = block_to_block_type(block)
        html_nodes.append(markdown_router(block, block_type))

    return ParentNode(
        'div',
        html_nodes,
    ).to_html()
