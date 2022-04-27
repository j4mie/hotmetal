from hotmetal import render, safe, VOID_ELEMENTS
from textwrap import dedent
from unittest import TestCase


class EmptyNodeTestCase(TestCase):
    def test_empty_node(self):
        node = ("", {}, [])
        self.assertEqual(render(node), "")

    def test_falsy_node(self):
        for falsy in [None, False, "", [], {}, ()]:
            self.assertEqual(render(falsy), "")


class SimpleNodeTestCase(TestCase):
    def test_div(self):
        node = ("div", {}, [])
        self.assertEqual(render(node), "<div></div>")


class SelfClosingNodeTestCase(TestCase):
    def test_void_elements(self):
        for tag in VOID_ELEMENTS:
            node = (tag, {}, [])
            self.assertEqual(render(node), f"<{tag} />")


class AttributeTestCase(TestCase):
    def test_attrs(self):
        node = ("div", {"class": "some-class"}, [])
        self.assertEqual(render(node), '<div class="some-class"></div>')

    def test_empty_attr(self):
        """
        "The value, along with the "=" character, can be omitted altogether
        if the value is the empty string."
        - https://html.spec.whatwg.org/#a-quick-introduction-to-html
        """
        node = ("input", {"disabled": ""}, [])
        self.assertEqual(render(node), "<input disabled />")


class TestNodeTestCase(TestCase):
    def test_text(self):
        node = "test"
        self.assertEqual(render(node), "test")


class ChildrenTestCase(TestCase):
    def test_text_child(self):
        node = ("p", {}, ["test"])
        self.assertEqual(render(node), "<p>test</p>")

    def test_nested_children(self):
        node = ("p", {}, [("strong", {}, "test")])
        self.assertEqual(render(node), "<p><strong>test</strong></p>")

    def test_multiple_children(self):
        node = ("p", {}, [("strong", {}, "test1"), ("em", {}, ["test2"])])
        self.assertEqual(render(node), "<p><strong>test1</strong><em>test2</em></p>")

    def test_mixed_node_and_text_children(self):
        node = ("p", {}, [("strong", {}, "test1"), "hello"])
        self.assertEqual(render(node), "<p><strong>test1</strong>hello</p>")


class EscapingTestCase(TestCase):
    def test_text_escaping(self):
        node = ("p", {}, "<script></script>")
        self.assertEqual(render(node), "<p>&lt;script&gt;&lt;/script&gt;</p>")

    def test_tag_escaping(self):
        node = ("alert('hi')", {}, [])
        self.assertEqual(
            render(node), "<alert(&#x27;hi&#x27;)></alert(&#x27;hi&#x27;)>"
        )

    def test_attr_value_escaping(self):
        node = ("div", {"onclick": "alert('hi')"}, [])
        self.assertEqual(render(node), '<div onclick="alert(&#x27;hi&#x27;)"></div>')

    def test_attr_key_escaping(self):
        node = ("div", {"on('click')": "hi"}, [])
        self.assertEqual(render(node), '<div on(&#x27;click&#x27;)="hi"></div>')

    def test_safe(self):
        node = ("div", {}, [safe("<p>hello</p>")])
        self.assertEqual(render(node), "<div><p>hello</p></div>")


class IndentationTestCase(TestCase):
    def test_indentation_2(self):
        node = ("div", {"class": "test"}, [("div", {}, ["hello"])])
        self.assertEqual(
            render(node, indent=2),
            dedent(
                """\
                <div class="test">
                  <div>
                    hello
                  </div>
                </div>"""
            ),
        )

    def test_indentation_4(self):
        node = ("div", {"class": "test"}, [("div", {}, ["hello"])])
        self.assertEqual(
            render(node, indent=4),
            dedent(
                """\
                <div class="test">
                    <div>
                        hello
                    </div>
                </div>"""
            ),
        )

    def test_indentation_with_root_fragment(self):
        node = (
            "",
            {},
            [
                ("div", {}, ["hello1"]),
                ("div", {}, ["hello2"]),
            ],
        )
        self.assertEqual(
            render(node, indent=2),
            dedent(
                """\
                <div>
                  hello1
                </div>
                <div>
                  hello2
                </div>"""
            ),
        )


class ContextTestCase(TestCase):
    def test_context(self):
        node = lambda context: ("div", {}, [context["message"]])  # noqa: E731
        self.assertEqual(render(node, context={"message": "test"}), "<div>test</div>")
