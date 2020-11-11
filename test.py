import jsonc

with open('test.jsonc') as f:
    data = jsonc.load(f)

with open('test.json', 'w') as f:
    f.write(data.without_comments)

with open('test.out.jsonc', 'w') as f:
    jsonc.dump(data, f)