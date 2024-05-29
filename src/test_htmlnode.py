import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHtmlNode(unittest.TestCase):
    def test_eq(self):
        html_node = HTMLNode()
        html_node2 = HTMLNode()
        self.assertEqual(html_node, html_node2)

    def test_props_to_html(self):
        html_node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(
            html_node.props_to_html(),
            ''' href="https://www.google.com" target="_blank"''',
        )

    def test_props_to_html_if_empty(self):
        html_node = HTMLNode(props={})
        self.assertEqual(
            html_node.props_to_html(),
            ''
        )


class TestLeafNode(unittest.TestCase):
    def test_to_html_empty_args_raises_exception(self):
        self.assertRaises(TypeError, LeafNode)

    def test_to_html_falsy_value(self):
        with self.assertRaises(ValueError) as context:
            LeafNode('').to_html()
        self.assertEqual(str(context.exception), 'LeafNode must have a value')

    def test_to_html_empty_tag(self):
        test_leaf = LeafNode('abc')
        self.assertEqual(test_leaf.to_html(), 'abc')

    def test_to_html(self):
        test_leaf = LeafNode('abc', 'a', props={"href": "https://www.example.com", "target": "_blank"})
        self.assertEqual(test_leaf.to_html(), '<a href="https://www.example.com" target="_blank">abc</a>')


class TestParentNode(unittest.TestCase):
    def test_to_html(self):
        test_parent = ParentNode(
            "p",
            [
                LeafNode(tag="b", value="Bold text"),
                LeafNode(tag=None, value="Normal text"),
                LeafNode(tag="i", value="italic text"),
                LeafNode(tag=None, value="Normal text"),
            ],
        )
        self.assertEqual(
            test_parent.to_html(),
            '<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>'
        )

    def test_to_html_single_child(self):
        test_parent = ParentNode(
            "p",
            [
                LeafNode(tag="b", value="Bold text"),
            ],
        )
        self.assertEqual(test_parent.to_html(), '<p><b>Bold text</b></p>')

    def test_to_html_nested_child(self):
        test_parent = ParentNode(
            "ol",
            [
                LeafNode(tag="li", value="list item 1"),
                LeafNode(tag="li", value="list item 2"),
                ParentNode(
                    "ol",
                    [
                        LeafNode(tag="li", value="nested list item 3"),
                    ],
                )
            ]
        )
        self.assertEqual(
            test_parent.to_html(),
            '<ol><li>list item 1</li><li>list item 2</li><ol><li>nested list item 3</li></ol></ol>'
        )


if __name__ == '__main__':
    unittest.main()
