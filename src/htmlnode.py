from functools import reduce


class HTMLNode:
    def __init__(self, value: str = None, tag: str = None, children: list = None, props: dict = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        result = ''
        if not isinstance(self.props, dict) or not self.props:
            return result
        for attr, value in self.props.items():
            result += f' {attr}="{value}"'
        return result

    def __eq__(self, other):
        return (
                isinstance(other, HTMLNode) and
                self.tag == other.tag and
                self.value == other.value and
                self.children == other.children and
                self.props == other.props
        )

    def __repr__(self):
        return f'HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})'


class LeafNode(HTMLNode):
    def __init__(self, value, tag=None, props=None):
        super().__init__(value, tag, None, props)

    def to_html(self):
        self_closing_html_tags = ['img']

        if not self.value and self.tag not in self_closing_html_tags:
            raise ValueError('LeafNode must have a value')
        if self.tag is None:
            return self.value
        if self.tag in self_closing_html_tags:
            return f'<{self.tag}{self.props_to_html()}>'

        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'

    def __repr__(self):
        return f'LeafNode({self.value}, {self.tag}, {self.props})'


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(None, tag, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError('ParentNode must have a tag')
        if self.children is None:
            raise ValueError('ParentNode must have children')
        if not isinstance(self.children, list):
            raise ValueError('Children must be a list object')

        def concat_children(a, b):
            return a + b.to_html()

        return f'<{self.tag}{self.props_to_html()}>{
            reduce(
                concat_children, self.children[1:], self.children[0].to_html()
            )
        }</{self.tag}>'
