import os
import re
from string import whitespace, punctuation, maketrans
from itertools import groupby
import itertools

#path_input = "/home/cbuse/Desktop/php/php-src/Zend/"
path_input = "/home/cbuse/Desktop/Python/"
for filename in os.listdir(path_input):
        if filename.endswith('.c') or filename.endswith('.h'):
            f = open(path_input+filename)
            str1 = "\\\""
            str2 = ":"
            if  f.read().find(str1) != -1:
               # if f.read().find(str1) != -1:
                print filename
def get_index_list(orig_line):
    index_list_and = [m.start() for m in re.finditer("&&", orig_line)]
    index_list_or = [m.start() for m in re.finditer("\|\|", orig_line)]
    return sorted(index_list_or + index_list_and)

def tag(condition):
    tagged_condition = ""
    index_list = get_index_list(condition)

    tagged_condition += condition[0 : index_list[0]] + "/*branch*/\n"
    for i in range(0, len(index_list) - 1):
        tagged_condition += condition[index_list[i] : index_list[i + 1]] + "/*branch*/\n"
    tagged_condition += condition[index_list[len(index_list) - 1] : len(condition)]


    return tagged_condition



#condition = """if ((*tmp == '0' && length > 1) /* numbers with leading zeros */	 || (end - tmp > MAX_LENGTH_OF_LONG - 1) /* number too long */	 || (SIZEOF_ZEND_LONG == 4 &&	     end - tmp == MAX_LENGTH_OF_LONG - 1 &&	     *tmp > '2'))"""
#print condition
#print "-------------------------------------------------------------------"
#print tag(condition)
#print "-------------------------------------------------------------------"

"""
def r():
    if 2 in range(1,4):
        print True
    else:
        print False

def get_index_list(condition):
    index_list_quotes = [m.start() for m in re.finditer('"', condition)]
    bad_index = condition.find("\'\"\'")
    if bad_index != -1 and len(index_list_quotes) > 0:
        index_list_quotes.remove(bad_index + 1)
    return index_list_quotes


print get_index_list(condition)
"""




"""
def alt(s, splitters):
    result = []
    special = dict.fromkeys(splitters, True)
    splitted = [''.join(g) for k,g in groupby(s, special.get)]
    for s in splitted:
        index_open = s.find('(')
        index_close = s.find(')')
        if  index_open != -1:
            result += [s[0:index_open]] + [s[index_open]] + [s[index_open+1:]]
        if index_close != -1:
            #print "inca o data"
            result += [s[0:index_close]] + [s[index_close]] + [s[index_close+1:]]
        if index_open == -1 and index_close == -1:
            #print s,"din else"
            result += [s]

    return result
"""
def alt(s, splitters):
    result = []
    special = dict.fromkeys(splitters, True)
    splitted = [''.join(g) for k,g in groupby(s, special.get)]
    return splitted

s = "if ( los/*tb*/its)\n"
splitters = ' /**/()&&\t||'
print alt(s, splitters)

"""
#mai buna dar elimina spatiile :(
def separate(myStr, seps):
    answer = []
    temp = []
    for char in myStr:
        if char in seps:
            answer.append(''.join(temp))
            answer.append(char)
            temp = []
        else:
            temp.append(char)
    answer.append(''.join(temp))
    return answer

myStr = "if ( lostbits)"
seps = ' /**/()&&\t||'
#print separate(myStr, seps)

print re.split(r'\s(?=(?:\(||into|ones|)\b)', "Let's split this string ( into )  many small ones")
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


condition = """while (**ptr != '/' && **ptr != '.' && **ptr != '-' && **ptr != '(' && **ptr != ')' ) {
		++*ptr;
	}"""


separators = ['(', ')', '\t', ' ','/*', '*/', '&&', '||']
print false_paren(condition, separators)