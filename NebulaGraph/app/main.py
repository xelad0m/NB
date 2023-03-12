# python 3.10+
import os

from fastapi import FastAPI

from dotenv import load_dotenv                          # pip install python-dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))              # выставляет переменные окружения из файла


from db import rest, neighbours, reachable              # теперь можно подключиться


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI"}


@app.get("/api/neighbours")
def read_neighbours(full_name: str):

    return {"full_name": full_name, "neighbours": rest(neighbours(full_name))}


@app.get("/api/reachable")
def read_reachable(full_name: str):
    
    return {"full_name": full_name, "reachable": rest(reachable(full_name))}