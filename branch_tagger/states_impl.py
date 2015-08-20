import re

from state import State
from global_var import GlobalVar
from helpers import tag, get_index_list, tag_weird_condition, tag_default_condition

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
        #print token
        #print "token*"+token+"*token"
        GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])


        if token.find('#') != -1 and token.endswith('\n') and (not token.endswith('\\\n')):
            #print "aicissa", token
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

        if token.find("/*") != -1:
            GlobalVar.in_comment = True
            return InComment()
        if token == "if" or token == "if\n":
            GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])
            GlobalVar.modified_text = GlobalVar.modified_text[:-len(token)]
            GlobalVar.if_condition = True
            return InCondition()
        if token == "while":
            #print "aici"
            GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])
            GlobalVar.modified_text = GlobalVar.modified_text[:-len(token)]
            GlobalVar.while_condition = True
            return InCondition()
        if token == "for":
            #print "aici e for"
            GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])
            GlobalVar.modified_text = GlobalVar.modified_text[:-len(token)]
            GlobalVar.for_condition = True
            return InCondition()

        return OutContext()

class InComment(State):
    def run_state(self):
        pass

    def next_state(self, token):
        GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])
        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return OutContext()
        # if I find " inside a comment, I am not inside a string
        if token.find("\""):
            GlobalVar.in_string = False

        return InComment()


class InCondition(State):
    def run_state(self):
        print "inCondition"
        pass

    def next_state(self, token):
        #print token
       # if token.endswith('\n'):
        #
        #else:
        GlobalVar.condition = "".join([GlobalVar.condition, token])


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

        #if token.endswith('\n'):
         #   GlobalVar.condition += token
        #else:
        GlobalVar.condition = "".join([GlobalVar.condition, token])


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
        #print "in condition"
        GlobalVar.condition = "".join([GlobalVar.condition, token])

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
            GlobalVar.weird_condition = True
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

        #if token.endswith('\n'):
        #    GlobalVar.condition += token
        #else:
        GlobalVar.condition = "".join([GlobalVar.condition, token])


        if token.find("*/") != -1:
            GlobalVar.in_comment = False
            return InConditionOpenParen()

        return InConditionOpenParenInComment()


class InConditionOpenParenCloseParen(State):
    def run_state(self):
        pass

    def next_state(self, token):
        #print token

        #print GlobalVar.condition

        index_list = get_index_list(GlobalVar.condition)
        string = GlobalVar.condition
        #print string
        #print "--------------------------------------------------------------"


        #todo s-ar putea sa nu fie suficient pt alte cazuri #if, dar se strica alea din define poate !!!!
        #print GlobalVar.weird_condition
        else_index = GlobalVar.condition.find("else")
        define_index = GlobalVar.condition.find("define")
        if GlobalVar.weird_condition or GlobalVar.condition.find("ifdef") != -1 or GlobalVar.condition.find("endif") != -1 or GlobalVar.condition.find("ifndef") != -1\
                or (define_index != -1 and (not GlobalVar.condition[define_index-1].isalnum()) and (not GlobalVar.condition[define_index + 6].isalnum()) and \
                            (GlobalVar.condition[define_index-1] != '_' and GlobalVar.condition[define_index + 4]!= '_')) or \
                (else_index != -1 and (not GlobalVar.condition[else_index-1].isalnum()) and (not GlobalVar.condition[else_index + 4].isalnum()) and \
                         (GlobalVar.condition[else_index-1] != '_' and GlobalVar.condition[else_index + 4]!= '_')) or GlobalVar.condition.find("#if") != -1:
            # conditia cu #if e provizorie, poate sa fie si cu spatii, taburi, if inconjurat de space sau tab??? pare aceeasi treaba cu daca gasesc if in if
            """
            print "------------------------------------------------------------------------begin--------------------------------------"
            print GlobalVar.condition
            print "------------------------------------------------------------------------end--------------------------------------"
            """
            #tag special pt weird condition

            """ATENTIE AICI TAG CU WEIRD CONDITION"""
            #GlobalVar.modified_text = "".join([GlobalVar.modified_text, tag_weird_condition(GlobalVar.condition)])
            GlobalVar.modified_text += GlobalVar.condition
            GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])

        else:
            if string.find("\\\n") != -1:
                string = string.replace("\\\n","")
            if string.find("\n"):
                string = string.replace("\n","")

            if len(index_list) == 0:
                #print GlobalVar.condition
                if GlobalVar.if_condition:
                    GlobalVar.modified_text = "".join([GlobalVar.modified_text, GlobalVar.condition, "/*if branch &&*/"])
                elif GlobalVar.while_condition:
                     GlobalVar.modified_text = "".join([GlobalVar.modified_text, GlobalVar.condition, "/*while branch &&*/"])
                elif GlobalVar.for_condition:
                     GlobalVar.modified_text = "".join([GlobalVar.modified_text, GlobalVar.condition, "/*for branch &&*/"])
                GlobalVar.modified_text = "".join([GlobalVar.modified_text, token])

            else:
                new = tag(string)
                GlobalVar.modified_text = "".join([GlobalVar.modified_text, new])

                if token.endswith("\\\n"):
                    tag_default_condition(token, "\\\n")
                elif token.endswith("\n"):
                    tag_default_condition(token, '\n')
                else:
                    if GlobalVar.if_condition:
                        GlobalVar.modified_text = "".join([GlobalVar.modified_text, token, "/*if branch &&*/"])
                    elif GlobalVar.while_condition:
                         GlobalVar.modified_text = "".join([GlobalVar.modified_text, token, "/*while branch &&*/"])
                    elif GlobalVar.for_condition:
                         GlobalVar.modified_text = "".join([GlobalVar.modified_text, token, "/*for branch &&*/"])


        # the condition which was being traversed has ended,
        # so the flags indicating the condition type are reset
        GlobalVar.if_condition = False
        GlobalVar.while_condition = False
        GlobalVar.for_condition = False
        GlobalVar.condition = ""
        GlobalVar.weird_condition = False

        return OutContext()