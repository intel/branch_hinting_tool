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

<<<<<<< HEAD
    line_comment = False
    condition = StringIO()
=======
    condition = ""
>>>>>>> fccb7db8d0088e3a7dec7c34dd0c32cb0745141e
