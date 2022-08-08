from hotmetal.utils.find import and_, find, has_class, id_is, not_, or_, tag_is
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
