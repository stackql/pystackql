import json, os
import pandas as pd
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
    res = stackql.execute("REGISTRY PULL aws")
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

    query = """
SELECT instanceType, COUNT(*) as num_instances
FROM aws.ec2.instances
WHERE region = 'ap-southeast-2'
GROUP BY instanceType
    """

    print("# aws auth as str\n")
    authstr = '{"aws": {"credentialsenvvar": "AWS_SECRET_ACCESS_KEY", "keyIDenvvar": "AWS_ACCESS_KEY_ID", "type": "aws_signing_v4"}}'
    stackql = StackQL(auth=authstr)
    res = stackql.execute(query)
    print("```json")
    print(res)
    print("```\n")
    del stackql

    print("# aws auth as dict\n")
    authdict =  { 
                    "aws": { 
                        "credentialsenvvar": "AWS_SECRET_ACCESS_KEY", 
                        "keyIDenvvar": "AWS_ACCESS_KEY_ID", 
                        "type": "aws_signing_v4" 
                    } 
                }
    stackql = StackQL(auth=authdict)
    res = stackql.execute(query)
    print("```json")
    print(res)
    print("```\n")
    del stackql


    from pystackql import StackQL
    auth = '{"aws": {"credentialsenvvar": "AWS_SECRET_ACCESS_KEY", "keyIDenvvar": "AWS_ACCESS_KEY_ID", "type": "aws_signing_v4"}}'
    region = "ap-southeast-2"
    stackql = StackQL(auth=auth)
    query = "SELECT * FROM aws.ec2.instances WHERE region = '%s'" % (region)
    res = stackql.execute(query)
    df = res.to_dataframe()
    print(df)

def pandas_test():

    region = "ap-southeast-2"
    query = """
SELECT instanceType, COUNT(*) as num_instances
FROM aws.ec2.instances
WHERE region = '%s'
GROUP BY instanceType
    """ % (region)

    print("# basic pandas test\n")
    authstr = '{"aws": {"credentialsenvvar": "AWS_SECRET_ACCESS_KEY", "keyIDenvvar": "AWS_ACCESS_KEY_ID", "type": "aws_signing_v4"}}'
    stackql = StackQL(auth=authstr)
    res = stackql.execute(query)
    df = pd.read_json(res)
    print("```")
    print(df)
    print("```\n")
    del stackql

    regions = ["ap-southeast-2", "us-east-1"]
    query = """
    SELECT '%s' as region, instanceType, COUNT(*) as num_instances
    FROM aws.ec2.instances
    WHERE region = '%s'
    GROUP BY instanceType
    UNION
    SELECT  '%s' as region, instanceType, COUNT(*) as num_instances
    FROM aws.ec2.instances
    WHERE region = '%s'
    GROUP BY instanceType
    """ % (regions[0], regions[0], regions[1], regions[1])

    print("# union test\n")
    authstr = '{"aws": {"credentialsenvvar": "AWS_SECRET_ACCESS_KEY", "keyIDenvvar": "AWS_ACCESS_KEY_ID", "type": "aws_signing_v4"}}'
    stackql = StackQL(auth=authstr)
    res = stackql.execute(query)
    df = pd.read_json(res)
    print("```")
    print(df)
    print("```\n")
    del stackql

    query = """
SELECT split_part(replace(instanceState, ' ', ''),'\n',2) as stateCode,
split_part(replace(instanceState, ' ', ''),'\n',3) as stateName,
COUNT(*) as num_instances 
FROM aws.ec2.instances 
WHERE region = '%s'
GROUP BY split_part(replace(instanceState, ' ', ''),'\n',2),
split_part(replace(instanceState, ' ', ''),'\n',3)
    """ % (region)

    print("# pandas test with builtin functions\n")
    authdict =  { 
                    "aws": { 
                        "credentialsenvvar": "AWS_SECRET_ACCESS_KEY", 
                        "keyIDenvvar": "AWS_ACCESS_KEY_ID", 
                        "type": "aws_signing_v4" 
                    } 
                }
    stackql = StackQL(auth=authdict)
    res = stackql.execute(query)
    df = pd.read_json(res)
    print("```")
    print(df)
    print("```\n")
    del stackql

# basic_instantiation()
# upgrade_stackql()
# output_tests()
# aws_auth()
pandas_test()