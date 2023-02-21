import json, os
from pystackql import StackQL 

def basic_instantiation():
    print("# basic instantiation")
    stackql = StackQL()
    print("```")
    print(stackql.version)
    print("```\n")
    print("```")
    stackql.show_properties()
    print("```\n")
    del stackql

def upgrade_stackql():
    print("# upgrade stackql")
    stackql = StackQL()
    print("```")
    print(stackql.version)
    print("```\n")
    print("```")
    stackql.upgrade(showprogress=False)
    print("```\n")
    print("```")
    print(stackql.version)
    print("```\n")
    del stackql

def output_tests():
    print("# output tests\n")

    print("## json output (default)\n")
    stackql = StackQL()
    res = stackql.execute("REGISTRY LIST")
    print("```json")
    print(res)
    print("```\n")
    del stackql

    print("## csv output with headers\n")
    stackql = StackQL(output="csv")
    res = stackql.execute("REGISTRY LIST")
    print("```")
    print(res)
    print("```\n")
    del stackql

    print("## csv output without headers\n")
    stackql = StackQL(output="csv", hideheaders="true")
    res = stackql.execute("REGISTRY LIST")
    print("```")
    print(res)
    print("```\n")
    del stackql

    print("## table output\n")
    stackql = StackQL(output="table")
    res = stackql.execute("REGISTRY LIST")
    print("```")
    print(res)
    print("```\n")
    del stackql

    print("## text output\n")
    stackql = StackQL(output="text")
    res = stackql.execute("REGISTRY LIST")
    print("```")
    print(res)
    print("```\n")
    del stackql

def aws_auth():

    # print("# aws auth as str\n")
    # authstr = 'fred'
    # stackql = StackQL(auth=authstr)
    # res = stackql.execute("")
    # print("```json")
    # print(res)
    # print("```\n")
    # del stackql

    print("# aws auth as dict\n")
    authdict = { 
            'aws': { 
            'credentialsenvvar': 'AWS_SECRET_ACCESS_KEY', 
            'accesskeyidenvvar': 'AWS_ACCESS_KEY_ID', 
            'type': 'aws_signing_v4' 
            } 
        }
    print(json.dumps(authdict))
    stackql = StackQL(auth=authdict)
    res = stackql.execute("REGISTRY PULL aws")
    res = stackql.execute("SELECT instanceState, COUNT(*) as num_instances FROM aws.ec2.instances WHERE region = 'ap-southeast-2' GROUP BY instanceState")
    print("```json")
    print(res)
    print("```\n")
    print("```")
    stackql.show_properties()
    print("```\n")    
    del stackql

# basic_instantiation()
# upgrade_stackql()
# output_tests()
aws_auth()




# iql.()

