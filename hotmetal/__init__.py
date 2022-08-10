import html

__version__ = "0.0.1"

# https://html.spec.whatwg.org/#void-elements
VOID_ELEMENTS = set(
    "area,base,br,col,embed,hr,img,input,link,meta,param,source,track,wbr".split(",")
)


class safe(str):
    pass


def esc(string):
    return string if isinstance(string, safe) else safe(html.escape(string))


def _render(*, tree_or_text_or_callable, context, indent, level, is_root):
    breaker = "\n" if indent else ""
    indenter = " " * indent * level
    tree_or_text = (
        tree_or_text_or_callable(context)
        if callable(tree_or_text_or_callable)
        else tree_or_text_or_callable
    )
    if not tree_or_text:
        return ""
    if isinstance(tree_or_text, str):
        return f"{breaker}{indenter}{esc(tree_or_text)}"
    tag, attrs, children = tree_or_text
    breaker = breaker if tag else ""
    attrs = (
        (
            " "
            + " ".join(
                esc(k) if v == "" else f'{esc(k)}="{esc(v)}"' for k, v in attrs.items()
            )
        )
        if attrs
        else ""
    )
    is_void = tag.lower() in VOID_ELEMENTS
    self_closer = " /" if is_void else ""
    opener = f"<{esc(tag)}{attrs}{self_closer}>" if tag else ""
    closer = f"</{esc(tag)}>" if (tag and not is_void) else ""
    next_level = level + 1 if tag else level
    children = "".join(
        _render(
            tree_or_text_or_callable=child,
            context=context,
            indent=indent,
            level=next_level,
            is_root=False,
        )
        for child in children
    )
    contents = f"{children}{breaker}{indenter}" if children else ""
    rendered = f"{breaker}{indenter}{opener}{contents}{closer}"
    return rendered.strip("\n") if is_root else rendered


def render(node, context=None, indent=0):
    return _render(
        tree_or_text_or_callable=node,
        context=context or {},
        indent=indent,
        level=0,
        is_root=True,
    )
