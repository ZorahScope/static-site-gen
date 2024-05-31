import unittest
from textnode import TextType, TextNode, text_node_to_html_node
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


if __name__ == '__main__':
    unittest.main()
