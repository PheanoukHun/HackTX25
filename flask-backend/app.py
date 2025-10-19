from flask import Flask, jsonify
import requests
import json

class CustomerProfile():
    def __init__(self, name, age, employment, city, monthlyIncome, monthlyExpense, totalDebt, creditScore, totalAmountInAccount, financialGoal):
        self.name = name
        self.age = age
        self.employment  = employment
        self.city = city
        self.monthlyIncome = monthlyIncome
        self.monthlyExpense = monthlyExpense
        self.totalDebt = totalDebt
        self.creditScore = creditScore
        self.totalAmountInAccount = totalAmountInAccount
        self.financialGoal = financialGoal
    
    def getCustomerProfile(self):
        data = {
            "name": self.name,
            "age": self.age,
            "employment": self.employment,
            "city": self.city,
            "income": self.monthlyIncome,
            "expenses": self.monthlyExpense,
            "shouldPayDebt": self.shouldPayOffDebt(),
            "totalDebt": self.totalDebt,
            "totalAmountInAccount": self.totalAmountInAccount,
            "netIncome" : self.getNetIncome(),
            "financialGoal": self.financialGoal
        }
        
        # 2. Write dictionary to a JSON file
        with open("../../db/customerProfile.json", "w") as file:
            json.dump(data, file, indent=4)
    
    def getNetIncome(self):
        return self.monthlyIncome - self.monthlyExpense
    
    def shouldPayOffDebt(self):
        if (self.monthlyIncome - self.monthlyExpense > 0):
            return 1
        else:
            return 0

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/api/data')
def get_data():
    data = {
        'message': 'This is some data from the API!',
        'status': 'success'
    }
    return jsonify(data)  # Return data as JSON

@app.route('/api/submit', methods=['POST'])
def submit_data():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body
        name = data.get('name')
        email = data.get('email')

        # Process the data (e.g., save to a database)
        print(f"Received data: Name={name}, Email={email}")

        return jsonify({'message': 'Data received successfully!'}), 201  # 201 Created

if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode