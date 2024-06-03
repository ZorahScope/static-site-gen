import unittest
from textnode import TextType, TextNode, text_node_to_html_node, split_nodes_delimiter
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
        node = TextNode("This is a text node", 1, "https://www.boot.dev")
        self.assertEqual(
            'TextNode(This is a text node, 1, https://www.boot.dev)', repr(node)
        )

    def test_img_text_node_no_url(self):
        with self.assertRaises(ValueError) as context:
            TextNode("Image alt text", TextType.IMAGE, "")
        self.assertEqual(str(context.exception), "URL must be provided for image TextNode")

    def test_link_text_node_no_url(self):
        with self.assertRaises(ValueError) as context:
            TextNode("link example text", TextType.LINK, "")
        self.assertEqual(str(context.exception), "URL must be provided for link TextNode")


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
            TextNode("", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" block at start and end ", TextType.TEXT),
            TextNode("example", TextType.CODE),
            TextNode(".", TextType.TEXT)
        ]
        self.assertEqual(new_nodes, expected_output)

    def test_unbalanced_delimiters(self):
        node = TextNode("This is `unbalanced code block example.", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(str(context.exception), 'Odd or missing amount of delimiters')


if __name__ == '__main__':
    unittest.main()
