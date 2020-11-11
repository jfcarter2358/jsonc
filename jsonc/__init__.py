import json
import re
import urllib.parse
import difflib

__version__ = '0.0.2'

_hdr_pat = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")
_no_eol = "\ No newline at end of file"

class JSONCDict(dict):
    def __init__(self, *args, **kwargs):
        super(JSONCDict, self).__init__(*args, **kwargs)
        self.with_comments = ''
        self.without_comments = ''
        self.comment_diff = ''

    def __setitem__(self, key, value):
        super(JSONCDict, self).__setitem__(key, value)
        self.refresh()

    def __delitem__(self, key):
        super(JSONCDict, self).__delitem__(key)
        self.refresh()

    def clear():
        super(JSONCDict, self).clear()
        self.without_comments = '{}'
        self.with_comments = '{}'
        self.comment_diff = ''

    def refresh(self):
        data = {key: self[key] for key in self}
        new_without_comments = json.dumps(data, indent=4)
        diff = self.make_patch(new_without_comments, self.without_comments)
        merged_diff = self.merge_diff(diff, self.comment_diff)
        new_with_comments = self.apply_patch(new_without_comments, merged_diff)
        self.without_comments = new_without_comments
        self.with_comments = new_with_comments
        self.comment_diff = self.make_patch(self.without_comments, new_with_comments)

    def make_patch(self, a, b):
        """
        Get unified string diff between two strings. Trims top two lines.
        Returns empty string if strings are identical.
        """
        diffs = difflib.unified_diff(a.splitlines(True), b.splitlines(True), n=0)
        try: 
            _,_ = next(diffs), next(diffs)
        except StopIteration: 
            pass
        return ''.join([d if d[-1] == '\n' else d + '\n' + _no_eol + '\n' for d in diffs])

    def apply_patch(self, s, patch, revert=False):
        """
        Apply unified diff patch to string s to recover newer string.
        If revert is True, treat s as the newer string, recover older string.
        """
        s = s.splitlines(True)
        p = patch.splitlines(True)
        t = ''
        i = sl = 0
        (midx,sign) = (1,'+') if not revert else (3,'-')
        while i < len(p) and p[i].startswith(("---","+++")): 
            i += 1 # skip header lines
        while i < len(p):
            m = _hdr_pat.match(p[i])
            if not m: 
                raise Exception("Cannot process diff")
            i += 1
            l = int(m.group(midx)) - 1 + (m.group(midx+1) == '0')
            t += ''.join(s[sl:l])
            sl = l
            while i < len(p) and p[i][0] != '@':
                if i+1 < len(p) and p[i+1][0] == '\\': 
                    line = p[i][:-1]
                    i += 2
                else: 
                    line = p[i]
                    i += 1
                if len(line) > 0:
                    if line[0] == sign or line[0] == ' ': 
                        t += line[1:]
                    sl += (line[0] != sign)
        t += ''.join(s[sl:])
        return t

    def get_diff_changes(self, diff):
        p = diff.splitlines(True)
        i = 0
        (midx,sign) = (1,'+')
        diff_changes = []
        while i < len(p) and p[i].startswith(("---","+++")): i += 1 # skip header lines
        while i < len(p):
            m = _hdr_pat.match(p[i])
            if not m: 
                raise Exception("Cannot process diff")
            i += 1
            diff_changes.append(list(m.groups()))
            while i < len(p) and p[i][0] != '@':
                if i+1 < len(p) and p[i+1][0] == '\\': 
                    line = p[i][:-1]
                    i += 2
                else: 
                    line = p[i]
                    i += 1

        return diff_changes

    def merge_diff(self, d1, d2):
        d1_changes = self.get_diff_changes(d1)
        old_d2_changes = self.get_diff_changes(d2)
        new_d2_changes = self.get_diff_changes(d2)

        for i in range(0, len(d1_changes)):
            for j in range(0, 4):
                if d1_changes[i][j] == None:
                    d1_changes[i][j] = 1
        for i in range(0, len(new_d2_changes)):
            for j in range(0, 4):
                if old_d2_changes[i][j] == None:
                    old_d2_changes[i][j] = 1
                if new_d2_changes[i][j] == None:
                    new_d2_changes[i][j] = 1

        for i in range(0, len(d1_changes)):
            for j in range(0, len(new_d2_changes)):
                if d1_changes[i][0] < new_d2_changes[j][0]:
                    if d1_changes[i][3] != None and d1_changes[i][1] != None:
                        new_d2_changes[j][2] = str(int(new_d2_changes[j][2]) + int(d1_changes[i][1]) - int(d1_changes[i][3]))
                        new_d2_changes[j][0] = str(int(new_d2_changes[j][0]) + int(d1_changes[i][1]) - int(d1_changes[i][3]))

        old_change_strings = []
        new_change_strings = []

        for change in old_d2_changes:
            old_change_strings.append(self.rebuild_change_str(change))
        for change in new_d2_changes:
            new_change_strings.append(self.rebuild_change_str(change))
            
        for i in range(0, len(new_change_strings)):
            d2 = d2.replace(old_change_strings[i], new_change_strings[i])

        return d2

    def rebuild_change_str(self, change):
        if change[1] != 1:
            part_1 = '{},{}'.format(change[0], change[1])
        else:
            part_1 = change[0]
        if change[3] != 1:
            part_2 = '{},{}'.format(change[2], change[3])
        else:
            part_2 = change[2]

        out = '@@ -{} +{} @@'.format(part_1, part_2)
        return out


def load(stream):
    data = stream.read()
    return loads(data)

def loads(text):
    inline_pattern = re.compile(r'[ \t]*\/\/(.*)')
    multiline_pattern = re.compile(r'[ \t]*\/\*(((?!\/\*).)|\n|\r)*\*\/')

    no_comments = re.sub(inline_pattern, '', text)
    no_comments = re.sub(multiline_pattern, '', no_comments)
    json_obj = json.loads(no_comments)

    dict_obj = JSONCDict(**json_obj)
    dict_obj.without_comments = json.dumps(json_obj, indent=4)
    dict_obj.with_comments = text
    dict_obj.comment_diff = dict_obj.make_patch(dict_obj.without_comments, text)

    with open('comment_diff.txt', 'w') as f:
        f.write(dict_obj.comment_diff)

    return dict_obj

def dumps(data):
    return data.with_comments

def dump(data, stream):
    text = dumps(data, indent=4)
    stream.write(text)