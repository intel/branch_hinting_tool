from state import State
from global_var import GlobalVar
from helpers import tag_condition, tag_condition_comment, \
    tag_condition_preprocessor, tag_condition_close_paren, \
    tag_condition_operator, tag_condition_operator_no_backslash,\
    tag_condition_last_operator, tag_condition_last_operator_in_preprocessor,\
    tag_condition_last_operator_no_backslash_in_preprocessor

"""
All the states of the finite state machine are implemented here.
The method next_state ususally implements:
	- the updating of the global variable which keeps the tagged text	
	- transition to the next state
"""

"""
State OutContext also checks
	- whether a preprocessor directive is being traversed
	- whether a string is being traversed
and updates the state of the global variables which indicate which 
condition is being traversed(if, for, while)
"""


class OutContext(State):
    def run_state(self):

        print "Tagging file"

    def next_state(self, token):

        GlobalVar.modified_text += token

        if token.find('#') != -1 and token.endswith('\n') and (not token.endswith('\\\n')):
            GlobalVar.in_preprocessor = False
            return OutContext()
        if token.find('#') != -1 and (not token.endswith('\n')):
            GlobalVar.in_preprocessor = True
        if token.endswith('\\\n'):
            GlobalVar.in_preprocessor = True
        if token.endswith('\n') and (not token.endswith('\\\n')) and GlobalVar.in_preprocessor:
            GlobalVar.in_preprocessor = False

        if GlobalVar.in_string:
            return OutContext()

        if token == "/*":
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

        return OutContext()

class InComment(State):
    def run_state(self):
        pass

    def next_state(self, token):
        GlobalVar.modified_text += token

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

        if token.endswith('\n'):
            tag_condition_comment(token)
        else:
            GlobalVar.modified_text += token

        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InConditionInComment()
        if token == "(":
            GlobalVar.count_paren = 1
            return InConditionOpenParen()

        return InCondition()


class InConditionInComment(State):
    def run_state(self):

        pass

    def next_state(self, token):

        if token.endswith('\n'):
            tag_condition(token)
        else:
            GlobalVar.modified_text += token

        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return InCondition()

        return InConditionInComment()


"""
If in a condition, a binary operator && or || is found, it will be followed by
endline in order to have one condition per line in case the condition is multiple.
Example : if (a && b) ----->
		  if (a && /*if branch*/
		  	b)/*if branch*/
In case the line begins with a binary operator, that operator will not be followed by endline.
"""


class InConditionOpenParen(State):
    def run_state(self):
        pass

    def next_state(self, token):

        if GlobalVar.in_preprocessor:
            # TODO: aici nu intra pe if-urile bune
            #print "in preprocesor", token
            if token.endswith('\\\n') and (token.find("&&") == -1 and token.find("||") == -1):
                tag_condition_preprocessor(token)
            elif (token.find("&&") != -1 or token.find("||") != -1) and token.endswith("\\\n"):
                #print "smecheria cu endl din backslash"
                tag_condition_last_operator_in_preprocessor(token)
            elif token.endswith('\n') and (not token.endswith('\\\n')) and (token.find("&&") == -1 and token.find("||") == -1):
                tag_condition_comment(token)
            elif token.endswith('\n') and (not token.endswith('\\\n')) and (token.find("&&") != -1 or token.find("||") != -1):
                #print "smecheria cu endl"
                tag_condition_last_operator_no_backslash_in_preprocessor(token)
            elif token == '&&' or token == '||':
                tag_condition_operator(token)
            else:
                GlobalVar.modified_text += token
        else:

            if (token.find("&&") != -1 or token.find("||") != -1) and token.endswith("\n"):
                tag_condition_last_operator(token)
            elif token.endswith('\n') and (token.find("&&") == -1 and token.find("||") == -1):
                tag_condition_comment(token)
            elif token == '&&' or token == '||':
                tag_condition_operator_no_backslash(token)
            else:
                GlobalVar.modified_text += token

        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InConditionOpenParenInComment()
        if token == ")":
            GlobalVar.count_paren -= 1
            if GlobalVar.count_paren == 0:
                return InConditionOpenParenCloseParen()
        if token == "(":
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

        return InConditionOpenParen()


class InConditionOpenParenInComment(State):
    def run_state(self):

        pass

    def next_state(self, token):

        if token.endswith('\n'):
            tag_condition(token)
        else:
            GlobalVar.modified_text += token

        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return InConditionOpenParen()

        return InConditionOpenParenInComment()


class InConditionOpenParenCloseParen(State):
    def run_state(self):
        pass

    def next_state(self, token):
        tag_condition_close_paren(token)

        # the condition which was being traversed has ended,
        # so the flags indicating the condition type are reset
        GlobalVar.if_condition = False
        GlobalVar.while_condition = False
        GlobalVar.FOR_CONDITION = False

        return OutContext()
