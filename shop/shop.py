from fastapi import FastAPI, Form
from typing import Annotated
from model import model
import sqlite3

app = FastAPI()
conn = sqlite3.connect('./database', check_same_thread=False)

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
        USERID INTEGER,
        item INTEGER,
        count INTEGER
        ) 
    ''')
    conn.commit()

def add_cart(data):
    cur = conn.cursor()
    # userid =
    # TODO : USERID 찾아서 넣기, JWT 기반
    cur.execute("INSERT INTO cart (userid, item, count) VALUES (?, ?, ?)", (userid, data.id, data.count))

product_list = {
    1: "딸기",
    2: "고구마",
    3: "떡볶이"
}

# TODO : LOGIN/REGISTER 만들기. 만들어졌을 때 bank 에서도 만들어져야할것이다?

@app.get('/list')
def _list():
    return product_list

@app.post('/addcart')
def _addcart(data: Annotated[model.AddProductAtCart, Form()]):
    # TODO

    return 1
init()