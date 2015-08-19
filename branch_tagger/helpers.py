import re
from itertools import groupby
from global_var import GlobalVar

"""
Takes a line from a file and tokenizes it according to the function "split", keeping in mind two exceptions:
    1. If the line contains one of the strings ')' or '(', only the parts before and after the problematic strings will
     be split.
    2. If the line begins with a preprocessor directive, the line will split after it
    3. If the line begins with a boolean operator && or ||, the line will split after it
    4. If the line has a one-line comment, the line will split before it

@input: orig_string - the line from file to split
@input: separators - a list of separators according to which the line will be split

@return: a list with the tokens in a string
"""


# not used stuff
def token_comment(orig_line, separators):
    index_begin_comm = orig_line.find("/*")
    index_end_comm = orig_line.find("*/")

    if index_begin_comm != -1 and index_end_comm != -1:
        return tokenize_line(orig_line[0:index_begin_comm], separators) + [
            orig_line[index_begin_comm:index_end_comm]] + tokenize_line(orig_line[index_end_comm:], separators)

    # /*comment
    # comment
    # comment*/
    if index_begin_comm != -1:
        GlobalVar.comment = True
        return tokenize_line(orig_line[0:index_begin_comm], separators) + [orig_line[index_begin_comm:]]

    if index_end_comm != -1:
        # print "sfarsit comentariu"
        GlobalVar.comment = False
        return [orig_line[0:index_end_comm]] + tokenize_line(orig_line[index_end_comm:], separators)

    if GlobalVar.comment:
        return [orig_line]

    # nu se poate face

    # if (orig_line.find("if") == -1 or orig_line.find("while") == -1 or orig_line.find("for") == -1) or orig_line.find("||") == -1 or orig_line.find("&&") == -1:
    """
    if "if" not in orig_line or "while" not in orig_line or "&&" not in orig_line or "||" not in orig_line or "for" not in orig_line:
        return [orig_line]
    """
    return tokenize_line(orig_line, separators)


def tokenize_line(orig_line, separators):

    # ')' is found
    index_close = orig_line.find("\')\'")
    # '(' is found
    index_open = orig_line.find("\'(\'")
    if index_open != -1 or index_close != -1:
        return false_paren(orig_line, separators)

    # begin preprocessor directive
    # cazul din php_config.h cu #error no suitable type for ssize_t found
    regex = re.compile(r"[ \t]*#[ \t]*[a-z]+")
    if regex.match(orig_line) is not None:
        if orig_line.find("for") == -1:
            string = orig_line[regex.match(orig_line).end() + 1:]
            token_list = [orig_line[0: regex.match(orig_line).end() + 1]]
            return token_list + split(string, separators)
        else:
            return [orig_line]

    if orig_line.find("//") != -1:
        comment = orig_line[orig_line.find("//"):]
        string = orig_line[0:orig_line.find("//")]
        return split(string, separators) + [comment]
    return split(orig_line, separators)


"""
Splits a string into tokens according to the separators, keeping the separators.

@input: string - the string to split
@input: separators - a list of separators according to which the string will be split

@return: a list with the tokens in a string
"""


def split(string, separators):
    # separators.sort(key=len)
    i = 0
    token_list = []
    length = len(string)
    while i < length:
        separator = ""
        for current in separators:
            if current == string[i:i + len(current)]:
                separator = current
        if separator != "":
            token_list += [separator]
            i += len(separator)
        else:
            if token_list == []:
                token_list = [""]
            if token_list[-1] in separators:
                token_list += [""]
            token_list[-1] += string[i]
            i += 1

    return token_list


"""
The following functions(tag_condition, tag_condition_comment, tag_condition_operator, tag_condition_preprocessor,
tag_condition_close_paren, tag_condition_operator_no_backslash) tag the lines inside a condition(if, for, while)
according to their needs. If inside the condition there are multiple line comments, the tag will simply be 
'if/while/for branch' at the end of the line, otherwise the tag will be '/*if/while/for branch*/'.
The last tag for a condition appears immediately after the last closing parenthesis.
Specific tagging for each type of condition(if, for, while) is done by checking the state of global variables
which retain the type of condition traversed at a certain moment.

@input: token
"""


def __tag__(condition, comment_tag, backslash):
    tagged_condition = ""
    index_list = get_index_list(condition)
    binary_op_or = " ||*/"
    binary_op_and = " &&*/"

    if condition[index_list[0]] == '&':
        tagged_condition = "".join(
            [tagged_condition, condition[0: index_list[0]], comment_tag, binary_op_and, backslash])
    else:
        tagged_condition = "".join(
            [tagged_condition, condition[0: index_list[0]], comment_tag, binary_op_or, backslash])

    for i in range(0, len(index_list) - 1):
        if condition[index_list[i + 1]] == '&':
            tagged_condition = "".join(
                [tagged_condition, condition[index_list[i]: index_list[i + 1]], comment_tag, binary_op_and, backslash])
        else:
            tagged_condition = "".join(
                [tagged_condition, condition[index_list[i]: index_list[i + 1]], comment_tag, binary_op_or, backslash])
    tagged_condition = "".join([tagged_condition, condition[index_list[len(index_list) - 1]: len(condition)]])
    return tagged_condition


def tag(condition):
    if GlobalVar.if_condition:
        if GlobalVar.in_preprocessor:
            return __tag__(condition, "/*if branch", "\\\n")
        else:
            return __tag__(condition, "/*if branch", "\n")
    elif GlobalVar.while_condition:
        if GlobalVar.in_preprocessor:
            return __tag__(condition, "/*while branch", "\\\n")
        else:
            return __tag__(condition, "/*while branch", "\n")
    elif GlobalVar.for_condition:
        if GlobalVar.in_preprocessor:
            return __tag__(condition, "/*for branch", "\\\n")
        else:
            return __tag__(condition, "/*for branch", "\n")


def tag_weird_condition(condition):
    index_list_endl = [m.start() for m in re.finditer("\n", condition)]

    tagged_condition = ""
    tagged_condition += condition[0: index_list_endl[0]] + "/*weird condition*/"

    for i in range(0, len(index_list_endl) - 1):
        tagged_condition += condition[index_list_endl[i]: index_list_endl[i + 1]] + "/*weird condition*/"

    tagged_condition += condition[index_list_endl[len(index_list_endl) - 1]: len(condition)] + "/*weird condition*/"
    return tagged_condition


def false_paren(line, separators):
    index_open_paren = [m.start() for m in re.finditer("\'\(\'", line)]
    index_close_paren = [m.start() for m in re.finditer("\'\)\'", line)]
    index_paren = sorted(index_open_paren + index_close_paren)

    splitted_line = []
    splitted_line += split(line[0: index_paren[0]], separators) + [line[index_paren[0]:index_paren[0] + 3]]
    for i in range(0, len(index_paren) - 1):
        splitted_line += split(line[index_paren[i] + 3:index_paren[i + 1]], separators) + [line[index_paren[i + 1]:index_paren[i + 1] + 3]]
    splitted_line += split(line[index_paren[len(index_paren) - 1] +3:], separators)
    return splitted_line


def get_index_list(condition):
    index_list_quotes = [m.start() for m in re.finditer('"', condition)]

    bad_quotes = [m.start() for m in re.finditer("\'\"\'", condition)]
    for bad_quote in bad_quotes:
        if bad_quote != -1 and len(index_list_quotes) > 0:
            index_list_quotes.remove(bad_quote + 1)

    index_list_open_comm = [m.start() for m in re.finditer("\/\*", condition)]
    index_list_close_comm = [m.start() for m in re.finditer("\*/", condition)]

    index_list_and = [m.start() for m in re.finditer("&&", condition)]
    index_list_or = [m.start() for m in re.finditer("\|\|", condition)]
    index_list_binary_op = sorted(index_list_and + index_list_or)

    bad_indexes = []
    if len(index_list_binary_op) >= 1 and len(index_list_open_comm) != 0:
        index_list_comm = sorted(index_list_open_comm + index_list_close_comm)
        bad_indexes = get_bad_indexes(index_list_comm, index_list_binary_op)

    bad_indexes_quotes = []

    if len(index_list_binary_op) >= 1 and len(index_list_quotes) != 0:
        #print GlobalVar.condition
        bad_indexes_quotes = get_bad_indexes_quotes(index_list_quotes, index_list_binary_op, condition)

    clean_list = [x for x in index_list_binary_op if x not in bad_indexes]
    clean_list = [x for x in clean_list if x not in bad_indexes_quotes]

    return clean_list


def get_bad_indexes(index_list_comm, index_list_binary_op):
    bad_indexes = []
    for i in xrange(0, len(index_list_comm), 2):
        for j in xrange(len(index_list_binary_op)):
            if index_list_binary_op[j] in range(index_list_comm[i], index_list_comm[i + 1]):
                bad_indexes.append(index_list_binary_op[j])
    return bad_indexes


def get_bad_indexes_quotes(index_list_comm, index_list_binary_op, condition):

    #print index_list_comm
    new_index_list_comm = index_list_comm
    bad_indexes = []
    escaped_quotes = []
    for i in xrange(len(index_list_comm)):
        if count_backslash(condition, index_list_comm[i]) % 2 == 1:
            escaped_quotes.append(index_list_comm[i])

    for i in xrange(len(escaped_quotes)):
        #print escaped_quotes[i]
        new_index_list_comm.remove(escaped_quotes[i])

    if len(new_index_list_comm) > 0:
        for i in xrange(0, len(new_index_list_comm), 2):

            for j in xrange(len(index_list_binary_op)):
                if index_list_binary_op[j] in range(new_index_list_comm[i], new_index_list_comm[i + 1]):
                    bad_indexes.append(index_list_binary_op[j])

    return bad_indexes


"""
Counts the backslashes in a token before a certain index

@input: token
@input: index - the index of character "(quotes) in token

@return: the number of backslashes before "(quotes) in a token
"""


def count_backslash(token, index):
    cnt = 0

    for i in xrange(index, -1, -1):
        if token[i - 1] != '\\':
            break
        else:
            cnt += 1
    return cnt


"""
Updates the state of a global variable which retains whether a string is being traversed
The operation is performed if the token does not contain '"'

@input: token
"""


def update_in_string(token):
    #print GlobalVar.in_string
    #print token,' ' ,token.find("\'\\\"\'")

    if token.find("\'\\\"\'") != -1 and GlobalVar.in_string is False:
        GlobalVar.in_string = False
        #print "aici"
        """
        list_index_simple = [m.start() for m in re.finditer("\'\"\'", token)]
        if len(list_index_simple) % 2 == 0:
            GlobalVar.in_string = False
        """
        return
    if token.find('"') != -1 and token.find("\'\"\'") == -1:
        #print "aici"
        list_index_double_quotes = [m.start() for m in re.finditer('"', token)]
        for i in list_index_double_quotes:
            if GlobalVar.in_string:
                if count_backslash(token, i) % 2 == 0:
                    GlobalVar.in_string = False
            else:
                GlobalVar.in_string = True

