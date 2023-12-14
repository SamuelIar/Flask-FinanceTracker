from flask import Blueprint, jsonify, render_template, redirect, request, session, url_for
from financesapp import auth
from financesapp import database_access
from datetime import date

mainRoutes = Blueprint('main', __name__)

@mainRoutes.route('/Home')
def home():
   
    username = session.get("username")
    #if(username is not None):
    #    print("Username is not none!")
    if(username is None):
        User = []
        Accounts = []
        Transactions = []
        Expenses = []
    else:
        try:
            User = database_access.retrieveUserData(username)
            Accounts = database_access.retrieveAccounts(username)
            Transactions = database_access.retrieveTransactions(username)
            Expenses = database_access.retrieveExpenses(username)
        except IndexError:
            session.pop("username")
            User = []
            Accounts = []
            Transactions = []
            Expenses = []

    storedData = {
        "User": User,
        "Accounts": Accounts,
        "Transactions": Transactions,
        "Expenses": Expenses,
        "TransactionsAndExpenses": Transactions + Expenses
    }

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
    
    username = request.json['username']
    password = request.json['password']
    
    authenticationSuccessful = database_access.authenticateUser(username, password)

    match authenticationSuccessful:
        case 0:
            session['username'] = username
            return jsonify({'status':'success','message':'Login successful!'})
        case 404 | 1 | _:
            return jsonify({'status':'error','message':'We could not log you in with those credentials. Please try again.'})
            

    # Cleansing user input to prevent SQL insertion
    #username = re.sub('r\W+', '', username)
    #password = re.sub('r\W+', '', password)
    #if(auth.authenticateUser(username, password)):
    #    session['user']=username
    #    redirect(url_for('main.home', username=username))
    ##else()
    #else:
    #    return jsonify({"message":"Unauthorized"}), 401

@mainRoutes.route('/register', methods=['POST'])
def register():
    newUsername = request.json['newUsername']
    newPassword = request.json['newPassword']
    ### ADD USER INPUT SANITATION!!!
    print("New Username", newUsername)
    print("New Password", newPassword)


    registerNewUserSuccessful = database_access.registerNewUser(newUsername, newPassword)

    if registerNewUserSuccessful == 0:
        return jsonify({"status": "success", "message": "Registration successful!"})
    elif registerNewUserSuccessful == 1:
        return jsonify({"status": "error", "message": "Username unavailable! Please try another username."})
    else:
        return jsonify({"status": "error", "message": "Unknown error."})

@mainRoutes.route('/updateUserSettings', methods=['POST'])
def updateUserSettings():
    timeframe = request.form["homeTimeframe"]
    displayColorPrimary = request.form["displayColorPrimary"]
    displayColorSecondary = request.form["displayColorSecondary"]

    database_access.updateUserData(session["username"], timeframe, displayColorPrimary, displayColorSecondary)
    print("Timeframe: ", timeframe)
    print("displayColorPrimary: ", displayColorPrimary)
    print("displayColorSecondary: ", displayColorSecondary)

    return redirect(url_for("main.home"))

@mainRoutes.route("/newTransactionOrExpense", methods=["POST"])
def newTransactionOrExpense():
    account = request.form["account"]
    amount = request.form['amount']
    datetime = request.form["transactionDate"] + " " + request.form["transactionTime"]
    transactionOrExpense = request.form.get("toggleTransactionExpense")
    if (transactionOrExpense == None): transactionOrExpense = "transaction"
    if (transactionOrExpense == "transaction"):
        type = request.form['transactionType']
    elif (transactionOrExpense == "expense"):
        type = request.form['expenseType']
    else:
        print("Error: Transaction or expense of type ", transactionOrExpense)

    username = session.get("username")

    if transactionOrExpense == "transaction":
        database_access.storeTransaction(username, account, amount, type, datetime)
    elif transactionOrExpense == "expense":
        database_access.storeExpense(username, account, amount, type, datetime)
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
    database_access.createNewAccount(name, type, initialBalance, session["username"])
    return redirect(url_for("main.home"))

@mainRoutes.route("/deleteDataByID", methods=["DELETE"])
def deleteDataByID():
    data = request.json
    deleteSuccessful = database_access.deleteDataByID(data["id"], data["type"])
    if (deleteSuccessful[1] == 200):
        return jsonify({"message":"Success"}),200
    else:
        print(deleteSuccessful)
        return "Error", 404
    
@mainRoutes.route("/logout", methods=['POST'])
def logout():
    try:
        session.pop('username', None)
        return jsonify({"status": "success", "message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": e})