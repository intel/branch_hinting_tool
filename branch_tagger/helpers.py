############################################################################
# Branch Hinting Tool
#
# Copyright (c) 2015, Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
###########################################################################

import re
from global_var import GlobalVar

"""
Takes a line from a file and tokenize it according to the function "split", keeping in mind some exceptions:
    1. If the line contains one of the strings ')' or '(', only the parts before and after the problematic strings will
     be split. This is done to avoid corner cases such as --if (c == ')')-- and be misled into thinking the context
     ended sooner.
    2. If the line begins with a preprocessor directive, the line will split after it

@input: orig_string - the line from file to split
@input: separators - a list of separators according to which the line will be split

@return: a list with the tokens in a string
"""


def tokenize_line(orig_line, separators):
    # ')' is found
    index_close = orig_line.find("\')\'")
    # '(' is found
    index_open = orig_line.find("\'(\'")
    if index_open != -1 or index_close != -1:
        return false_paren(orig_line, separators)
    if orig_line.find("#error") != -1 and (
                        orig_line.find("if") != -1 or orig_line.find("for") != -1 or orig_line.find("while") != -1):
        return [orig_line]

    # detect beginning of preprocessor directive
    regex = re.compile(r"[ \t]*#[ \t]*[a-z]+")
    if regex.match(orig_line) is not None:
        string = orig_line[regex.match(orig_line).end() + 1:]
        token_list = [orig_line[0: regex.match(orig_line).end() + 1]]
        return token_list + split(string, separators)

    return split(orig_line, separators)


"""
Splits a string into tokens according to the separators, keeping the separators.

@input: string - the string to split
@input: separators - a list of separators according to which the string will be split

@return: a list with the tokens in a string
"""


def split(string, separators):
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
Takes a context without line endings and tags it accordingly

@input: condition - context(conditional instruction)
@input: comment_tag - if/for/while
@input: backslash - \n or \\n

@return: tagged_condition - tagged context
"""


def __tag__(condition, comment_tag, backslash, line_no):
    tagged_condition = ""
    index_list = get_index_list(condition)
    binary_op_or = " ||*/"
    binary_op_and = " &&*/"

    if condition[index_list[0]] == '&':
        tagged_condition += condition[0: index_list[0]] + "/*" + line_no + ": " + comment_tag + binary_op_and + backslash
    else:
        tagged_condition += condition[0: index_list[0]] + "/*" + line_no + ": " + comment_tag + binary_op_or + backslash

    for i in range(0, len(index_list) - 1):
        if condition[index_list[i + 1]] == '&':
            tagged_condition += condition[index_list[i]: index_list[i + 1]] + "/*" + line_no + ": " + comment_tag + binary_op_and + backslash
        else:
            tagged_condition += condition[index_list[i]: index_list[i + 1]] + "/*" + line_no + ": " + comment_tag + binary_op_or + backslash
    tagged_condition += condition[index_list[len(index_list) - 1]: len(condition)]
    return tagged_condition


def tag(condition, line_no):
    eol = "\\\n" if GlobalVar.in_preprocessor else "\n"
    if GlobalVar.if_condition:
        return __tag__(condition, "if branch", eol, line_no)
    elif GlobalVar.while_condition:
        return __tag__(condition, "while branch", eol, line_no)
    elif GlobalVar.for_condition:
        return __tag__(condition, "for branch", eol, line_no)


def tag_default_condition(token, endl):
    if GlobalVar.if_condition:
        GlobalVar.modified_text.write(token.rstrip(endl) + "/*if branch &&*/" + endl)
    elif GlobalVar.while_condition:
        GlobalVar.modified_text.write(token.rstrip(endl) + "/*while branch &&*/" + endl)
    elif GlobalVar.for_condition:
        GlobalVar.modified_text.write(token.rstrip(endl) + "/*for branch &&*/" + endl)


"""
Splits a line of code taking into account the cases --if (c == ')')--

@input: line - the line of code which contains '(' or ')'
@input: separators - separators

@return: split_line - the line split accordingly

"""


def false_paren(line, separators):
    index_open_paren = [m.start() for m in re.finditer("\'\(\'", line)]
    index_close_paren = [m.start() for m in re.finditer("\'\)\'", line)]
    index_paren = sorted(index_open_paren + index_close_paren)

    split_line = []
    split_line += split(line[0: index_paren[0]], separators) + [line[index_paren[0]:index_paren[0] + 3]]
    for i in range(0, len(index_paren) - 1):
        split_line += split(line[index_paren[i] + 3:index_paren[i + 1]], separators) + [
            line[index_paren[i + 1]:index_paren[i + 1] + 3]]
    split_line += split(line[index_paren[len(index_paren) - 1] + 3:], separators)
    return split_line

"""
Gets a list with the real boolean operators(those which are not inside strings or comments).

@input: condition - context

@return: clean_list - list with the real boolean operators
"""


def get_index_list(condition):
    index_list_quotes = [m.start() for m in re.finditer('"', condition)]

    bad_quotes = [m.start() for m in re.finditer("\'\"\'", condition)]
    for bad_quote in bad_quotes:
        if bad_quote != -1 and len(index_list_quotes) > 0:
            index_list_quotes.remove(bad_quote + 1)

    index_list_open_comm = [m.start() for m in re.finditer("/\*", condition)]
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
        bad_indexes_quotes = get_bad_indexes_quotes(index_list_quotes, index_list_binary_op, condition)

    clean_list = [x for x in index_list_binary_op if x not in bad_indexes]
    clean_list = [x for x in clean_list if x not in bad_indexes_quotes]

    return clean_list


"""
Gets a list with indexes of boolean operators which are inside multi-line comments.

@input: index_list_comm - list which contains the indexes of "/*" and "*/" from a context
@input: index_list_binary_op - list which contains the indexes of "&&" and "||" from a context

@return: bad_indexes - list with boolean operators which are inside multi-line comments
"""


def get_bad_indexes(index_list_comm, index_list_binary_op):
    bad_indexes = []
    for i in xrange(0, len(index_list_comm), 2):
        for j in xrange(len(index_list_binary_op)):
            if index_list_binary_op[j] in range(index_list_comm[i], index_list_comm[i + 1]):
                bad_indexes.append(index_list_binary_op[j])
    return bad_indexes


"""
Gets a list with indexes of boolean operators which are inside strings, taking into account escaped quotes.

@input: index_list_comm - list which contains the indexes of all quotes from a context
@input: index_list_binary_op - list which contains the indexes of "&&" and "||" from a context

@return: bad_indexes - list with boolean operators which are inside strings
"""


def get_bad_indexes_quotes(index_list_comm, index_list_binary_op, condition):
    new_index_list_comm = index_list_comm
    bad_indexes = []
    escaped_quotes = []
    for i in xrange(len(index_list_comm)):
        if count_backslash(condition, index_list_comm[i]) % 2 == 1:
            escaped_quotes.append(index_list_comm[i])

    for i in xrange(len(escaped_quotes)):
        new_index_list_comm.remove(escaped_quotes[i])

    if len(new_index_list_comm) > 0:
        for i in xrange(0, len(new_index_list_comm), 2):

            for j in xrange(len(index_list_binary_op)):
                if index_list_binary_op[j] in range(new_index_list_comm[i], new_index_list_comm[i + 1]):
                    bad_indexes.append(index_list_binary_op[j])

    return bad_indexes


"""
Counts the backslashes in a token before a certain index.
This is useful when escaped quotes exist in strings.

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
    if token.find("\'\\\"\'") != -1 and not GlobalVar.in_string:
        GlobalVar.in_string = False
        return
    if token.find('"') != -1 and token.find("\'\"\'") == -1:

        list_index_double_quotes = [m.start() for m in re.finditer('"', token)]
        for i in list_index_double_quotes:
            if GlobalVar.in_string:
                if count_backslash(token, i) % 2 == 0:
                    GlobalVar.in_string = False
            else:
                GlobalVar.in_string = True


"""
Identifies when a conditional instruction contains preprocessor directives.

@input: cond - context
@:return True/False
"""
def identify_weird_condition(cond):
    regex = re.compile(r"[ \t]*#[ \t]*[a-z]+")
    return regex.search(cond) is not None
