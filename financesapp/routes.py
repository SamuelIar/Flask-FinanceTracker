from flask import Blueprint, jsonify, render_template, redirect, request, url_for
from financesapp.auth import checkUserLogin, registerNewUser
from financesapp import database_access

mainRoutes = Blueprint('main', __name__)


@mainRoutes.route('/Home')
def home():
    
    # storedData Dictionaty Structure
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
    Accounts = database_access.retrieveAccounts()
    Transactions = database_access.retrieveTransactions()
    Expenses = database_access.retrieveExpenses()
    print("Transactions Amount: ", len(Transactions))
    print("Expenses amount: ", len(Expenses))

    storedData = {
        "Accounts": Accounts,
        "Transactions": Transactions,
        "Expenses": Expenses,
        "TransactionsAndExpenses": Transactions + Expenses
    }
    print("Stored Data:\n",storedData)
    transactionsAndExpenses = {}

    return render_template("Home.html", storedData = storedData)

@mainRoutes.route("/Accounts")
def accounts():
    return render_template("Accounts.html")

@mainRoutes.route("/Graphs")
def graphs():
    return render_template("Graphs.html")

@mainRoutes.route('/')
def index():
    #return render_template("Home.html")
    return redirect(url_for('main.home'))

@mainRoutes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    if checkUserLogin(username, password):
        return
    else:
        return

@mainRoutes.route('/register', methods=['POST'])
def register():
    newUsername = request.json['newUsername']
    newPassword = request.json['newPassword']
    registerNewUser = registerNewUser(newUsername, newPassword)

    if registerNewUser == 0:
        return jsonify({"available": True, "message": "Registration successful!"})
    elif registerNewUser == 1:
        return jsonify({"available": False, "message": "Username unavailable! Please try another username."})
    else:
        return jsonify({"available:": False, "message": "Unknown error."})

@mainRoutes.route("/newTransactionOrExpense", methods=["POST"])
def newTransactionOrExpense():
    account = request.form["account"]
    amount = request.form['amount']
    transactionOrExpense = request.form.get("toggleTransactionExpense")
    if (transactionOrExpense == None): transactionOrExpense = "transaction"
    if (transactionOrExpense == "transaction"):
        type = request.form['transactionType']
    elif (transactionOrExpense == "expense"):
        type = request.form['expenseType']
    else:
        print("Error: Transaction or expense of type ", transactionOrExpense)

    if transactionOrExpense == "transaction":
        database_access.storeTransaction(account, amount, type)
    elif transactionOrExpense == "expense":
        database_access.storeExpense(account, amount, type)
    return redirect(url_for("main.home"))

@mainRoutes.route("/newAccountFromHomePage", methods=["POST"])
def newAccountFromHomePage():
    name = request.form["accountName"]
    type = request.form["accountType"]
    initialBalance = request.form.get("initialBalance")
    if initialBalance == None or initialBalance == '': 
        initialBalance = 0
    else:
        initialBalance = int(initialBalance)
    database_access.createNewAccount(name, type, initialBalance)
    return redirect(url_for("main.home"))

@mainRoutes.route("/deleteDataByID", methods=["DELETE"])
def deleteDataByID():
    data = request.json
    print("Got request to delete data by ID ", data["id"])
    deleteSuccessful = database_access.deleteDataByID(data["id"], data["type"])
    print("Delete Successful: ", deleteSuccessful)
    print("Delete Successful[1]: ", deleteSuccessful[1])
    print(deleteSuccessful[1] == 200)
    if (deleteSuccessful[1] == 200):
        print("In delete successful")
        return jsonify({"message":"Success"}),200
    else:
        print(deleteSuccessful)
        return "Error", 404
    