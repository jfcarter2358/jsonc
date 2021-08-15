import json
import re
import uuid
import copy
import collections

__version__ = '1.0.1'

def _finditem(obj, key):
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = _finditem(v, key)
            if item is not None:
                return item

class JSONCDict(dict):
    def __init__(self, parent=None, jsonc_key=None, *args, **kwargs):
        """
        Initialize the dictionary
        """

        super(JSONCDict, self).__init__(*args, **kwargs)
        # create the variables that we'll use to deal with the comments
        self.jsonc_with_comments = {}
        self.jsonc_parent = parent
        self.jsonc_key = jsonc_key

    def __setitem__(self, key, value):
        """
        Set an item in the dictionary
        """

        invalid_keys = ['jsonc_key', 'jsonc_with_comments', 'jsonc_parent']
        if key in invalid_keys:
            raise KeyError(f'Key "{key}" in not allowed for a JSONCDict')

        super(JSONCDict, self).__setitem__(key, value)
        # add the value to the with comments dictionary

        # handle if a dictionary was handed back
        if type(value) == JSONCDict or type(value) == JSONCList:
            self.jsonc_with_comments.__setitem__(key, value.jsonc_with_comments)
        else:
            self.jsonc_with_comments.__setitem__(key, value)

        if self.jsonc_parent != None:
            self.jsonc_parent.__setitem__(self.jsonc_key, self)

    def __delitem__(self, key):
        """
        Delete an item from the dictionary
        """
        super(JSONCDict, self).__delitem__(key)

    def __getitem__(self, key):
        """
        Get an item from the dictionary
        """
        out = super(JSONCDict, self).__getitem__(key)
        # handle dictionaries being passed without changes being reflected back in the JSONCDict
        if type(out) == dict:
            out = JSONCDict(data=out, parent=self, key=key)
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(key)
            return out
        elif type(out) == list:
            out = JSONCList(data=out)
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(key)
            return out
        elif type(out) == JSONCDict:
            out.jsonc_parent = self
            out.jsonc_key = key
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(key)
            return out
        elif type(out) == JSONCList:
            out.jsonc_parent = self
            out.jsonc_key = key
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(key)
            return out
        else:
            return out

    def clear(self):
        """
        Clear the dictionary
        """
        super(JSONCDict, self).clear()
        # clear the internal variables
        self.jsonc_with_comments = {}

def indexing_decorator(func):

    def decorated(self, index, *args):
        return func(self, index, *args)

    return decorated

class JSONCList(collections.MutableSequence):
    def __init__(self, data=[], parent=None, key=None):
        self._inner_list = data
        self.jsonc_with_comments = []
        self.jsonc_parent = parent
        self.jsonc_key = key

    def __len__(self):
        return len(self._inner_list)

    @indexing_decorator
    def __delitem__(self, index):
        self._inner_list.__delitem__(index)
        self.jsonc_with_comments.__delitem__(self.find_comment_index(index))

    @indexing_decorator
    def insert(self, index, value):
        self._inner_list.insert(index, value)
        self.jsonc_with_comments.insert(self.find_comment_index(index), value)

    @indexing_decorator
    def __setitem__(self, index, value):
        self._inner_list.__setitem__(index, value)

        if type(value) == JSONCDict or type(value) == JSONCList:
            self.jsonc_with_comments.__setitem__(self.find_comment_index(index), value.jsonc_with_comments)
        else:
            self.jsonc_with_comments.__setitem__(self.find_comment_index(index), value)

        if self.jsonc_parent != None:
            self.jsonc_parent.__setitem__(self.jsonc_key, self)

    @indexing_decorator
    def __getitem__(self, index):
        out = self._inner_list.__getitem__(index)

        if type(out) == dict:
            out = JSONCDict(data=out, parent=self, key=index)
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(self.find_comment_index(index))
            return out
        elif type(out) == list:
            out = JSONCList(data=out)
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(self.find_comment_index(index))
            return out
        elif type(out) == JSONCDict:
            out.jsonc_parent = self
            out.jsonc_key = index
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(self.find_comment_index(index))
            return out
        elif type(out) == JSONCList:
            out.jsonc_parent = self
            out.jsonc_key = index
            out.jsonc_with_comments = self.jsonc_with_comments.__getitem__(self.find_comment_index(index))
            return out
        else:
            return out

    def append(self, value):
        self.insert(len(self) + 1, value)

    def __str__(self):
        return str(self._inner_list)

    def __repr__(self):
        return str(self._inner_list)

    def find_comment_index(self, index):
        counter = 0
        idx = 0
        while idx < index:
            if counter == len(self.jsonc_with_comments):
                return counter + 1
            if type(self.jsonc_with_comments[counter]) != str:
                idx += 1
            elif not self.jsonc_with_comments[counter].startswith('.jsonc'):
                idx += 1
            counter += 1
        return counter


def load(stream):
    """
    Initialize a JSONCDict from a file
    """
    data = stream.read()
    return loads(data)

def loads(text):
    """
    Initialize a JSONCDict from a string
    """
    # inline_pattern = re.compile(r'(?:^|[ \t])+\/\/(.*)', re.MULTILINE)
    # multiline_pattern = re.compile(r'(?:^|[ \t])+\/\*(((?!\/\*).)|\n|\r)*\*\/')

    lines = text.split('\n')
    lines = [l for l in lines if not len(l.strip()) == 0]

    single_line_patterns = {
        'c': '(?:^|[ \t])+\/\/((?:[^"]*"[^"]")*[^"]*(?:$))',
        'python': '(?:^|[ \t])+#((?:[^"]*"[^"]")*[^"]*(?:$))'
    }

    inline_patterns = {
        'c': '((?:^|[ \t])[^ \t\n]+[ \t]*)\/\/((?:[^"]*"[^"]")*[^"]*(?:$))',
        'python': '((?:^|[ \t])[^ \t\n]+[ \t]*)#((?:[^"]*"[^"]")*[^"]*(?:$))'
    }

    # block comments are not yet supported
    '''
    block_patterns = {
        'c': '(?:^|[ \t])+\/\*(((?!\/\*).)|\n|\r)*\*\/',
        'python_double': '(?:^|[ \t])+"""(((?!""").)|\n|\r)*"""',
        'python_single': '(?:^|[ \t])+\'\'\'(((?!\'\'\').)|\n|\r)*\'\'\'',
        'html': '(?:^|[ \t])+<!--(((?!<!--).)|\n|\r)*-->'
    }
    '''

    list_start_pattern = r'\[(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    list_end_pattern = r'\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    map_start_pattern = r'\{(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'
    map_end_pattern = r'\}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'

    list_count = 0
    map_count = 1

    for i in range(1, len(lines) - 1):
        l = lines[i]

        if re.search(list_start_pattern, l):
            list_count += 1
        if re.search(list_end_pattern, l):
            list_count -= 1
        if re.search(map_start_pattern, l):
            map_count += 1
        if re.search(map_end_pattern, l):
            map_count -= 1

        for k in inline_patterns:
            if re.search(inline_patterns[k], l):
                if map_count > list_count:
                    l = re.sub(inline_patterns[k], '\\1\n".jsonc_inline_{}_comment_{}": "\\2"'.format(k, str(uuid.uuid4())), l, count=1)
                else:
                    l = re.sub(inline_patterns[k], '\\1\n".jsonc_inline_{}_comment_{}: \\2"'.format(k, str(uuid.uuid4())), l, count=1)
        for k in single_line_patterns:
            if re.search(single_line_patterns[k], l):
                if map_count > list_count:
                    l = re.sub(single_line_patterns[k], '".jsonc_{}_comment_{}": "\\1"'.format(k, str(uuid.uuid4())), l, count=1)
                else:
                    l = re.sub(single_line_patterns[k], '".jsonc_{}_comment_{}: \\1"'.format(k, str(uuid.uuid4())), l, count=1)
        lines[i] = l
    lines = '\n'.join(lines).split('\n')
    for i in range(1, len(lines) - 2):
        l = lines[i]
        l_next = lines[i + 1]
        l_strip = l.strip()
        if not l_strip.endswith(',') and not l_strip.endswith('{') and not l_strip.endswith('['):
            if l_next.strip().startswith('"'):
                l = l + ','
        lines[i] = l

    text = '\n'.join(lines)

    invalid_keys = ['jsonc_key', 'jsonc_with_comments', 'jsonc_parent']
    for key in invalid_keys:
        if re.search(f'"{key}"\s*:', text):
            raise KeyError(f'Key "{key}" in not allowed for a JSONCDict')
    data = json.loads(text)
    without_comments = clean_comments(copy.deepcopy(data))

    dict_obj = JSONCDict(**without_comments)
    dict_obj.jsonc_with_comments = data

    return dict_obj

def dumps(data, indent=4, comments=True):
    """
    Write the JSONCDict to a string
    """
    if indent <=0 :
        err = ValueError('Indent value must be greater or equal to 1')
        raise err
    if comments:
        text = json.dumps(data.jsonc_with_comments, indent=indent)
    else:
        text = json.dumps(data, indent=indent)

    # replace single-line c-style comments that are in a map
    text = re.sub(r'"\.jsonc_c_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"\: "(.*)",?', '//\\1', text)
    # replace single-line python-style comments that are in a map
    text = re.sub(r'"\.jsonc_python_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"\: "(.*)",?', '#\\1', text)
    # replace single-line c-style comments that are in a list
    text = re.sub(r'"\.jsonc_c_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\: (.*)",?', '//\\1', text)
    # replace single-line python-style comments that are in a lit
    text = re.sub(r'"\.jsonc_python_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\: (.*)",?', '#\\1', text)

    # replace inline c-style comments that are in a map
    text = re.sub(r'\n\s*"\.jsonc_inline_c_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"\: "(.*)",?', ' //\\1', text)
    # replace inline python-style comments that are in a map
    text = re.sub(r'\n\s*"\.jsonc_inline_python_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"\: "(.*)",?', ' #\\1', text)
    # replace inline c-style comments that are in a list
    text = re.sub(r'\n\s*"\.jsonc_inline_c_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\: (.*)",?', ' //\\1', text)
    # replace inline python-style comments that are in a list
    text = re.sub(r'\n\s*"\.jsonc_inline_python_comment_[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\: (.*)",?', ' #\\1', text)

    lines = text.split('\n')
    for i in range(1, len(lines) - 2):
        l = lines[i]
        l_next = lines[i + 1]
        match = re.search(r'(.*)((?://|#).*)', l)
        if match:
            if l_next.strip().startswith('}') or l_next.strip().startswith(']'):
                if match.group(1).rstrip().endswith(','):
                    parts = match.group(1).split(',')
                    lines[i] = ','.join(parts[:-1]) + parts[-1] + match.group(2)

    text = '\n'.join(lines)

    return text

def dump(data, stream, indent=4, comments=True):
    """
    Write the JSONCDict to a file
    """
    text = dumps(data, indent=indent, comments=comments)
    stream.write(text)

def clean_comments(data):
    if type(data) == dict:
        data = JSONCDict(**{k:clean_comments(data[k]) for k in data if not k.startswith('.jsonc_')})
    elif type(data) == list:
        temp = []
        for x in data:
            if type(x) == str:
                if x.startswith('.jsonc_'): continue
            temp.append(clean_comments(x))
        data = temp
    return data