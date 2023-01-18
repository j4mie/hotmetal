# hotmetal

**A tiny HTML generator**

## Installation

Install from PyPI

    pip install hotmetal

## What is hotmetal?

`hotmetal` is a tiny library that lets you generate HTML directly from Python primitive data structures without using any sort of text-based template language. It is an alternative to [Jinja](https://jinja.palletsprojects.com/), [Django templates](https://docs.djangoproject.com/en/4.0/topics/templates/), etc. It is loosely inspired by ideas from [React](https://reactjs.org/), [Mithril](https://mithril.js.org/vnodes.html) and other JavaScript libraries. It is also similar to [Hyperpython](https://github.com/ejplatform/hyperpython), but it's even simpler. It attempts to stay as close as possible to [the HTML spec](https://html.spec.whatwg.org/).

## How does it work?

First, read [a quick introduction to HTML](https://html.spec.whatwg.org/#a-quick-introduction-to-html). Go on, it's important.

An HTML document represents a tree of nodes. Each node (called an "element") consists of exactly three things: a **tag name** (such as `div`, `p` or `title`), a collection of **attributes** (a mapping of keys to values) and a list of **children** (other elements or text nested inside the node).

So: that's a **tag name** (a string), **attributes** (a mapping), and **children** (a list).

The simplest way to represent that structure in Python is a tuple of three elements:

```python
("", {}, [])
```

Here's an example of an anchor element (a link) with a text node inside it:

```python
link_element = ("a", {"href": "somewhere.html"}, ["click me!"])
```

Here's an example of a full HTML document (note that the `DOCTYPE` is missing, we'll come back to that later):

```python
document = (
    "html",
    {"lang": "en"},
    [
        ("head", {}, [("title", {}, ["Sample page"])]),
        (
            "body",
            {},
            [
                ("h1", {}, ["Sample page"]),
                (
                    "p",
                    {},
                    ["This is a ", ("a", {"href": "demo.html"}, ["simple"]), " sample"],
                ),
            ],
        ),
    ],
)
```

Once we've created a structure like this, we can use `hotmetal` to _render_ it into a string:

```pycon
>>> from hotmetal import render
>>> print(render(document, indent=2))
<html lang="en">
  <head>
    <title>
      Sample page
    </title>
  </head>
  <body>
    <h1>
      Sample page
    </h1>
    <p>
      This is a
      <a href="demo.html">
        simple
      </a>
       sample
    </p>
  </body>
</html>
```

In essence, _that's it_. That's all that `hotmetal` does.

## Components

But this all looks pretty fiddly, right? If you always needed to painstakingly assemble a huge tree of nested tuples to render every page on your web app, that would be annoyingly verbose and difficult to read.

So here's the clever bit: instead, **write functions with meaningful names that return element nodes, and build your web app with those**. Let's call these functions that return nodes _components_ (if you're familiar with React you might see where this is going).

```python
def menu_item(href, text):
    return ("li", {}, [("a", {"href": href}, [text])])


def menu(items):
    return ("ul", {}, [menu_item(href, text) for href, text in items])


menu_node = menu(
    [
        ("/home/", "Home"),
        ("/blog/", "Blog"),
    ]
)
```

... and so on, right down to the `<html>`.

For a good explanation of some useful patterns to use when composing markup in this way, have a read of the React docs on [Composition vs Inheritance](https://reactjs.org/docs/composition-vs-inheritance.html). The concepts should be directly transferable.

## Fragments

Earlier, we brushed over the fact that the example we used was missing its `DOCTYPE`. That's because the root of an HTML document is really two things: the `<html>` element itself, and before it [the `DOCTYPE` preamble](https://html.spec.whatwg.org/#the-doctype). We can express this structure in `hotmetal` by using a _fragment_. Again, the [same concept exists in React](https://reactjs.org/docs/fragments.html), but the syntax is simpler in `hotmetal`. Just use a node with an empty tag name and attributes:

```python
from hotmetal import safe


document = (
    "",
    {},
    [
        safe("<!DOCTYPE html>"),
        (
            "html",
            {"lang": "en"},
            [...],  # head, body etc
        ),
    ],
)
```

When rendering, `hotmetal` will "optimise away" the empty node, leaving only the two consecutive child nodes. This is also often useful during component composition: you might create a component that accepts a single child node as an argument, but you can still pass it a list of multiple nodes by wrapping them in a fragment.

But what's that `safe` thing about?

## Escaping

You have to be careful when generating HTML. If any part of your markup or text content can be supplied by a user (which is common in web applications), you may be vulnerable to cross-site scripting (XSS) attacks. The Django docs have [a good explanation of why this is important](https://docs.djangoproject.com/en/4.0/ref/templates/language/#automatic-html-escaping-1).

By default, `hotmetal` escapes _every_ string it renders using the same approach as Python's built-in [`html.escape`](https://docs.python.org/3/library/html.html#html.escape) functionality. So you can add user-generated content to your documents without worrying.

If you want to add some raw markup that you _know_ is safe (some hand-crafted HTML, or the rendered output of another templating system that already escapes unsafe content) then you can wrap those strings in the `safe` function. See the above section for an example.

## Context

The [React docs on context](https://reactjs.org/docs/context.html) say:

> Context provides a way to pass data through the component tree without having to pass props down manually at every level.

Exactly the same concept exists in `hotmetal`, but again the implementation is a little simpler.

If you're familiar with the concept of context in Django or Jinja templates, this is _not quite the same thing_. In those languages, context is the _only_ way to pass variables into a template. In `hotmetal` there's no need to do this: you can just create component functions that accept arguments:

```python
def header(title):
    return ("h1", {}, [title])
```

So where would you use context? Just like in React:

> Context is primarily used when some data needs to be accessible by many components at different nesting levels. Apply it sparingly because it makes component reuse more difficult.

A good example might be if you need to access the `request` object or the currently logged in user somewhere deep in your component tree, but you don't want to explicitly pass it down through the component hierarchy from the root.

To use context in `hotmetal`, you pass a dictionary to the `render` function:

```python
render(some_node, context={"logged_in_user_email": "hello@example.com"})
```

To access the context from inside the tree, replace any node in the tree with a _callable_ (a named function or a lambda) that returns that node. During rendering, `hotmetal` will call your function, passing the `context` dictionary as its single argument.

```python
def current_user_panel():
    return lambda context: (
        "p",
        {},
        [f"Hello, {context['logged_in_user_email']}"],
    )
```

## Indentation control

The `render` function takes an `indent` argument, which is a integer used to control how many spaces are used as indentation in the generated HTML. The default is 0, meaning the entire HTML string will be returned on a single line. You may wish to use (say) `indent=2` for development, and `indent=0` for production (essentially minifying your HTML).

## Testing tools

When writing tests for components, it's often useful to be able to search through a tree to find particular nodes and make assertions about them. To help with this, `hotmetal` provides a `find` function, which takes an iterable of nodes and a predicate callable, and returns a generator that yields nodes that match the predicate (using depth-first pre-order traversal of the nodes, much like the browser's [`querySelectorAll`](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelectorAll) function).

For example, given the following component:

```python
def header(title):
    return ("div", {"class": "header"}, [("h1", {}, [title])])
```

You could write a test something like this:

```python
from hotmetal.utils.find import find
from unittest import TestCase


class HeaderTestCase(TestCase):
    def test_title_appears_correctly_inside_h1(self):
        node = header("hello world")
        h1_elements = list(
            find([node], lambda node: isinstance(node, tuple) and node[0] == "h1")
        )
        self.assertEqual(len(h1_elements), 1)
        h1 = h1_elements[0]
        children = node[2]
        self.assertEqual(children, ["hello world"])
```

Here, a `lambda` is being used to match against each node in the tree, which returns `True` or `False` depending on whether that node should be included in the results. When writing the predicate, remember that the `node` argument may be a tree node (a tuple), or a text node (a string), or a function (for nodes that require `context`, see above).

As an alternative to writing the `predicate` function yourself, a selection of functions are provided that address common requirements for finding nodes. The `find` line in the above example can be rewritten like this:

```python
h1_elements = list(find([node], tag_is("h1")))
```

A full list of these predicate functions is below:

### `hotmetal.utils.find.tag_is(tag)`

Returns a predicate function that matches nodes by tag name: `find(nodes, tag_is("h1"))`

### `hotmetal.utils.find.id_is(id)`

Returns a predicate function that matches nodes by the value of the ID attribute: `find(nodes, id_is("header"))`

### `hotmetal.utils.find.has_class(cls)`

Returns a predicate function that matches nodes by a particular class name within the `class` attribute: `find(nodes, has_class("someclass"))`

### `hotmetal.utils.find.has_attr(attr)`

Returns a predicate function that matches nodes that have the given attribute, with any value: `find(nodes, has_attr("href"))`

### `hotmetal.utils.find.has_attr_with_value(attr, value)`

Returns a predicate function that matches nodes that have the given attribute, and also the value of that attribute is equal to the given value: `find(nodes, has_attr_with_value("type", "hidden"))`

### `hotmetal.utils.find.attr_value_matches(attr, predicate)`

Returns a predicate function that matches nodes that have the given attribute, and the value of that attribute matches the given predicate function: `find(nodes, attr_value_matches("class", lambda value: "background-" in value))`

### `hotmetal.utils.find.text_contains(text)`

Returns a predicate function that matches text nodes (strings) that contain the given text: `find(nodes, text_contains("hello world"))`

### `hotmetal.utils.find.any_immediate_child_matches(predicate)`

Returns a predicate function that matches nodes with at least one direct child node that matches the given predicate: `find(nodes, any_immediate_child_matches(text_contains("hello world")))`

### `hotmetal.utils.find.or_(*predicates)`

Given multiple predicate functions, returns a predicate function that matches nodes that match any of the predicates: `find(nodes, or_(tag_is("h1"), id_is("title")))`

### `hotmetal.utils.find.and_(*predicates)`

Given multiple predicate functions, returns a predicate function that matches nodes that match all of the predicates: `find(nodes, and_(tag_is("input"), has_attr_with_value("type", "text")))`

### `hotmetal.utils.find.not_(predicate)`

Inverts a predicate function: `find(nodes, and_(tag_is("input"), not_(has_attr_with_value("type", "hidden")))`

### `hotmetal.utils.find.TAG`
### `hotmetal.utils.find.ATTRS`
### `hotmetal.utils.find.CHILDREN`

These three constants are simply the indices into a node for each component. They enhance readability: instead of `children = node[2]` you can say `children = node[CHILDREN]`
