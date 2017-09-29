import time
import datetime
import json
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask.ext.jsonpify import jsonify

db_conn = create_engine('sqlite:///n26.db')
app = Flask(__name__)
api = Api(app)

RETURN_TRANSACTIONS = {
    'sum': 0,
    'avg': 0,
    'max': 0,
    'min': 0,
    'count': 0
}
START_TIME = datetime.datetime.now()

def get_seconds(timestamp, time_now):
    dt_timestamp = datetime.datetime.fromtimestamp(timestamp/1000.)
    timedelta_elapsed = time_now - dt_timestamp
    secs = timedelta_elapsed.total_seconds()

    return int(secs)

@app.route('/')
def count():
    return 'hello'

class Transactions(Resource):
    def put(self):
        QUERY = '''INSERT INTO statistics (AMOUNT, SEC) VALUES ({amount}, {sec})'''
        # print(request.form['data'])
        amount = request.form['amount']
        timestamp = request.form['timestamp']

        sec = get_seconds(int(timestamp), datetime.datetime.now())

        conn = db_conn.connect()
        conn.execute(QUERY.format(amount=amount, sec=sec))

        if (sec > 60):
            return '', 204
        else:
            return '', 201




class Statistics(Resource):
    def get(self):
        conn = db_conn.connect()
        # query
        # result
        result = {
            "sum": 1000,
            "avg": 100,
            "max": 200,
            "min": 50,
            "count": 10
        }

        return jsonify(result)

api.add_resource(Transactions, '/transactions')
api.add_resource(Statistics, '/statistics')

if __name__ == '__main__':
    app.run(port='5000')
