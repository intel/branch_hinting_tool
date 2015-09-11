# Keeps all the global variables
from cStringIO import StringIO


class GlobalVar:
    def __init__(self):
        pass

    modified_text = StringIO()

    count_paren = 1

    if_condition = False
    while_condition = False
    for_condition = False

    in_preprocessor = False
    in_string = False

    in_comment = False

    comment = False

    line_comment = False
    condition = StringIO()
