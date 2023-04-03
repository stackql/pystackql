import json, os, sys,time
import psycopg
from psycopg.rows import dict_row
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystackql import StackQL

def connect_and_run_query(query):
    conn = psycopg.connect(
        host="localhost", port=5444,
        autocommit = True,
        row_factory=dict_row
    )
    cur = conn.cursor()
    cur.execute(query)
    res = cur.fetchall()
    print("```")
    print(res)
    print("```\n")
    cur.close()
    conn.close()

def stop_server():
    print("stopping StackQL server...")
    stackql.stop()

print("starting StackQL server...")
stackql = StackQL(server_mode=True)
print("```")
print(stackql.version)
print("```\n")
time.sleep(5)
print("```")
stackql.show_properties()
print("```\n")

connect_and_run_query("REGISTRY LIST")

stop_server()