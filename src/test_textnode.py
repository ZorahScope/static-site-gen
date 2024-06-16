import unittest
from textnode import (
    TextType,
    BlockType,
    TextNode,
    text_node_to_html_node,
    text_to_textnodes,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    extract_markdown_links,
    extract_markdown_images,
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node,
)

from htmlnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_eq_false(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq_false2(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node2", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.example.com")
        node2 = TextNode("This is a text node", TextType.TEXT, "https://www.example.com")
        self.assertEqual(node, node2)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")
        self.assertEqual(
            'TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")', repr(node)
        )

    def test_img_text_node_no_url(self):
        with self.assertRaises(ValueError) as context:
            TextNode("Image alt text", TextType.IMAGE, "")
        self.assertEqual(str(context.exception), "URL must be provided for image TextNode")

    def test_link_text_node_no_url(self):
        with self.assertRaises(ValueError) as context:
            TextNode("link example text", TextType.LINK, "")
        self.assertEqual(str(context.exception), "URL must be provided for link TextNode")


class TestTextToTextNodes(unittest.TestCase):

    def test_text_to_textnodes(self):
        markdown_text = ("This is **text** with an *italic* word and a `code block` and an "
                         "![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) "
                         "and a [link](https://boot.dev)")

        expected_output = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE,
                     "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(
            text_to_textnodes(markdown_text),
            expected_output,
        )


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_incorrect_text_type(self):
        incorrect_text_node = TextNode("abc", '1')
        with self.assertRaises(TypeError):
            text_node_to_html_node(incorrect_text_node)

    def test_self_closing_tag(self):
        image_text_node = TextNode("image alt text", 6, "img/example.png")
        img_leaf_node = text_node_to_html_node(image_text_node)
        self.assertEqual(
            img_leaf_node,
            LeafNode("", "img", {'alt': 'image alt text', 'src': 'img/example.png'}),
        )

    def test_str_text_type(self):
        test_text = TextNode("This is a text node", 'bold')
        self.assertEqual(
            text_node_to_html_node(test_text),
            LeafNode("This is a text node", "b")
        )

    def test_int_text_type(self):
        test_text = TextNode("This is a text node", 2)
        self.assertEqual(
            text_node_to_html_node(test_text),
            LeafNode("This is a text node", "b")
        )


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_expected_output(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_output = [
            TextNode("This is text with a ", TextType.TEXT, None),
            TextNode("code block", TextType.CODE, None),
            TextNode(" word", TextType.TEXT, None),
        ]
        self.assertEqual(new_nodes, expected_output)

    def test_expected_output_2(self):
        node = TextNode("This `first` and `second` examples.", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_output = [
            TextNode("This ", TextType.TEXT),
            TextNode("first", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.CODE),
            TextNode(" examples.", TextType.TEXT)
        ]
        self.assertEqual(new_nodes, expected_output)

    def test_without_delimiters_in_node(self):
        node = TextNode("This has no code blocks.", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_output = [
            TextNode("This has no code blocks.", TextType.TEXT)
        ]
        self.assertEqual(new_nodes, expected_output)

    def test_with_delimiters_at_start_and_end(self):
        node = TextNode("`code` block at start and end `example`.", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_output = [
            TextNode("code", TextType.CODE),
            TextNode(" block at start and end ", TextType.TEXT),
            TextNode("example", TextType.CODE),
            TextNode(".", TextType.TEXT)
        ]
        self.assertEqual(expected_output, new_nodes)

    def test_unbalanced_delimiters(self):
        node = TextNode("This is `unbalanced code block example.", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(str(context.exception), 'Odd or missing amount of delimiters')


class TestSplitNodesImage(unittest.TestCase):
    def test_single_image_node(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/"
            "course_assets/zjjcJKZ.png) and not another ",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", TextType.TEXT, None),
            TextNode("image", TextType.IMAGE,
                     "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"),
            TextNode(" and not another ", TextType.TEXT, None)
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_image_nodes(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/"
            "qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and another "
            "![second image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE,
                     "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image", TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png"
            ),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_missing_image_node(self):
        node = TextNode("This is text node without any images to extract from", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(new_nodes, [node])

    def test_empty_image_node(self):
        node = TextNode(
            "This is text with a ![]() and no other links",
            TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_image([node])
        self.assertEqual(str(context.exception), "URL must be provided for image TextNode")


class TestSplitNodesLink(unittest.TestCase):
    def test_single_link_node(self):
        node = TextNode(
            "This is text with a [link](https://www.example.com) and no other links",
            TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "https://www.example.com"),
            TextNode(" and no other links", TextType.TEXT, None),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_link_nodes(self):
        node = TextNode(
            "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)",
            TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "https://www.example.com"),
            TextNode(" and ", TextType.TEXT, None),
            TextNode("another", TextType.LINK, "https://www.example.com/another")
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_missing_link_node(self):
        node = TextNode("This is text node without any links to extract from", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(new_nodes, [node])

    def test_empty_link_node(self):
        node = TextNode(
            "This is text with a empty link []() and no other links",
            TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_link([node])
        self.assertEqual(str(context.exception), "URL must be provided for link TextNode")


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_img(self):
        text = ("This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/"
                "course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets"
                "/course_assets/dfsdkjfd.png)")

        expected_output = [
            ('image', 'https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png'),
            ('another', 'https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png')
        ]

        self.assertEqual(
            extract_markdown_images(text),
            expected_output
        )

    def test_markdown_without_img(self):
        text = "Lorem ipsum dolor sit amet consectetur adipiscing elit arcu bibendum etiam taciti"
        expected_output = []
        self.assertEqual(
            extract_markdown_images(text),
            expected_output
        )

    def test_img_regex_on_link_markdown(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        expected_output = []
        self.assertEqual(
            extract_markdown_images(text),
            expected_output
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_link(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"

        expected_output = [("link", "https://www.example.com"), ("another", "https://www.example.com/another")]

        self.assertEqual(
            extract_markdown_links(text),
            expected_output
        )

    def test_markdown_without_link(self):
        text = "Lorem ipsum dolor sit amet consectetur adipiscing elit arcu bibendum etiam taciti"
        expected_output = []
        self.assertEqual(
            extract_markdown_links(text),
            expected_output
        )

    def test_link_regex_on_img_markdown(self):
        text = ("This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/"
                "course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/"
                "qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)")
        expected_output = []
        self.assertEqual(
            extract_markdown_links(text),
            expected_output
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        block_markdown = ("# This is a heading\n\n"
                          "This is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n"
                          "* This is a list item\n* This is another list item\n"
                          )
        output = markdown_to_blocks(block_markdown)
        expected_output = [
            '# This is a heading',
            'This is a paragraph of text. It has some **bold** and *italic* words inside of it.',
            '* This is a list item\n* This is another list item'
        ]
        self.assertEqual(output, expected_output)

    def test_markdown_to_blocks_single_block(self):
        block_markdown = ("\n\n\n\n# This is a heading\n\n\n\n\n")
        output = markdown_to_blocks(block_markdown)
        expected_output = ['# This is a heading']
        self.assertEqual(output, expected_output)

    def test_markdown_to_blocks_empty(self):
        empty_markdown = ""
        with self.assertRaises(Exception) as context:
            markdown_to_blocks(empty_markdown)
        self.assertEqual(str(context.exception), 'Empty blocks: Invalid Markdown')


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type(self):
        heading_text = '###### This is a heading'
        code_block_text = '''
```
num1 = 1
num2 = 2
print(num1 + num2)
```                
'''
        quote_block_text = '''
> testing multi-line block quotes
> second line
> third line
> etc line        
'''
        undorderd_list_text = '''
- unordered
* list example
- third item
* last item        
'''
        ordered_list_text = '''
1. one
2. two
3. three
4. four        
'''
        paragraph_text = '''
“Pride is not the opposite of shame, but its source. True humility is the antidote to shame.” - Uncle Iroh
'''

        self.assertEqual(block_to_block_type(heading_text), BlockType.HEADING)
        self.assertEqual(block_to_block_type(code_block_text), BlockType.CODEBLOCK)
        self.assertEqual(block_to_block_type(quote_block_text), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(undorderd_list_text), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type(ordered_list_text), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type(paragraph_text), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid_markdown(self):
        heading_text = '####### This is a heading'
        code_block_text = '''
```
num1 = 1
num2 = 2
print(num1 + num2)
``                
'''
        quote_block_text = '''
> testing multi-line block quotes
> second line
 third line
> etc line        
'''
        undorderd_list_text = '''
- unordered
 list example
- third item
* last item        
'''
        ordered_list_text = '''
1. one
2. two
8. three
4. four        
'''
        paragraph_text = '''
“Pride is not the opposite of shame, but its source. True humility is the antidote to shame.” - Uncle Iroh
'''

        self.assertEqual(block_to_block_type(heading_text), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type(code_block_text), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type(quote_block_text), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type(undorderd_list_text), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type(ordered_list_text), BlockType.PARAGRAPH)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_markdown_to_html_node(self):
        markdown_doc = (
"""
### This is a heading

#### Second heading

```
num1 = 1
num2 = 2
print(num1 + num2)
```

> this is block
> quote
> third line

1. **first**
2. second
3. third

* example `unordered` list
- testing *list*
* third item

Lorem ipsum **dolor** sit amet [consectetur](www.example.com) adipiscing ![invalid image](img/yeahno.jpg) nascetur 
fusce dis, blandit nulla risus magna cursus himenaeos commodo eu urna, erat condimentum sem facilisi fames eros natoque 
mus nostra. Velit hendrerit platea auctor est nascetur, et blandit primis suscipit aliquet vestibulum

"""
        )
        
        expected_output = ('''<div><h3>This is a heading</h3><h4>Second heading</h4><pre><code>num1 = 1
num2 = 2
print(num1 + num2)</code></pre><blockquote>this is block
quote
third line</blockquote><ol><li><b>first</b></li><li>second</li><li>third</li></ol><ul><li>example <code>unordered</code> list</li><li>testing <i>list</i></li><li>third item</li></ul><p>Lorem ipsum <b>dolor</b> sit amet <a href="www.example.com">consectetur</a> adipiscing <img src="img/yeahno.jpg" alt="invalid image"> nascetur 
fusce dis, blandit nulla risus magna cursus himenaeos commodo eu urna, erat condimentum sem facilisi fames eros natoque 
mus nostra. Velit hendrerit platea auctor est nascetur, et blandit primis suscipit aliquet vestibulum</p></div>''')
        
        actual_output = markdown_to_html_node(markdown_doc).to_html()
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
