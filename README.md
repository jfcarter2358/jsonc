# JSONC

## Getting Started

To use JSONC, add the following import statement to your code

```python
import jsonc
```

You can then use the four functions below to interact with your jsonc file and data

```
jsonc.load(file)
jsonc.loads(str)
jsonc.dump(JSONCDict)
jsonc.dumps(JSONCDict, file)
```

In addition, you can accesss the raw JSON string without comments by using

```
data_dict = JSONCDict()
data_dict.without_comments
```

and you can access the string _with_ comments by using

```
data_dict = JSONCDict()
data_dict.with_comments
```

