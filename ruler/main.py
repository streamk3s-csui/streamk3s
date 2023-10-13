import logging

from flask import Flask, request
import MongoDB

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)



@app.route('/submit', methods=['POST'])
def submit():
    content = request.json
    MongoDB.insert(content)
    message = "received"
    logging.info(content)
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3003', debug=True)
