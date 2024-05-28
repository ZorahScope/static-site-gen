import unittest
from htmlnode import HTMLNode


class TestHtmlNode(unittest.TestCase):
    def test_eq(self):
        html_node = HTMLNode()
        html_node2 = HTMLNode()
        self.assertEqual(html_node, html_node2)

    def test_props(self):
        html_node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(
            html_node.props_to_html(),
            '''href="https://www.google.com" target="_blank" ''',
        )


if __name__ == '__main__':
    unittest.main()
