import bsInternal
def format_spaces(msg=''):
    if "  " in msg: 
        while True:
            msg=msg.replace("  ", " ")
            if "  " not in msg: break
    if msg.endswith(" "): msg=msg[0:-1]
    if msg.startswith(" "): msg=msg[1:]
    if msg.startswith("/") and len(msg.split("/")) > 1 and msg.split("/")[1].startswith(" "): msg=msg[0]+msg[2:]
    return msg

def word_equals(word="", exists_word="", max_mist=2):
    result=0
    if len(word) in range(len(exists_word) - 2, len(exists_word) + 2):
        for b in [word, exists_word]:
            for i in range(len(b)):
                if b == word: c=exists_word
                else: c=word
                if len(c) > i:
                    if b[i] == c[i]: result+=1
    if result >= (len(exists_word)+len(word))-max_mist*2: return True
    return False
    
def text_split(words=[], words_count=4, split_symbol=', ', string_symbol='\n', stroke_on_end=True):
    msg = ''
    for i in range(len(words)):
        if int(i / words_count) > 0 and i % words_count == 0: msg += words[i]+string_symbol
        else: 
            msg = msg+words[i]+split_symbol if i != (len(words)-1) else msg+words[i]
    if stroke_on_end:
        if not msg.endswith(string_symbol): msg += string_symbol
    else:
        if msg.endswith(string_symbol): msg = msg[0:-1]
    return msg
    
