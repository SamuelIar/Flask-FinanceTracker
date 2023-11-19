from flask import Flask
from . import routes

import psycopg2
from psycopg2 import sql

import os

userDatabase = {
    'dbname': 'userdata',
    'user':os.getenv("USERNAME") or os.getenv("USER"),
    'password':'Password1234',
    'host':'localhost',
    'port':5432
}

defaultDatabase = userDatabase.copy()
defaultDatabase['dbname'] = "postgres"

def createApp():
    
    app = Flask(__name__)
    app.register_blueprint(routes.mainRoutes)

    
    # Comment out below for it to work in it's current state
    
    # Database Setup
    newDatabase = checkDatabase()
    #if newDatabase:
    #    return # <- Remove this return
        ####################
        #
        # If new database, HTML window pop-up
        # Text-form, asks for user username
        # Accept username
        # Send to userAccounts table, username column
        #
        ####################
    #else:
    #    return # <- Remove this return
        ####################
        #
        # Retrieve user table from database
        #   Retrieve backgroundPreference
        #   Retrieve complimentColor
        #   Retrieve homeTimeframe  
        #   Retrieve Accounts where userID is the same as this user's userID
        #   Retrieve transactions where transaction accountID is in user's accountIDs, and where transaction timeframe is within homeTimeframe
        #       Serve homepage  
        #    
        ####################
    # Flask Routes (between HTML pages) Setup
    return app              


def checkDatabase():
    #   Pop-up HTML window with text-field
    databaseCheckQuery = "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename = %s)"
    defaultCheckQuery = "SELECT EXISTS(SELECT 1 FROM userdata WHERE %s)"
    defaultAddQuery = "ALTER TABLE %s ADD COLUMN %s"
    with psycopg2.connect(**defaultDatabase) as conn:
        with conn.cursor() as cur:
            # Check if database exists, create it if it doesnt. Doesn't create tables!
            databaseExists = userDataCheck(conn, cur, databaseCheckQuery)
            print(databaseExists)
    
    print(databaseExists)

    if not databaseExists:
        createDatabase(defaultDatabase)

    with psycopg2.connect(**userDatabase) as conn:
        with conn.cursor() as cur:
            # Check if each table exists, if it doesn't, create each table and row independently
            # Done this way to facilitate possible future updates, potentially
            # needing to store more data, or cut down on data stored depending
            # on new features implemented. (Not sure if this is best practice,
            # but for our project, with various database schema updates, it works)
            userAccountsCheck(cur)
            accountsCheck(cur)
            transactionsCheck(cur)
            expensesCheck(cur)
    return
   
def userDataCheck(conn, cursor, checkQuery):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = %s)",("userdata",))
    exists = cursor.fetchone()[0]
    return exists

def createDatabase(databaseParams):
    
    conn = psycopg2.connect(**databaseParams)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE UserData"))
    
    finally:
        conn.close()
    
def userAccountsCheck(cursor):
    # Query table existence
    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'useraccounts')")
    tableExists = cursor.fetchone()[0]
    if not tableExists:
        cursor.execute("CREATE TYPE timeframe AS ENUM('daily', 'weekly', 'bi-weekly', 'monthly');")
        cursor.execute("CREATE TABLE UserAccounts (userID SERIAL PRIMARY KEY, userName VARCHAR(24), password varchar(24), homeTimeframe timeframe DEFAULT 'weekly', backgroundColor CHAR(7), complimentColor CHAR(7))")

def accountsCheck(cursor):
    
    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'accounts')")
    tableExists = cursor.fetchone()[0]
    if not tableExists:
        # cursor.execute("Will need to be added to add custom enum types for account types, if necessary")
        cursor.execute("CREATE TABLE Accounts (accountID SERIAL PRIMARY KEY, userID INTEGER REFERENCES UserAccounts(userID), accountName VARCHAR(24), accountType VARCHAR(24), accountBalance INT)")

def transactionsCheck(cursor):

    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'transactions')")
    tableExists = cursor.fetchone()[0]

    if not tableExists:
        cursor.execute("CREATE TYPE transactionType AS ENUM('work', 'gift', 'account transfer', 'other');")
        cursor.execute("CREATE TABLE Transactions(transactionID SERIAL PRIMARY KEY, accountID INTEGER REFERENCES Accounts(accountID), amount INT, type transactionType DEFAULT 'other')")

def expensesCheck(cursor):
    cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'expenses')")
    tableExists = cursor.fetchone()[0]

    if not tableExists:
        cursor.execute("CREATE TYPE expenseType AS ENUM('other', 'food', 'gas', 'bills', 'housing and accomodations');")
        cursor.execute("CREATE TABLE Expenses(expenseID SERIAL PRIMARY KEY, accountID INTEGER REFERENCES Accounts(accountID), amount INT, type expenseType DEFAULT 'other')")

# OLD
def userDataCreate(connParams):
    conn = psycopg2.connect(**connParams)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            print("Started database setup")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("userData")))
            cur.execute(sql.SQL("CREATE TABLE Transactions(TransactionID int, AccountName VARCHAR(24), TransactionType VARCHAR(24), Amount INT, Date DATE)"))
            cur.execute(sql.SQL("CREATE TABLE Accounts(User VARCHAR(64), AccountName VARCHAR(24), AccountType VARCHAR(24), AccountBalance INT)"))
            cur.execute(sql.SQL("CREATE TABLE Users(Name VARCHAR(64), )")) 
            print("Completed database setup")

    finally:
        conn.close()