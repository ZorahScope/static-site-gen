class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        result = ''
        for attr, value in self.props.items():
            result += f'{attr}="{value}" '
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