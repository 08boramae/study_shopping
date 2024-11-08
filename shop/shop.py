import requests
from datetime import datetime
from fastapi import FastAPI, Form, Cookie
from typing import Annotated
from model import model
import jwt
import sqlite3

app = FastAPI()
conn = sqlite3.connect('./database', check_same_thread=False)
SECRET = "VERYSECRETCODEYEAH"

CARD_SERVER_URL = "http://127.0.0.1:10000/"

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
        count INTEGER,
        price INTEGER
        ) 
    ''')
    conn.commit()

def get_userid_from_jwt(session):
    id = jwt.decode(session, SECRET, algorithms=["HS256"])["id"]
    return id

def add_cart(data, session):
    try:
        cur = conn.cursor()
        id = get_userid_from_jwt(session)
        cur.execute("INSERT INTO cart (id, item, count, price) VALUES (?, ?, ?, ?) ON CONFLICT(item) DO UPDATE SET count = count + excluded.count and price = price + (price * excluded.count)", (id, data.product_id, data.count, product_list[data.product_id-1]["price"] * data.count))
        conn.commit()
        return 1
    except:
        return 0

product_list = [
    {"name": "고구마", "product_id": 1, "price":3000},
    {"name": "딸기", "product_id": 2, "price":5000},
    {"name": "떡볶이", "product_id": 3, "price":7000}
]

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

def checkout(session, card_number):
    try:
        cur = conn.cursor()
        id = get_userid_from_jwt(session)
        cur.execute("SELECT price FROM cart WHERE id=?", (id, ))
        res = cur.fetchall()
        total_price = 0
        for i in res:
            total_price += i[0]
        res_s = requests.post(CARD_SERVER_URL + "checkout", json={"card_number":str(card_number), "money":str(total_price)}).text
        print(res_s)
        if res_s == "1":
            return 1
        else:
            return 0
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

@app.post('/checkout')
def _checkout(SESSION: str | None = Cookie(default=None)):
    if checkout(SESSION, 4906100054532729):
        return {"status":"success"}
    else:
        return {"status":"fail"}


init()