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

def tokenize_line(orig_line, separators):
    """
    Takes a line from a file and tokenize it according to the function "split",
    keeping in mind some exceptions:
    1. If the line contains one of the strings ')' or '(', only the
       parts before and after the problematic strings will be split. This
       is done to avoid corner cases such as --if (c == ')')--
       and be misled into thinking the context ended sooner.
    2. If the line begins with a preprocessor directive, the line will
       split after it

    @input: orig_string - the line from file to split
    @input: separators - a list of separators according to
                         which the line will be split
    @return: a list with the tokens in a string
    """
    # ')' is found
    index_close = orig_line.find("\')\'")
    # '(' is found
    index_open = orig_line.find("\'(\'")
    if index_open != -1 or index_close != -1:
        return false_paren(orig_line, separators)
    if re.match(r'\s*#\s*error', orig_line) and (
            orig_line.find("if") != -1 or \
            orig_line.find("for") != -1 or \
            orig_line.find("while") != -1):
        return [orig_line]

    # detect beginning of preprocessor directive
    regex = re.compile(r"\s*#\s*[a-z]+")
    if regex.match(orig_line) is not None:
        string = orig_line[regex.match(orig_line).end() + 1:]
        token_list = [orig_line[: regex.match(orig_line).end() + 1]]
        return token_list + split(string, separators)

    return split(orig_line, separators)


def split(string, separators):
    """
    Splits a string into tokens according to the separators,
    keeping the separators.

    @input: string - the string to split
    @input: separators - a list of separators according to which
                         the string will be split

    @return: a list with the tokens in a string
    """
    i = 0
    last_separator = None
    token_list = []
    while i < len(string):
        found = False
        for current in separators:
            if current == string[i:i + len(current)]:
                if current == last_separator and current.isspace():
                    token_list[-1] += current
                else:
                    token_list += [current]
                    last_separator = current
                i += len(current)
                found = True
                break;
        if not found:
            if not token_list or last_separator:
                token_list += [string[i]]
            else:
                token_list[-1] += string[i]
            i += 1
            last_separator = None

    return token_list


def __tag(condition, comment_tag, backslash, line_no):
    """
    Takes a context without line endings and tags it accordingly

    @input: condition - context(conditional instruction)
    @input: comment_tag - if/for/while
    @input: backslash - \n or \\n

    @return: tagged_condition - tagged context
    """
    index_list = get_index_list(condition)
    binary_op_or = " ||*/"
    binary_op_and = " &&*/"

    frmt = "%s/*%s: %s%s%s" % ("%s", line_no, comment_tag, "%s", backslash)
    if condition[index_list[0]] == '&':
        tagged_condition = frmt % (condition[:index_list[0]], binary_op_and)
    else:
        tagged_condition = frmt % (condition[:index_list[0]], binary_op_or)

    for i in range(0, len(index_list) - 1):
        substr = condition[index_list[i]: index_list[i + 1]]
        if condition[index_list[i + 1]] == '&':
            tagged_condition += frmt % (substr, binary_op_and)
        else:
            tagged_condition += frmt % (substr, binary_op_or)
    tagged_condition += condition[index_list[len(index_list) - 1]:]
    return tagged_condition


def tag(condition, line_no):
    line_break = "\\\n" if GlobalVar.in_preprocessor else "\n"
    name = None
    if GlobalVar.if_condition:
        name = "if"
    elif GlobalVar.while_condition:
        name = "while"
    elif GlobalVar.for_condition:
        name = "for"
    if name:
        return __tag(condition, "%s branch" % name, line_break, line_no)


def tag_default_condition(token, endl):
    name = None
    if GlobalVar.if_condition:
        name = "if"
    elif GlobalVar.while_condition:
        name = "while"
    elif GlobalVar.for_condition:
        name = "for"
    if name:
        GlobalVar.modified_text.write(
            token.rstrip(endl) + "/*%s branch &&*/%s" % (name, endl))


def false_paren(line, separators):
    """
    Splits a line of code taking into account the cases --if (c == ')')--

    @input: line - the line of code which contains '(' or ')'
    @input: separators - separators

    @return: split_line - the line split accordingly
    """
    index_open_paren = [m.start() for m in re.finditer(r"\'\(\'", line)]
    index_close_paren = [m.start() for m in re.finditer(r"\'\)\'", line)]
    index_paren = sorted(index_open_paren + index_close_paren)

    split_line = split(line[:index_paren[0]], separators)
    split_line.append(line[index_paren[0]:index_paren[0] + 3])

    for i in range(0, len(index_paren) - 1):
        start = index_paren[i]
        end = index_paren[i + 1]
        split_line += split(line[start + 3:end], separators)
        split_line.append(line[end:end + 3])

    split_line += split(line[index_paren[-1] + 3:], separators)
    return split_line


def get_index_list(condition):
    """
    Gets a list with the real boolean operators (those which
    are not inside strings or comments).

    @input: condition - context

    @return: clean_list - list with the real boolean operators
    """
    index_list_quotes = [m.start() for m in re.finditer('"', condition)]

    bad_quotes = [m.start() for m in re.finditer("\'\"\'", condition)]
    for bad_quote in bad_quotes:
        if bad_quote != -1 and index_list_quotes > 0:
            index_list_quotes.remove(bad_quote + 1)

    index_list_open_comm = [m.start() for m in re.finditer(r"/\*", condition)]
    index_list_close_comm = [m.start() for m in re.finditer(r"\*/", condition)]

    index_list_and = [m.start() for m in re.finditer(r"&&", condition)]
    index_list_or = [m.start() for m in re.finditer(r"\|\|", condition)]
    index_list_binary_op = sorted(index_list_and + index_list_or)

    bad_indexes = []
    if index_list_binary_op and index_list_open_comm:
        index_list_comm = sorted(index_list_open_comm + index_list_close_comm)
        bad_indexes = get_bad_indexes(index_list_comm, index_list_binary_op)

    bad_indexes_quotes = []

    if index_list_binary_op and index_list_quotes:
        bad_indexes_quotes = get_bad_indexes_quotes(
            index_list_quotes, index_list_binary_op, condition)

    clean_list = [x for x in index_list_binary_op if x not in bad_indexes]
    clean_list = [x for x in clean_list if x not in bad_indexes_quotes]

    return clean_list


def get_bad_indexes(index_list_comm, index_list_binary_op):
    """
    Gets a list with indexes of boolean operators which are inside
    multi-line comments.

    @input: index_list_comm - list which contains the indexes of "/*" and
                              "*/" from a context
    @input: index_list_binary_op - list which contains the indexes of "&&" and
                                   "||" from a context

    @return: bad_indexes - list with boolean operators which are inside
                           multi-line comments
    """
    bad_indexes = []
    for i in xrange(0, len(index_list_comm), 2):
        for op_index in index_list_binary_op:
            if index_list_comm[i] <= op_index < index_list_comm[i + 1]:
                bad_indexes.append(op_index)
    return bad_indexes


def get_bad_indexes_quotes(index_list_comm, index_list_binary_op, condition):
    """
    Gets a list with indexes of boolean operators which are inside strings,
    taking into account escaped quotes.

    @input: index_list_comm - list which contains the indexes of all quotes
                              from a context
    @input: index_list_binary_op - list which contains the indexes of "&&" and
                                   "||" from a context

    @return: bad_indexes - list with boolean operators which are inside strings
    """
    for index in index_list_comm[:]:
        if count_backslash(condition, index) % 2 == 1:
            index_list_comm.remove(index)
    return get_bad_indexes(index_list_comm, index_list_binary_op)


def count_backslash(token, index):
    """
    Counts the backslashes in a token before a certain index.
    This is useful when escaped quotes exist in strings.

    @input: token
    @input: index - the index of character "(quotes) in token

    @return: the number of backslashes before "(quotes) in a token
    """
    cnt = 0

    for i in xrange(index, -1, -1):
        if token[i - 1] != '\\':
            break
        else:
            cnt += 1
    return cnt


def update_in_string(token):
    """
    Updates the state of a global variable which retains whether a string is
    being traversed
    The operation is performed if the token does not contain '"'

    @input: token
    """
    if token.find("\'\\\"\'") != -1 and not GlobalVar.in_string:
        return
    if token.find('"') != -1 and token.find("\'\"\'") == -1:
        for i in [m.start() for m in re.finditer('"', token)]:
            if GlobalVar.in_string:
                if count_backslash(token, i) % 2 == 0:
                    GlobalVar.in_string = False
            else:
                GlobalVar.in_string = True


def identify_weird_condition(cond):
    """
    Identifies when a conditional instruction contains preprocessor directives.

    @input: cond - context
    @:return True/False
    """
    return re.compile(r"[ \t]*#[ \t]*[a-z]+").search(cond) is not None
