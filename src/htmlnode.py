class HTMLNode:
    def __init__(self, value=None, tag=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if not isinstance(self.props, dict) or not self.props:
            raise ValueError("Invalid or empty properties")
        result = ''
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
        if not self.value:
            raise ValueError('LeafNode must have a value')
        if self.tag is None:
            return self.value

        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
