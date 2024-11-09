import sqlite3
import random
from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing import Annotated

class CheckOutData(BaseModel):
    card_number: str
    money: str

class NewUserData(BaseModel):
    id: str
    name: str
    password: str

conn = sqlite3.connect('./bank_database', check_same_thread=False)
app = FastAPI()

def init():
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS bank_account (
        USERID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        id TEXT,
        password TEXT,
        card_number TEXT,
        account_number INTEGER,
        money INTEGER)
    ''')
    conn.commit()

# def checkout(data):
#     cur.execute

def generate_unique_account_number():
    cur = conn.cursor()
    while True:
        account_number = int(str(random.randint(100, 999)) + '20' + str(random.randint(100000, 999999)))
        cur.execute("SELECT account_number FROM bank_account WHERE account_number = ?",(account_number,))
        if cur.fetchone() is None:
            return account_number

def generate_unique_card_number():
    cur = conn.cursor()
    while True:
        card_number = int('49061000'+str(random.randint(10000000, 99999999)))
        cur.execute("SELECT card_number FROM bank_account WHERE card_number = ?", (card_number, ))
        if cur.fetchone() is None:
            return card_number

def newuser(data):
    try:
        cur = conn.cursor()
        account_number = generate_unique_account_number()
        card_nubmer = generate_unique_card_number()
        cur.execute("INSERT INTO bank_account (name, id, password, account_number, card_number, money) VALUES (?, ?, ?, ?, ?, ?)", (data.name, data.id, data.password, account_number, card_nubmer, 0))
        conn.commit()
        return 1
    except:
        return 0

@app.post('/newuser')
def _newuser(data: Annotated[NewUserData, Form()]):
    if newuser(data): # 단축 가능
        return {"status":"suceess"}
    else:
        return {"status":"fail"}


@app.post('/checkout')
def _checkout(data: CheckOutData):
    try:
        cur = conn.cursor()
        if cur.execute("SELECT money FROM bank_account WHERE card_number = ?", (data.card_number, )).fetchone()[0] < int(data.money):
            return 0
        cur.execute("UPDATE bank_account SET money = money - ? WHERE card_number = ?", (data.money, data.card_number))
        conn.commit()
        return 1
    except:
        return 0

init()