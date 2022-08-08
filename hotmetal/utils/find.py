def is_tree_node(node):
    return not isinstance(node, str) and not callable(node)


def tree_node_only(predicate):
    return lambda node: is_tree_node(node) and predicate(node)


def tag_is(tag):
    return tree_node_only(lambda node: node[0] == tag)


def id_is(id):
    return tree_node_only(lambda node: node[1].get("id") == id)


def has_class(cls):
    return tree_node_only(lambda node: cls in node[1].get("class", "").split(" "))


def text_contains(text):
    return lambda node: isinstance(node, str) and text in node


def direct_children(predicate):
    return lambda node: any(predicate(child) for child in node[2])


def or_(*predicates):
    return lambda node: any(predicate(node) for predicate in predicates)


def and_(*predicates):
    return lambda node: all(predicate(node) for predicate in predicates)


def not_(predicate):
    return lambda node: not predicate(node)


def find(nodes, predicate):
    for node in nodes:
        yield from [node] if predicate(node) else []
        yield from find(node[2], predicate) if is_tree_node(node) else []
