#lifted from http://stackoverflow.com/questions/3601864/python-load-text-as-python-object/3602436#3602436
# Author: Paul McGuire

import json
import codecs
from pyparsing import (Suppress, Regex, quotedString, Word, alphas, 
alphanums, oneOf, Forward, Optional, dictOf, delimitedList, Group, removeQuotes)

def transform(txt):

    idx1 = txt.find('[')
    idx2 = txt.find('{')
    if idx1 < idx2 and idx1 > 0:
        txt = txt[idx1:txt.rfind(']')+1]
    elif idx2 < idx1 and idx2 > 0:
        txt = txt[idx2:txt.rfind('}')+1]
    
    try:
        json.loads(txt)
    except:
        # parse dict-like syntax    

        LBRACK,RBRACK,LBRACE,RBRACE,COLON,COMMA = map(Suppress,"[]{}:,")
        integer = Regex(r"[+-]?\d+").setParseAction(lambda t:int(t[0]))
        real = Regex(r"[+-]?\d+\.\d*").setParseAction(lambda t:float(t[0]))
        string_ = Word(alphas,alphanums+"_") | quotedString.setParseAction(removeQuotes)
        bool_ = oneOf("true false").setParseAction(lambda t: t[0]=="true")
        item = Forward()

        key = string_
        dict_ = LBRACE - Optional(dictOf(key+COLON, item+Optional(COMMA))) + RBRACE
        list_ = LBRACK - Optional(delimitedList(item)) + RBRACK
        item << (real | integer | string_ | bool_ | Group(list_ | dict_ ))

        result = item.parseString(txt,parseAll=True)[0]
        print result
        txt = result

    return txt
