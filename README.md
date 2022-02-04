# pystackql - Python Library for StackQL

![Platform Support](https://img.shields.io/badge/platform-windows%20macos%20linux-brightgreen)
![Python Support](https://img.shields.io/badge/python-3.6%2B-brightgreen)

Python wrapper for [StackQL](https://stackql.io)

## Usage

```python
from pystackql import StackQL  
iql = StackQL(keyfilepath='/tmp/pystackql-demo.json')
results = iql.execute("SHOW SERVICES IN google")
print(results)
```

if the StackQL binary is not in the system path you can explicitly specify this using the `exe` argument of the `StackQL` constructor method, for example:

```python
from pystackql import StackQL  
iql = StackQL(exe='/some/other/path/stackql', keyfilepath='/tmp/infraql-demo.json')
```