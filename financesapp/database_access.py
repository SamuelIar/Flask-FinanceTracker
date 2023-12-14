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


def storeTransaction(user, account, amount, type, datetime):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            queryAccountID = sql.SQL("SELECT accountID FROM Accounts WHERE accountname = %s AND userid IN (SELECT userid FROM useraccounts WHERE username = %s)")
            storeTransaction = sql.SQL("INSERT INTO Transactions (accountid, amount, type, datetime) VALUES (%s, %s, %s, %s)")
            cur.execute(queryAccountID, (account,user,))
            accountID = cur.fetchall()[0]
            cur.execute(storeTransaction, (accountID, amount, type, datetime))

def storeExpense(user, account, amount, type, datetime):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            queryAccountID = sql.SQL("SELECT accountID FROM Accounts WHERE accountname = %s AND userID IN (SELECT userid FROM useraccounts WHERE username = %s)")
            storeTransactions = sql.SQL("INSERT INTO Expenses (accountid, amount, type, datetime) VALUES (%s, %s, %s, %s)")
            cur.execute(queryAccountID, (account,user,))
            accountID = cur.fetchall()[0]
            cur.execute(storeTransactions, (accountID, amount, type, datetime))

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

def retrieveUserData(username):
    if(username == None): return []

    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT username, hometimeframe, primarycolor, secondarycolor FROM useraccounts WHERE username = %s;")
            cur.execute(query, (username,))
            queryResults = cur.fetchall()[0]
            returnResults = {
                "Username":queryResults[0],
                "homeTimeframe":queryResults[1],
                "displayColorPrimary":queryResults[2],
                "displayColorSecondary":queryResults[3]
            }
            print("Query Results: ",returnResults)
            return returnResults

def updateUserData(username, homeTimeFrame, primaryColor, secondaryColor):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("UPDATE useraccounts SET hometimeframe = %s, primarycolor = %s, secondarycolor = %s WHERE username = %s;")
            cur.execute(query, (homeTimeFrame, primaryColor, secondaryColor, username))
                

def retrieveAccounts(username):
    # If no user logged in, return no data
    if(username == None): return []

    # Otherwise, retrieve data
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT accountName, accountType, accountBalance FROM accounts WHERE userid IN (SELECT userid FROM useraccounts WHERE username = %s)")
            cur.execute(query, (username,))
            queryResults = cur.fetchall()
            returnResults = []
            for account in queryResults:
                returnResults.append({
                    "Name":account[0],
                    "Type":account[1],
                    "Balance":account[2]
                })
            return queryResults

def retrieveTransactions(username):
    # If no user logged in, return no data
    if (username == None): return []
    
    # Otherwise return data
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT transactionid, type, amount FROM Transactions WHERE accountid IN (SELECT accountid FROM accounts WHERE userid IN (SELECT userid FROM useraccounts WHERE username = %s))")
            cur.execute(query, (username,))
            queryResults = cur.fetchall()
            returnResults = []
            for transaction in queryResults:
                returnResults.append({
                    "id":transaction[0],
                    "type":transaction[1],
                    "amount":transaction[2],
                    "tOrE":"t"#,
                    #"datetime":transaction[3]
                })
    return returnResults

def retrieveExpenses(username):
    # If no user logged in, return no data
    if (username == None): return []

    # Otherwise return data
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT expenseid, type, amount FROM Expenses WHERE accountid IN (SELECT accountid FROM accounts WHERE userid IN (SELECT userid FROM useraccounts WHERE username = %s))")
            cur.execute(query, (username,))
            queryResults = cur.fetchall()
            returnResults = []
            for expense in queryResults:
                returnResults.append({
                    'id':expense[0],
                    "type":expense[1],
                    "amount":expense[2],
                    "tOrE":"e"#,
                    #"datetime":expense[3]
                })
    return returnResults

def deleteDataByID(id, dataType):
    # THIS IS INSECURE! Vulnerable to SQL injection (or something akin to it)
    # User could modify their webpage and send request to delete data by id for ids not
    # available to their user account
    # Will fix it! Later though
    try:
        with psycopg2.connect(**userDatabase) as conn:
            with conn.cursor() as cur:
                columnName = dataType[0:-1]+"id"
                # DELETE FROM (Transactions|Expenses) WHERE (transactionID|expenseID) = [expenseID]
                # Done with .format() because psycopg2 reads %s as placeholders for data values, not SQL identifiers
                # %s cannot be used for table and column names
                deleteQuery = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
                    sql.Identifier(dataType),
                    sql.Identifier(columnName)
                )
                cur.execute(deleteQuery, (id,))
        print("Data should be deleted successfully")
        return "success",200

    except Exception as e:
        print(e)
        return "Error ", 404

def createNewAccount(name, type, balance, username):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT userid FROM useraccounts WHERE username = %s")
            cur.execute(query, (username,))
            userID = cur.fetchall()[0]
            query = sql.SQL("INSERT INTO Accounts (userid, accountname, accounttype, accountbalance) VALUES (%s, %s, %s, %s)")
            cur.execute(query, (userID, name, type, balance))

def registerNewUser(name, password):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT * FROM useraccounts WHERE username = %s")
            cur.execute(query, (name,))
            if cur.fetchall():
                return 1
            query = sql.SQL("INSERT INTO useraccounts (username, password) VALUES (%s, %s)")
            cur.execute(query, (name, password,))
    return 0

def authenticateUser(username, password):
    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT password FROM useraccounts WHERE username = %s")
            cur.execute(query, (username,))
            try:
                queryResults = cur.fetchall()[0][0]
            except IndexError:
                queryResults = None
            if queryResults == password:
                return 0
            else:
                return 1