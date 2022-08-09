from hotmetal.utils.find import (
    and_,
    CHILDREN,
    direct_children,
    find,
    has_attr,
    has_attr_with_value,
    has_class,
    id_is,
    not_,
    or_,
    tag_is,
    text_contains,
)
from unittest import TestCase


class FindTestCase(TestCase):
    def test_basic_find(self):
        nodes = [("div", {}, [])]
        predicate = tag_is("div")
        result = [*find(nodes, predicate)]
        self.assertEqual(result, [("div", {}, [])])

    def test_no_match(self):
        nodes = [("div", {}, [])]
        predicate = tag_is("a")
        result = [*find(nodes, predicate)]
        self.assertEqual(result, [])

    def test_find_in_children(self):
        nodes = [("div", {}, [("h1", {}, []), ("p", {}, [])])]
        predicate = tag_is("p")
        result = [*find(nodes, predicate)]
        self.assertEqual(result, [("p", {}, [])])


class NodePredicatesIgnoreTextNodesTestCase(TestCase):
    def test_basic_find_with_text_node(self):
        nodes = [("div", {"id": "test"}, ["hello world"])]
        predicate = id_is("test")
        result = [*find(nodes, predicate)]
        self.assertEqual(result, [("div", {"id": "test"}, ["hello world"])])


class NodePredicatesIgnoreFunctionNodesTestCase(TestCase):
    def test_basic_find_with_function_node(self):
        nodes = [("div", {"id": "test"}, [lambda _: "hello world"])]
        predicate = id_is("test")
        result = [*find(nodes, predicate)]
        self.assertEqual(result, nodes)


class TagIsTestCase(TestCase):
    def test_match(self):
        node = ("div", {}, [])
        self.assertIs(tag_is("div")(node), True)

    def test_no_match(self):
        node = ("div", {}, [])
        self.assertIs(tag_is("p")(node), False)


class IDIsTestCase(TestCase):
    def test_match(self):
        node = ("div", {"id": "test"}, [])
        self.assertIs(id_is("test")(node), True)

    def test_no_match(self):
        node = ("div", {"id": "nope"}, [])
        self.assertIs(id_is("test")(node), False)


class HasClassTestCase(TestCase):
    def test_match(self):
        node = ("div", {"class": "foo bar baz"}, [])
        self.assertIs(has_class("bar")(node), True)

    def test_no_match(self):
        node = ("div", {"class": "foo bla baz"}, [])
        self.assertIs(has_class("bar")(node), False)


class HasAttrTestCase(TestCase):
    def test_match(self):
        node = ("div", {"yep": "yep"}, [])
        self.assertIs(has_attr("yep")(node), True)

    def test_no_match(self):
        node = ("div", {"nope": "nope"}, [])
        self.assertIs(has_attr("yep")(node), False)


class HasAttrWithValueTestCase(TestCase):
    def test_match(self):
        node = ("div", {"yep": "oh yep"}, [])
        self.assertIs(has_attr_with_value("yep", "oh yep")(node), True)

    def test_no_match(self):
        node = ("div", {"nope": "nope"}, [])
        self.assertIs(has_attr_with_value("yep", "nope")(node), False)
        self.assertIs(has_attr_with_value("nope", "yep")(node), False)


class TextContainsTestCase(TestCase):
    def test_match(self):
        node = "this is a text node"
        self.assertIs(text_contains("text")(node), True)

    def test_no_match(self):
        node = "this is a text node"
        self.assertIs(text_contains("nope")(node), False)


class OrTestCase(TestCase):
    def test_match(self):
        node = ("div", {"class": "foo bar baz"}, [])
        self.assertIs(or_(has_class("bar"), id_is("test"))(node), True)

        node = ("div", {"id": "test"}, [])
        self.assertIs(or_(has_class("bar"), id_is("test"))(node), True)

        node = ("div", {"class": "foo bar baz", "id": "test"}, [])
        self.assertIs(or_(has_class("bar"), id_is("test"))(node), True)

    def test_no_match(self):
        node = ("div", {"class": "foo bla baz", "id": "nope"}, [])
        self.assertIs(or_(has_class("bar"), id_is("test"))(node), False)


class AndTestCase(TestCase):
    def test_match(self):
        node = ("div", {"class": "foo bar baz", "id": "test"}, [])
        self.assertIs(and_(has_class("bar"), id_is("test"))(node), True)

    def test_no_match(self):
        node = ("div", {"class": "foo bar baz"}, [])
        self.assertIs(and_(has_class("bar"), id_is("test"))(node), False)

        node = ("div", {"id": "test"}, [])
        self.assertIs(and_(has_class("bar"), id_is("test"))(node), False)

        node = ("div", {"class": "foo bla baz", "id": "nope"}, [])
        self.assertIs(and_(has_class("bar"), id_is("test"))(node), False)


class NotTestCase(TestCase):
    def test_match(self):
        node = ("div", {}, [])
        self.assertIs(not_(tag_is("p"))(node), True)

    def test_no_match(self):
        node = ("div", {}, [])
        self.assertIs(not_(tag_is("div"))(node), False)


class DirectChildrenTestCase(TestCase):
    def test_match(self):
        nodes = [("div", {}, [("div", {"id": "test"}, [])]), ("div", {}, [])]
        predicate = direct_children(id_is("test"))
        result = [*find(nodes, predicate)]
        self.assertEqual(result, [("div", {}, [("div", {"id": "test"}, [])])])


def example_page(title):
    return (
        "html",
        {},
        [
            ("head", {}, [("title", {}, ["Test Page"])]),
            (
                "body",
                {},
                [
                    (
                        "div",
                        {"class": "wrapper"},
                        [
                            (
                                "section",
                                {"id": "header"},
                                [
                                    ("h1", {}, [title]),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    )


class ExampleComponentTestCase(TestCase):
    def test_title(self):
        page = example_page(title="Test Page")
        [header] = find([page], id_is("header"))
        [h1] = find([header], tag_is("h1"))
        [title] = h1[CHILDREN]
        self.assertEqual(title, "Test Page")
