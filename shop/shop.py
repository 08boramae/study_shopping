from datetime import datetime, timedelta

from dns.dnssecalgs import algorithms
from fastapi import FastAPI, Form, Cookie
from typing import Annotated
from model import model
import jwt
import sqlite3

app = FastAPI()
conn = sqlite3.connect('./database', check_same_thread=False)
SECRET = "VERYSECRETCODEYEAH"

def init():
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS shop_account (
        USERID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        id TEXT UNIQUE,
        password TEXT);
        ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cart(
        id TEXT,
        item INTEGER UNIQUE,
        count INTEGER
        ) 
    ''')
    conn.commit()

def add_cart(data, session):
    try:
        cur = conn.cursor()
        id = jwt.decode(session, SECRET, algorithms=["HS256"])["id"] # TODO : JWT 구조에 따라 id 가져오기
        cur.execute("INSERT INTO cart (id, item, count) VALUES (?, ?, ?) ON CONFLICT(item) DO UPDATE SET count = count + excluded.count", (id, data.product_id, data.count))
        conn.commit()
        return 1
    except:
        return 0

product_list = {
    1: "딸기",
    2: "고구마",
    3: "떡볶이"
}

def create_new_session(id):
    zulu = datetime.utcnow()
    # payload = {"id": id, "exp": zulu + timedelta(minutes=10)}
    payload = {"id": id}
    session = jwt.encode(payload, SECRET, algorithm="HS256")
    return session

def validate_user(login_data):
    cur = conn.cursor()
    cur.execute("SELECT USERID FROM shop_account WHERE id=? and password=?", (login_data.id, login_data.password))
    res = cur.fetchone()
    if res:
        return 1
    else:
        return 0

def validate_session(token):
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
        return 1
    except:
        return 0

def create_user(user_data):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO shop_account (name, id, password) VALUES (?, ?, ?)", (user_data.name, user_data.id, user_data.password))
        conn.commit()
        return 1
    except:
        print("EXC")
        return 0

@app.post('/login')
def _login(data: Annotated[model.Login, Form()]):
    if validate_user(data):
        return {"status":"success", "session": create_new_session(data.id)}
    else:
        return {"status":"fail"}

@app.post('/register')
def _register(data: Annotated[model.Signup, Form()]):
    if create_user(data):
        return {"status":"success"}
    else:
        return {"status":"fail"}

@app.get('/list')
def _list(SESSION: str | None = Cookie(default=None)):
    if validate_session(SESSION):
        return {"status":"success", "product_list":product_list}
    else:
        return {"status":"fail"}

@app.post('/addcart')
def _addcart(data: Annotated[model.AddProductAtCart, Form(),], SESSION: str | None = Cookie(default=None)):
    if add_cart(data, SESSION):
        return {"status":"success"}
    else:
        return {"status":"fail"}


init()