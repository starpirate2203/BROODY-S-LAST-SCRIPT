import bs
import bsInternal
import json, os, copy
import time, sys

def sort_settings(data={}):
    return sorted(data.items(), key=lambda dr : (dr[1] not in [False, True], dr[0]))

def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        ValueError=ValueError,
        basestring=basestring,
        dict=dict,
        float=float,
        id=id,
        int=int,
        isinstance=isinstance,
        list=list,
        long=long,
        str=str,
        tuple=tuple):

    def _iterencode_list(lst, _current_indent_level):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (' ' * (_indent * _current_indent_level))
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        for value in lst:
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, basestring):
                yield buf + _encoder(value)
            elif value is None:
                yield buf + 'null'
            elif value is True:
                yield buf + 'true'
            elif value is False:
                yield buf + 'false'
            elif isinstance(value, (int, long)):
                yield buf + str(value)
            elif isinstance(value, float):
                yield buf + _floatstr(value)
            else:
                yield buf
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                for chunk in chunks:
                    yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + (' ' * (_indent * _current_indent_level))
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(dct, _current_indent_level):
        if not dct:
            yield '{}'
            return
        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (' ' * (_indent * _current_indent_level))
            item_separator = _item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        first = True
        if _sort_keys:
            items = sort_settings(dct)
        else:
            items = dct.iteritems()
        for key, value in items:
            if isinstance(key, basestring):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                key = _floatstr(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif key is None:
                key = 'null'
            elif isinstance(key, (int, long)):
                key = str(key)
            elif _skipkeys:
                continue
            else:
                raise TypeError("key " + repr(key) + " is not a string")
            if first:
                first = False
            else:
                yield item_separator
            yield _encoder(key)
            yield _key_separator
            if isinstance(value, basestring):
                yield _encoder(value)
            elif value is None:
                yield 'null'
            elif value is True:
                yield 'true'
            elif value is False:
                yield 'false'
            elif isinstance(value, (int, long)):
                yield str(value)
            elif isinstance(value, float):
                yield _floatstr(value)
            else:
                if isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                for chunk in chunks:
                    yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + (' ' * (_indent * _current_indent_level))
        yield '}'
        if markers is not None:
            del markers[markerid]

    def _iterencode(o, _current_indent_level):
        if isinstance(o, basestring):
            yield _encoder(o)
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, (int, long)):
            yield str(o)
        elif isinstance(o, float):
            yield _floatstr(o)
        elif isinstance(o, (list, tuple)):
            for chunk in _iterencode_list(o, _current_indent_level):
                yield chunk
        elif isinstance(o, dict):
            for chunk in _iterencode_dict(o, _current_indent_level):
                yield chunk
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o)
            for chunk in _iterencode(o, _current_indent_level):
                yield chunk
            if markers is not None:
                del markers[markerid]

    return _iterencode

json.encoder._make_iterencode = _make_iterencode
_gData={"admins":[], "vips":[], "prefixes":{}, "banned": [], \
    "skins": {}, "lobby_connect_menu": False, "show_game_name": True, \
    "admins_prefix": True, "timer_the_disappearance_of_the_effect": True, \
    "powerup_lighting": True, "timer_the_disappearance_of_the_powerup": True, \
    "timer_before_the_bomb_explode": True, "chat_commands_enabled": True, \
    "disable_powerups": False, "auto-update": False, "internet_tab_search_text":"", \
    "in_menu_author_name": True, "party_search_log": False, "exclude_powerups": []}
        
env = bs.getEnvironment()
gSettingsPath=os.path.join(env["userScriptsDirectory"], "settings.json")

class Settings(object):
    def __init__(self, path=None):
        self.path = path
        self.path_correct = (self.path is not None and os.path.exists(self.path) and not os.path.isdir(self.path))
        self.get_settings()
    def get_settings(self):
        if not hasattr(self, 'modTime'): self.modTime = 0
        if self.path_correct: m_time = os.path.getmtime(self.path)
        else: m_time = 1
        if m_time != self.modTime:
            try: self.data = json.load(open(self.path))
            except Exception: self.data = _gData
        return self.data
    def set_settings(self, data):
        self.data = data
        if self.path_correct: 
            json.dump(self.data, open(self.path, 'w+'), indent=4, sort_keys=True)
            self.modTime = os.path.getmtime(self.path)
        else: self.modTime = 1
    def save(self):
        self.set_settings(data = self.data)
    def get_setting(self, key, default_value=True):
        return self.get_settings().get(key, default_value)
    def set_setting(self, key, value):
        self.data.update({key: value})
        self.save()

st = Settings(path=gSettingsPath)
def set_setting(name=None, value=True):
    st.set_setting(key=name, value=value)
    
def get_setting(name=None, default_value=None):
    return st.get_setting(key=name, default_value=default_value)

def set_settings(values=[{}]):
    data = st.get_settings()
    for i in values: data.update(i)
    st.set_settings(data=data)
    
def get_settings():
    return st.get_settings()

def reload_settings(data=None):
    if data is not None:
        for i in data: _gData.update({i: data[i]})

def rewrite_settings():
    json.dump(_gData, open(gSettingsPath, "w+"), indent=4, sort_keys=True)
    st.get_settings()

def check_settings_file():
    if not os.path.exists(gSettingsPath): rewrite_settings()
    else:
        data = st.get_settings()
        for i in _gData:
            if data.get(i) is None:
                reload_settings(data=data)
                rewrite_settings()
                break

def write_log(path=None):
    try:
        if path is None: path=os.path.join(env["userScriptsDirectory"], "log")
        with open(path, "w+") as f:
            f.write(bsInternal._getLog())
            f.close()
    except Exception as E: bs.screenMessage(str(E))
    
def save_settings():
    st.save()
