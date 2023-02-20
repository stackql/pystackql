import json
from pystackql import StackQL 
iql= StackQL()

# iql.show_properties()

# iql.upgrade()

res = iql.execute("REGISTRY LIST")
print(res)
