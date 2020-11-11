import jsonc

with open('test/test.in.jsonc') as f:
    data = jsonc.load(f)

with open('test/test.out.json', 'w') as f:
    jsonc.dump(data, f, indent=2, comments=False)

with open('test/test.out.jsonc', 'w') as f:
    jsonc.dump(data, f, indent=2)