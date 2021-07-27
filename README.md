# JSONC

## Install

```
pip install jsoncparser
```

## Getting Started

To use JSONC, add the following import statement to your code

```python
import jsonc
```

You can then use the four functions below to interact with your jsonc file and data

```
jsonc.load(file)
jsonc.loads(str)
jsonc.dumps(JSONCDict)
jsonc.dump(JSONCDict, file)
```

In addition, you can access the dictionary _with_ stored comments by using

```
data_dict = JSONCDict()
data_dict.with_comments
```

