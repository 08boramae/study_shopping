from fastapi import FastAPI, Form, Cookie
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime, timedelta
import random
import jwt
import sqlite3

conn = sqlite3.connect('./database', check_same_thread=False)
SECRET = "VERYSECRETCODEYEAH"

app = FastAPI()

class idpw(BaseModel):
    name: str
    password: str

class register_data(BaseModel):
    name: str
    id: str
    password: str

class transfer(BaseModel):
    target: str
    money: int

def init():
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS account (
                    USERID INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    id TEXT UNIQUE,
                    password TEXT,
                    account_number INTEGER UNIQUE,
                    money INTEGER
                )''')
    # cur.execute('''CREATE TABLE IF NOT EXISTS available_account_numbers (
    #                 account_number INTEGER UNIQUE,
    #                 used BOOLEAN DEFAULT 0
    #             )''')
    conn.commit()

def generate_unique_account_number():
    cur = conn.cursor()
    while True:
        account_number = int(str(random.randint(100, 999)) + '20' + str(random.randint(100000, 999999)))
        cur.execute("SELECT account_number FROM account WHERE account_number = ?",

                    (account_number,))
        if cur.fetchone() is None:
            return account_number

def register(data):
    try:
        cur = conn.cursor()
        account_number = generate_unique_account_number()
        print(account_number)
        cur.execute("INSERT INTO account (name, id, password, account_number, money) VALUES (?, ?, ?, ?, ?)", (data.name, data.id, data.password, account_number, 0))
        conn.commit()
        return 1
    except:
        print("EXC")
        return 0


def login(data):
    cur = conn.cursor()
    cur.execute("SELECT USERID FROM account WHERE name=? and password=?", (data.name, data.password))
    res = cur.fetchone()
    if res:
        return 1
    else:
        return 0

def create_new_session(data):
    zulu = datetime.utcnow()
    jwt_data = {"name": data.name, "password": data.password, "exp": zulu + timedelta(minutes=10)}
    session = jwt.encode(jwt_data, SECRET, algorithm="HS256")
    return session

def check_session(session):
    try:
        jwt_data = jwt.decode(session, SECRET, algorithms=["HS256"])
        return 1
    except:
        return 0

def transfer_money(data, originname):
    cur = conn.cursor()
    # if current money < target money
    if cur.execute("SELECT money FROM account WHERE name = ?", (originname,)).fetchone()[0] < data.money:
        return 0
    cur.execute("UPDATE account SET money = money - ? WHERE name = ?", (data.money, originname))
    cur.execute("UPDATE account SET money = money + ? WHERE account_number = ?", (data.money, data.target))
    conn.commit()
    return 1

def get_information(sesison):
    cur = conn.cursor()
    name = jwt.decode(sesison, SECRET, algorithms=["HS256"])["name"]
    cur.execute("SELECT account_number, money FROM account WHERE name = ?", (name,))
    account_number, money = cur.fetchone()
    return {"status": "success", "account_number": account_number, "money": money}

@app.post('/login')
def _login(data: Annotated[idpw, Form()]):
    if login(data):
        jwt = create_new_session(data)
        return {"status": "success", "session": jwt}
    else:
        return {"status": "fail"}

@app.post('/register')
def _register(data: Annotated[register_data, Form()]):
    if register(data):
        return {"status": "success"}
    else:
        return {"status": "fail"}

@app.get('/information')
def _information(SESSION: str | None = Cookie(default=None)):
    if check_session(SESSION):
        return get_information(SESSION)
    else:
        return {"status": "fail"}

@app.post('/transfer')
def _transfer(data: Annotated[transfer, Form()], SESSION: str | None = Cookie(default=None)):
    # get user name
    originname = jwt.decode(SESSION, SECRET, algorithms=["HS256"])["name"]
    if transfer_money(data, originname):
        return {"status": "success"}
    else:
        return {"status": "fail"}

init()