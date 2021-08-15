import jsonc

with open('test/test.in.jsonc') as f:
    data = jsonc.load(f)
data['bar']['h'] = 'foo'
data['foo'].append('bar')
data['hello'] = 'foo'
# print(data['foo'])
# print(data['foo'][3])
data['foo'][3]['c'] = 'hello world'
# print(data['foo'])
# print(data)

print('Test 1')
assert(data['hello'] == 'foo')
print('Test 2')
assert(data['foo'][4] == 'bar')
print('Test 3')
assert(data['foo'][3]['c'] == 'hello world')

with open('test/test.out.json', 'w') as f:
    jsonc.dump(data, f, indent=4, comments=False)

with open('test/test.out.jsonc', 'w') as f:
    jsonc.dump(data, f, indent=4)

loads_data = jsonc.loads("""{"key":"value"}""")
print('Test 4')
assert(loads_data['key'] == 'value')

print('Test 5')
success = False
try:
    loads_data = jsonc.loads("""{"jsonc_key":"value"}""")
except:
    success = True
assert(success)

print('Test 6')
success = False
try:
    loads_data = jsonc.loads("""{"jsonc_with_comments":"value"}""")
except:
    success = True
assert(success)

print('Test 7')
success = False
try:
    loads_data = jsonc.loads("""{"jsonc_parent":"value"}""")
except:
    success = True
assert(success)

set_data = jsonc.JSONCDict()
print('Test 8')
success = False
try:
    loads_data = jsonc.loads("""{"jsonc_key":"value"}""")
except:
    success = True
assert(success)

print('Test 9')
success = False
try:
    loads_data = jsonc.loads("""{"jsonc_with_comments":"value"}""")
except:
    success = True
assert(success)

print('Test 10')
success = False
try:
    set_data['jsonc_key'] = 'value'
except:
    success = True
assert(success)

print('Test 11')
success = False
try:
    set_data['jsonc_with_comments'] = 'value'
except:
    success = True
assert(success)

print('Test 12')
try:
    set_data['jsonc_parent'] = 'value'
except:
    success = True
assert(success)

print('All tests passed')