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
            storeTransactions = sql.SQL("INSERT INTO Transactions (accountid, amount, type) VALUES (%s, %s, %s)")
            cur.execute(queryAccountID, (account,))
            accountID = cur.fetchall()[0]
            cur.execute(storeTransaction, (accountID, amount, type))

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
                    "transactionid":transaction[0],
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
    try:
        with psycopg2.connect(**userDatabase) as conn:
            with conn.cursor() as cur:
                deleteQuery = sql.SQL("DELETE FROM %s WHERE %s=%s")
                match dataType:
                    case "UserAccount":
                        cur.execute(deleteQuery, (dataType, "UserAccountID", id))
                    case "Account":
                        cur.execute(deleteQuery, (dataType, "AccountID", id))
                    case "Transaction":
                        cur.execute(deleteQuery, (dataType, "TransactionID", id))
                    case "Expense":
                        cur.execute(deleteQuery, (dataType, "transactionID", id))
        return jsonify({"message":"success"}),200

    except:
        return jsonify({"message":"Item not found"}),404

def createNewAccount(name, type, balance):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("INSERT INTO Accounts (accountname, accounttype, accountbalance) VALUES (%s, %s, %s)")
            cur.execute(query, (name, type, balance))
