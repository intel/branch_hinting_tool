import re
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


def tokenize_line(orig_line, separators):
    token_list = []
    index = orig_line.find("\')\'")
    if index != -1:
        first_part = orig_line[0: index]
        last_part = orig_line[index + 3:]
        return split(first_part, separators) + [orig_line[index:index + 3]] + split(last_part, separators)

    index = orig_line.find("\'(\'")
    if index != -1:
        first_part = orig_line[0: index]
        last_part = orig_line[index + 3:]
        return split(first_part, separators) + [orig_line[index:index + 3]] + split(last_part, separators)


    regex = re.compile(r"[ \t]*#[ \t]*[a-z]+")
    if regex.match(orig_line) is not None:
        string = orig_line[regex.match(orig_line).end() + 1:]
        token_list = [orig_line[0: regex.match(orig_line).end() + 1]]
        stripped_line = string.rstrip("\n \t")
        if stripped_line.endswith("\\"):
            stripped_line_backslash = stripped_line.rstrip("\\")
            stripped_line_again = stripped_line_backslash.strip("\n \t(")

            end_token = ""
            rest = orig_line

            if stripped_line_again[-1] == '&' or stripped_line_again[-1] == '|':
                #print "se termina cu operator", (stripped_line_again.endswith("&&") or stripped_line_again.endswith("\|\|"))
                index_list_and = [m.start() for m in re.finditer("&&", orig_line)]
                index_list_or = [m.start() for m in re.finditer("\|\|", orig_line)]
                index_list = sorted(index_list_or + index_list_and)
                index_op = index_list[-1]
                end_token = orig_line[index_op:]
                rest = orig_line[0:index_op]
                #print "separat", split(rest, separators) + [end_token]
                return token_list + split(rest, separators) + [end_token]
        return token_list + split(string, separators)


    if (orig_line.find("&&") != -1 or orig_line.find("||") != -1) and (not orig_line.endswith("\\\n")):
        #print "linii care se termina cu endl si au op",orig_line
        stripped_line = orig_line.strip("\n \t")
        #if (not stripped_line.endswith("\\")):

        rest = orig_line
        #if stripped_line.endswith("&&") or stripped_line.endswith("\|\|"):
        if stripped_line[-1] == '&' or stripped_line[-1] == '|':
            index_list_and = [m.start() for m in re.finditer("&&", orig_line)]
            index_list_or = [m.start() for m in re.finditer("\|\|", orig_line)]
            index_list = sorted(index_list_or + index_list_and)
            index_op = index_list[-1]
            end_token = orig_line[index_op:]
            rest = orig_line[0:index_op]
            return split(rest, separators) + [end_token]

    if (orig_line.find("&&") != -1 or orig_line.find("||") != -1) and orig_line.endswith("\\\n"):
        #print "linii care se termina cu backendl si au op",orig_line
       # if stripped_line.endswith("\\"):
        stripped_line = orig_line.strip("\n \t")
        stripped_line_backslash = stripped_line.rstrip("\\")
        stripped_line_again = stripped_line_backslash.strip("\n \t(")

        end_token = ""
        rest = orig_line

        if stripped_line_again[-1] == '&' or stripped_line_again[-1] == '|':
            #print "se termina cu operator", (stripped_line_again.endswith("&&") or stripped_line_again.endswith("\|\|"))
            index_list_and = [m.start() for m in re.finditer("&&", orig_line)]
            index_list_or = [m.start() for m in re.finditer("\|\|", orig_line)]
            index_list = sorted(index_list_or + index_list_and)

            #print index_list , " " , orig_line
            index_op = index_list[-1]
            end_token = orig_line[index_op:]
            rest = orig_line[0:index_op]
            #print "separat", split(rest, separators) + [end_token]
            return split(rest, separators) + [end_token]



    if orig_line.find("//") != -1:
        comment = orig_line[orig_line.find("//"):]
        string = orig_line[0:orig_line.find("//")]
        return split(string, separators) + [comment]

    #print "nada", orig_line
    return split(orig_line, separators)


"""
Splits a string into tokens according to the separators, keeping the separators.

@input: string - the string to split
@input: separators - a list of separators according to which the string will be split

@return: a list with the tokens in a string
"""


def split(string, separators):
    separators.sort(key=len)
    i = 0
    token_list = []

    while i < len(string):
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


def tag_condition(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += token.strip('\n') + " if branch" + '\n'
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += token.strip('\n') + " while branch" + '\n'
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += token.strip('\n') + " for branch" + '\n'


def tag_condition_comment(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += token.strip('\n') + "/*if branch*/" + '\n'
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += token.strip('\n') + "/*while branch*/" + '\n'
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += token.strip('\n') + "/*for branch*/" + '\n'


def tag_condition_operator(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += "/*if branch*/" + '\\\n' + token
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += "/*while branch*/" + '\\\n' + token
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += "/*for branch*/" + '\\\n' + token


def tag_condition_last_operator_no_backslash_in_preprocessor(token):
    index_and = token.find("&&")
    index_or = token.find("||")
    if index_and != -1:
        if GlobalVar.if_condition:

            GlobalVar.modified_text += token[0:index_and]+ "/*if branch*/" +'\\\n' +  token[index_and:].strip("\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_and] + "/*while branch*/" + '\\\n' + token[index_and:].strip("\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_and]+ "/*for branch*/" + '\\\n' + token[index_and:].strip("\n")
    if index_or != -1:
        if GlobalVar.if_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*if branch*/" +'\\\n' + token[index_or:].strip("\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*while branch*/" + '\\\n' + token[index_or:].strip("\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*for branch*/" + '\\\n' + token[index_or:].strip("\n")

def tag_condition_last_operator_in_preprocessor(token):
    index_and = token.find("&&")
    index_or = token.find("||")
    if index_and != -1:
        if GlobalVar.if_condition:

            GlobalVar.modified_text += token[0:index_and]+ "/*if branch*/" +'\\\n' +  token[index_and:].strip("\\\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_and] + "/*while branch*/" + '\\\n' + token[index_and:].strip("\\\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_and]+ "/*for branch*/" + '\\\n' + token[index_and:].strip("\\\n")
    if index_or != -1:
        if GlobalVar.if_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*if branch*/" +'\\\n' + token[index_or:].strip("\\\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*while branch*/" + '\\\n' + token[index_or:].strip("\\\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*for branch*/" + '\\\n' + token[index_or:].strip("\\\n")

def tag_condition_last_operator(token):
    index_and = token.find("&&")
    index_or = token.find("||")
    if index_and != -1:
        if GlobalVar.if_condition:
            GlobalVar.modified_text += token[0:index_and]+ "/*if branch*/" +'\n' +  token[index_and:].strip("\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_and] + "/*while branch*/" + '\n' + token[index_and:].strip("\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_and]+ "/*for branch*/" + '\n' + token[index_and:].strip("\n")
    if index_or != -1:
        if GlobalVar.if_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*if branch*/" +'\n' + token[index_or:].strip("\n")
        elif GlobalVar.while_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*while branch*/" + '\n' + token[index_or:].strip("\n")
        elif GlobalVar.for_condition:
            GlobalVar.modified_text += token[0:index_or] + "/*for branch*/" + '\n' + token[index_or:].strip("\n")

def tag_condition_operator_no_backslash(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += "/*if branch*/" +'\n' + token
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += "/*while branch*/" + '\n' + token
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += "/*for branch*/" + '\n' + token


def tag_condition_preprocessor(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += "/*if branch*/" + '\\\n' + token.strip('\\\n')
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += "/*while branch*/" + '\\\n' + token.strip('\\\n')
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += "/*for branch*/" + '\\\n' + token.strip('\\\n')


def tag_condition_close_paren(token):
    if GlobalVar.if_condition:
        GlobalVar.modified_text += "/*if branch*/" + token
    elif GlobalVar.while_condition:
        GlobalVar.modified_text += "/*while branch*/" + token
    elif GlobalVar.for_condition:
        GlobalVar.modified_text += "/*for branch*/" + token



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
    if token.find('"') != -1 and token.find("\'\"\'") == -1:
        list_index_double_quotes = [m.start() for m in re.finditer('"', token)]
        for i in list_index_double_quotes:
            if GlobalVar.in_string:
                if count_backslash(token, i) % 2 == 0:
                    GlobalVar.in_string = False
            else:
                GlobalVar.in_string = True
