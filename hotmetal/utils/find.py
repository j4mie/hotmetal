TAG, ATTRS, CHILDREN = 0, 1, 2


def is_text_node(node):
    return isinstance(node, str)


def is_context_node(node):
    return callable(node)


def is_tree_node(node):
    return not_(or_(is_text_node, is_context_node))(node)


def tag_is(tag):
    return and_(is_tree_node, lambda node: node[TAG] == tag)


def id_is(id):
    return has_attr_with_value("id", id)


def attr_value_matches(attr, predicate):
    return and_(has_attr(attr), lambda node: predicate(node[ATTRS][attr]))


def has_class(cls):
    return attr_value_matches("class", lambda attr_value: cls in attr_value.split(" "))


def has_attr(attr):
    return and_(is_tree_node, lambda node: attr in node[ATTRS])


def has_attr_with_value(attr, value):
    return attr_value_matches(attr, lambda attr_value: attr_value == value)


def text_contains(text):
    return and_(is_text_node, lambda node: text in node)


def any_immediate_child_matches(predicate):
    return lambda node: any(predicate(child) for child in node[CHILDREN])


def or_(*predicates):
    return lambda node: any(predicate(node) for predicate in predicates)


def and_(*predicates):
    return lambda node: all(predicate(node) for predicate in predicates)


def not_(predicate):
    return lambda node: not predicate(node)


def find(nodes, predicate):
    for node in nodes:
        yield from [node] if predicate(node) else []
        yield from find(node[CHILDREN], predicate) if is_tree_node(node) else []
