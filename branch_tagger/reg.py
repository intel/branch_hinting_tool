import re

def identify_weird_condition(cond):
    regex = re.compile(r"[ \t]*#[ \t]*[a-z]+")
    if regex.search(cond) is not None:
        return True
    return False



if_cond = """if (j1 == 0 && mode != 1 && !(word1(&u) & 1)
 Honor_FLT_ROUNDS

				&& Rounding >= 1

								   ) {"""
print identify_weird_condition(if_cond)