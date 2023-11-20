import psycopg2
from psycopg2 import sql
from flask import jsonify

import os

userDatabase = {
    'dbname': 'userdata',
    'user':os.getenv("USERNAME") or os.getenv("USER"),
    'password':'Password1234',
    'host':'localhost',
    'port':5432
}


def storeTransaction(account, amount, type):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            queryAccountID = sql.SQL("SELECT accountID FROM Accounts WHERE accountname = %s")
            storeTransaction = sql.SQL("INSERT INTO Transactions (accountid, amount, type) VALUES (%s, %s, %s)")
            cur.execute(queryAccountID, (account,))
            accountID = cur.fetchall()[0]
            cur.execute(storeTransaction, (accountID, amount, type))

def storeExpense(account, amount, type):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            queryAccountID = sql.SQL("SELECT accountID FROM Accounts WHERE accountname = %s")
            storeTransactions = sql.SQL("INSERT INTO Expenses (accountid, amount, type) VALUES (%s, %s, %s)")
            cur.execute(queryAccountID, (account,))
            accountID = cur.fetchall()[0]
            cur.execute(storeTransactions, (accountID, amount, type))

# Data Retrieval Formats of Other Script Which Uses These Functions
    '''storedData = {
        "Accounts":[{
            "AccountName":"",
            "accountType":"",
            "AccountBalance":0,
        }, ],
        "Transactions":[{
            "Amount":0,
            "Type":"",
            "Datetime":""
        }],
        "Expenses":[{
            "Amount":0,
            "Type":"",
            "Datetime":""
        }]
    }'''

def sortTransactionsAndExpenses():
    return

def retrieveAccounts():
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT accountName, accountType, accountBalance FROM Accounts")
            queryResults = cur.fetchall()
            returnResults = []
            for account in queryResults:
                returnResults.append({
                    "Name":account[0],
                    "Type":account[1],
                    "Balance":account[2]
                })
            return queryResults

def retrieveTransactions():
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT transactionid, type, amount FROM Transactions")
            queryResults = cur.fetchall()
            returnResults = []
            for transaction in queryResults:
                returnResults.append({
                    "id":transaction[0],
                    "type":transaction[1],
                    "amount":transaction[2]#,
                    #"datetime":transaction[2]
                })
            return returnResults

def retrieveExpenses():
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT type, amount FROM Expenses")
            queryResults = cur.fetchall()
            returnResults = []
            for expense in queryResults:
                returnResults.append({
                    "type":expense[0],
                    "amount":expense[1]#,
                    #"datetime":expense[2]
                })

def deleteDataByID(id, dataType):
    print("ID: ", id)
    print("Data Type: ", dataType)
    try:
        print("Data Type Again: " + dataType)
        with psycopg2.connect(**userDatabase) as conn:
            with conn.cursor() as cur:
                columnName = dataType[0:-1]+"id"
                deleteQuery = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
                    sql.Identifier(dataType),
                    sql.Identifier(columnName)
                )
                cur.execute(deleteQuery, [id])
        return "success",200

    except Exception as e:
        print(e)
        return "Error ", 404

def createNewAccount(name, type, balance):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("INSERT INTO Accounts (accountname, accounttype, accountbalance) VALUES (%s, %s, %s)")
            cur.execute(query, (name, type, balance))
