def false_if_text(predicate):
    return lambda node: not isinstance(node, str) and predicate(node)


def tag_is(tag):
    return false_if_text(lambda node: node[0] == tag)


def id_is(id):
    return false_if_text(lambda node: node[1].get("id") == id)


def has_class(cls):
    return false_if_text(lambda node: cls in node[1].get("class", "").split(" "))


def text_contains(text):
    return lambda node: isinstance(node, str) and text in node


def or_(*predicates):
    return lambda node: any(predicate(node) for predicate in predicates)


def and_(*predicates):
    return lambda node: all(predicate(node) for predicate in predicates)


def not_(predicate):
    return lambda node: not predicate(node)


def find(nodes, predicate):
    for node in nodes:
        yield from [node] if predicate(node) else []
        yield from [child for child in node[2] if predicate(child)]
