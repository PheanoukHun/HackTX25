from flask import Flask, jsonify

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

if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode