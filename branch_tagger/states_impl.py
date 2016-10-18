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

from state import State
from global_var import GlobalVar
from helpers import \
    tag, get_index_list, tag_default_condition, identify_weird_condition
from cStringIO import StringIO


class OutContext(State):
    """
    All the states of the finite state machine are implemented here.
    The method next_state usually implements:
	- the updating of the global variable which keeps the tagged text
	- transition to the next state

    State OutContext also checks
	- whether a preprocessor directive is being traversed
	- whether a string is being traversed
    and updates the state of the global variables which indicate which
    condition is being traversed(if, for, while)
    """
    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.modified_text.write(token)

        if token.find('#') != -1 and token.endswith('\n') and \
           not token.endswith('\\\n'):
            GlobalVar.in_preprocessor = False
            return OutContext()
        if token.find('#') != -1 and (not token.endswith('\n')):
            GlobalVar.in_preprocessor = True
        if token.endswith('\\\n'):
            GlobalVar.in_preprocessor = True
        if token.endswith('\n') and not token.endswith('\\\n') and \
           GlobalVar.in_preprocessor:
            GlobalVar.in_preprocessor = False

        if GlobalVar.in_string:
            return OutContext()
        if token.find("/*") != -1 and GlobalVar.in_string:
            return OutContext()
        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InComment()
        if token == "if" or token == "if\n":
            GlobalVar.if_condition = True
            return InCondition()
        if token == "while":
            GlobalVar.while_condition = True
            return InCondition()
        if token == "for":
            GlobalVar.for_condition = True
            return InCondition()

        # one line comment starts
        if token.find("//") != -1 and not GlobalVar.in_string and \
           token.find("\n") != -1:
            return OutContext()
        if token.find("//") != -1 and not GlobalVar.in_string:
            return InLineComment()
        return OutContext()


class InLineComment(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.in_string = False
        GlobalVar.modified_text.write(token)
        if token.endswith("\n"):
            return OutContext()
        return InLineComment()


class InComment(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.modified_text.write(token)

        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return OutContext()
        # if I find " inside a comment, I am not inside a string
        if token.find("\""):
            GlobalVar.in_string = False

        return InComment()


class InCondition(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.condition.write(token)

        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InConditionInComment()

        if token == "(" and GlobalVar.in_string is False:
            GlobalVar.count_paren = 1
            return InConditionOpenParen()

        return InCondition()


class InConditionInComment(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.condition.write(token)

        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return InCondition()

        return InConditionInComment()


class InConditionOpenParen(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.condition.write(token)
        if token.find("/*") != -1 and GlobalVar.in_string:
            return InConditionOpenParen()

        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InConditionOpenParenInComment()

        if token == ")" and GlobalVar.in_string is False:
            GlobalVar.count_paren -= 1
            if GlobalVar.count_paren == 0:
                return InConditionOpenParenCloseParen()
        if token == "(" and GlobalVar.in_string is False:
            GlobalVar.count_paren += 1

        if token == "if":
            GlobalVar.if_condition = True
            GlobalVar.count_paren = 0
            return InConditionOpenParen()
        if token == "while":
            GlobalVar.if_condition = False
            GlobalVar.while_condition = True
            GlobalVar.count_paren = 0
            return InConditionOpenParen()
        # in one line comment
        if token.find("//") != -1 and not GlobalVar.in_string and \
           token.find("///") == -1:
            GlobalVar.line_comment = True
        return InConditionOpenParen()


class InConditionOpenParenInComment(State):

    def run_state(self):
        pass

    def next_state(self, token):
        token = token[0]
        GlobalVar.condition.write(token)

        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return InConditionOpenParen()

        return InConditionOpenParenInComment()


class InConditionOpenParenCloseParen(State):
    """
    This class reconstructs the condition with multiple boolean operators,
    eliminates all line endings and tags all boolean operators.
    Weird conditions (those with unbalanced parenthesis and preprocessor
    directives such as #ifdef, #ifndef, #else,
    #define, etc) are also checked and tagged with /*weird condition*/.
    """

    def run_state(self):
        pass

    def next_state(self, token):

        line_no = str(token[1])
        token = token[0]

        index_list = get_index_list(GlobalVar.condition.getvalue())
        string = GlobalVar.condition.getvalue()

        if identify_weird_condition(GlobalVar.condition.getvalue()):
            GlobalVar.modified_text.write(GlobalVar.condition.getvalue())
            GlobalVar.modified_text.write(token)
        # when there are one line comments in condition, the conditional
        # instruction is not tagged
        elif GlobalVar.line_comment:
            GlobalVar.modified_text.write(GlobalVar.condition.getvalue())
            GlobalVar.modified_text.write(token)
            GlobalVar.line_comment = False
        # when there is a string which contains "/*", the condition is not
        # tagged
        elif GlobalVar.condition.getvalue().find("/*") != -1 and \
             GlobalVar.condition.getvalue().find('"') != -1:
            GlobalVar.modified_text.write(GlobalVar.condition.getvalue())
            GlobalVar.modified_text.write(token)
        else:
            if string.find("\\\n") != -1:
                string = string.replace("\\\n", "")
            if string.find("\n"):
                string = string.replace("\n", "")

            # simple conditions(without boolean operators ||, &&)
            if len(index_list) == 0:
                if GlobalVar.if_condition:
                    GlobalVar.modified_text.write(
                        GlobalVar.condition.getvalue() + "/*" + line_no + \
                        ": if branch &&*/")
                elif GlobalVar.while_condition:
                    GlobalVar.modified_text.write(
                        GlobalVar.condition.getvalue() + "/*" + line_no + \
                        ": while branch &&*/")
                elif GlobalVar.for_condition:
                    GlobalVar.modified_text.write(
                        GlobalVar.condition.getvalue() + "/*" + line_no + \
                        ": for branch &&*/")
                GlobalVar.modified_text.write(token)

            else:
                new = tag(string, line_no)
                GlobalVar.modified_text.write(new)
                # last simple condition from conditional instruction is tagged
                # by default
                if token.endswith("\\\n"):
                    tag_default_condition(token, "\\\n")
                elif token.endswith("\n") and (not token.endswith("\\\n")):
                    tag_default_condition(token, '\n')
                else:
                    if GlobalVar.if_condition:
                        GlobalVar.modified_text.write(
                            token + "/*" + line_no + ": if branch &&*/")
                    elif GlobalVar.while_condition:
                        GlobalVar.modified_text.write(
                            token + "/*" + line_no + ": while branch &&*/")
                    elif GlobalVar.for_condition:
                        GlobalVar.modified_text.write(
                            token + "/*" + line_no + ": for branch &&*/")

        # the condition which was being traversed has ended,
        # so the flags indicating the condition type are reset
        GlobalVar.if_condition = False
        GlobalVar.while_condition = False
        GlobalVar.for_condition = False
        GlobalVar.condition = StringIO()

        return OutContext()
