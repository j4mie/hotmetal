def classnames(*args):
    classes = []
    for arg in args:
        if isinstance(arg, bool):
            continue
        if isinstance(arg, dict):
            for key, value in arg.items():
                if value:
                    classes.append(key)
        elif isinstance(arg, str) and arg.strip():
            classes.append(arg.strip())
        elif isinstance(arg, (int, float)) and arg:
            classes.append(str(arg))
        elif isinstance(arg, (list, set)):
            child = classnames(*arg)
            if child:
                classes.append(child)
    return " ".join(classes)
