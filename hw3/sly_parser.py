from sly import Parser
from sly_lexer import MyLexer

class MyParser(Parser):
    tokens = MyLexer.tokens

    @_('s_exp_list')
    def program(self, p):
        return p.s_exp_list

    @_('s_exp s_exp_list', '')
    def s_exp_list(self, p):
        if len(p) > 0:
            if p.s_exp_list != "":
                f_str = False
                p_s_exp = p.s_exp
                p_s_exp_list = p.s_exp_list
                if str(p.s_exp)[0] == '"': 
                    f_str = True
                    p_s_exp = p.s_exp[1:-1]
                if str(p.s_exp_list)[0] == '"':
                    p_s_exp_list = p.s_exp_list[1:-1]
                d = []
                f = False
                if type(p_s_exp_list) == list and type(p_s_exp_list[0]) == list: f = True
                if type(p_s_exp_list) == list:
                    if type(p_s_exp) == list: 
                        d = [*p_s_exp, *p_s_exp_list]
                    else:
                        if type(p_s_exp) == dict:
                            d = [p_s_exp, *p_s_exp_list]
                        else:
                            if f:
                                d = {p_s_exp: p_s_exp_list[0]}
                            else:
                                d = [p_s_exp, *p_s_exp_list]
                elif type(p_s_exp_list) == dict and type(p_s_exp) == dict:
                    if p_s_exp.keys() == p_s_exp_list.keys():
                        d = [p_s_exp, p_s_exp_list]
                    else:
                        p_s_exp.update(p_s_exp_list)
                        d = p_s_exp
                else:
                    if type(p_s_exp) == list: d = [*p_s_exp, p_s_exp_list]
                    else:
                        if type(p_s_exp) == int or f_str:
                            d = [p_s_exp, p_s_exp_list]
                        else:
                            d = {
                                p_s_exp: p_s_exp_list
                            }
                return d
            else:
                return p.s_exp
        else: return ""

    @_('data', 'LEFT_PAR s_exp_list RIGHT_PAR')
    def s_exp(self, p):
        if len(p) > 1:
            if type(p.s_exp_list) == dict: return p.s_exp_list
            else: return [p.s_exp_list]
        else: return p[0]

    @_('IDENTIFIER', 'STRING')
    def data(self, p):
        return p[0]

    @_('NUMBER')
    def data(self, p):
        return int(p[0])