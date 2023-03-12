import os
import pandas as pd

from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool



# адрес и порт graphd сервиса
HOST = "127.0.0.1"      
PORT = 9669

USER = os.environ.get('DATABASE_USER')
PASS = os.environ.get('DATABASE_PASS')

SPACE = "relations"   # схема данных


config = Config()
config.max_connection_pool_size = 10

# init connection pool
connection_pool = ConnectionPool()

# the graphd server's address
connection_pool.init([(HOST, PORT)], config)



def rest(query, conn=connection_pool):
    """Запрос к БД на языке NGQL"""

    with conn.session_context(USER, PASS) as session:
        session.execute(f"USE {SPACE};")
        result = session.execute(query)
        if not result.is_succeeded():
            return []
    
    names = []
    if result.column_values("connected"):
        for node in [x.cast() for x in result.column_values("connected")][0]:
            names.append(node.prop_values("person")[0].cast())
        names = names[1:] # исключить саму вершину

    return names



def neighbours(name):
    """Вершины, смежные для name"""

    return f"MATCH p = (v)-[r*1]->() WHERE v.person.name == '{name}' WITH v, nodes(p) AS n UNWIND n AS n1 RETURN id(v) AS vid, collect(DISTINCT n1) AS connected;"


def reachable(name):
    """Вершины, достижимые из name"""
    
    return f"MATCH p = (v)-[r*1..]->() WHERE v.person.name == '{name}' WITH v, nodes(p) AS n UNWIND n AS n1 RETURN id(v) AS vid, collect(DISTINCT n1) AS connected;"
