# Keeps all the global variables
class GlobalVar:
    def __init__(self):
        pass

    modified_text = ""

    count_paren = 1

    if_condition = False
    while_condition = False
    for_condition = False

    in_preprocessor = False
    in_string = False

    in_comment = False

    comment = False

    condition = ""
