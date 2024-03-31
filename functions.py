def verbosize_list(lst: list) -> str:
    if len(lst) == 1:
        return lst[0]
    elif len(lst) == 0:
        return ""
    else:
        return ", ".join(lst[:-1]) + " y " + lst[-1]
