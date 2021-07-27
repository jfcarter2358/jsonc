import jsonc

with open('test/test.in.jsonc') as f:
    data = jsonc.load(f)
data['bar']['h'] = 'foo'
data['foo'].append('bar')
data['hello'] = 'foo'
print(data['foo'])
print(data['foo'][3])
data['foo'][3]['c'] = 'hello world'
print(data['foo'])
print(data)

with open('test/test.out.json', 'w') as f:
    jsonc.dump(data, f, indent=4, comments=False)

with open('test/test.out.jsonc', 'w') as f:
    jsonc.dump(data, f, indent=4)

assert(data['hello'] == 'foo')
assert(data['foo'][4] == 'bar')
assert(data['foo'][3]['c'] == 'hello world')