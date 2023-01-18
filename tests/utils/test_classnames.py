from hotmetal.utils.classnames import classnames
from unittest import TestCase


class ClassnamesTestCase(TestCase):
    def test_dict_keys_with_truthy_values(self):
        self.assertEqual(
            classnames({"a": True, "b": False, "c": 0, "d": None, "e": 1}),
            "a e",
        )

    def test_joins_multiple_classnames_and_ignore_falsy_values(self):
        self.assertEqual(
            classnames("a", 0, None, True, 1, "b"),
            "a 1 b",
        )

    def test_heterogenous_args(self):
        self.assertEqual(
            classnames({"a": True}, "b", 0),
            "a b",
        )

    def test_result_trimmed(self):
        self.assertEqual(
            classnames("", "b", {}, ""),
            "b",
        )

    def test_returns_empty_string_for_empty_args(self):
        self.assertEqual(
            classnames({}),
            "",
        )

    def test_supports_list_of_classnames(self):
        self.assertEqual(
            classnames(["a", "b"]),
            "a b",
        )

    def test_supports_sets_of_classnames(self):
        self.assertTrue(
            classnames({"a", "b"}) in {"a b", "b a"},
        )

    def test_joins_lists_args_with_string_args(self):
        self.assertEqual(
            classnames(["a", "b"], "c"),
            "a b c",
        )
        self.assertEqual(
            classnames("c", ["a", "b"]),
            "c a b",
        )

    def test_handles_lists_that_include_falsy_and_true_values(self):
        self.assertEqual(
            classnames(["a", 0, None, False, True, "b"]),
            "a b",
        )

    def test_handles_lists_that_include_lists(self):
        self.assertEqual(
            classnames(["a", ["b", "c"]]),
            "a b c",
        )

    def test_handles_lists_that_include_dicts(self):
        self.assertEqual(
            classnames(["a", {"b": True, "c": False}]),
            "a b",
        )

    def test_handles_nested_lists_that_include_empty_nested_lists(self):
        self.assertEqual(
            classnames(["a", [[]]]),
            "a",
        )
