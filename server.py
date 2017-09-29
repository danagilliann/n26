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

STATISTICS = {}
RETURN_TRANSACTIONS = {
    'sum': 0,
    'avg': 0,
    'max': 0,
    'min': 0,
    'count': 0
}
START_TIME = datetime.datetime.now()

def hello():
    print('hello')

def subtract_sec(timestamp, time_now):
    dt_timestamp = datetime.datetime.fromtimestamp(timestamp/1000.)
    timedelta_elapsed = time_now - dt_timestamp
    secs = timedelta_elapsed.total_seconds()

    return int(secs)

def count():
    epoch = datetime.datetime.utcfromtimestamp(0)
    prev = datetime.datetime.now()
    now = datetime.datetime.now()
    diff = prev - now

    print('hello!')
    # wait until time difference = 1
    while (diff.total_seconds() < 60):
        now = datetime.datetime.now()
        diff = prev - now

    mili_now = (now - epoch).total_seconds() * 1000.0

    if now in STATISTICS:
        stat = STATISTICS[now]

        sum_stat = stat['sum']
        avg = stat['avg']
        max_stat = stat['max']
        min_stat = stat['min']
        count_stat = stat['count']

        sum_ret = RETURN_TRANSACTIONS['sum']
        max_ret = RETURN_TRANSACTIONS['max']
        min_ret = RETURN_TRANSACTIONS['min']
        count_ret = RETURN_TRANSACTIONS['count']

        # remove data from return transactions
        RETURN_TRANSACTIONS['sum'] = sum_ret - sum_stat
        RETURN_TRANSACTIONS['avg'] = (sum_ret - sum_stat) / count_ret
        RETURN_TRANSACTIONS['max'] = max(max_ret, max_stat)
        RETURN_TRANSACTIONS['min'] = min(min_ret, min_stat)
        RETURN_TRANSACTIONS['count'] = count_ret - count_stat

class Transactions(Resource):
    def put(self):
        # print(request.form['data'])
        amount = int(request.form['amount'])
        timestamp = int(request.form['timestamp'])

        sec = subtract_sec(timestamp, datetime.datetime.now())

        if timestamp not in STATISTICS:
            STATISTICS[timestamp] = {
                'sum': amount,
                'avg': amount,
                'max': amount,
                'min': amount,
                'count': 1
            }
        else:
            sum_stat = STATISTICS[timestamp]['amount'] + amount
            count = STATISTICS[timestamp]['count']

            STATISTICS[timestamp] = {
                'sum': sum_stat,
                'avg': sum_stat / count,
                'max': max(STATISTICS[timestamp]['max'], amount),
                'min': min(STATISTICS[timestamp]['min'], amount),
                'count': count
            }

        if RETURN_TRANSACTIONS['count'] != 0:
            count = RETURN_TRANSACTIONS['count']
            sum_ret = RETURN_TRANSACTIONS['sum']

            RETURN_TRANSACTIONS['sum'] = amount
            RETURN_TRANSACTIONS['avg'] = (sum_ret + amount) / count
            RETURN_TRANSACTIONS['max'] = max(RETURN_TRANSACTIONS['max'], amount)
            RETURN_TRANSACTIONS['min'] = min(RETURN_TRANSACTIONS['min'], amount)
            RETURN_TRANSACTIONS['count'] = count + 1
        else:
            RETURN_TRANSACTIONS['sum'] = amount
            RETURN_TRANSACTIONS['avg'] = amount
            RETURN_TRANSACTIONS['max'] = amount
            RETURN_TRANSACTIONS['min'] = amount
            RETURN_TRANSACTIONS['count'] = 1

        if (sec > 60):
            return '', 204
        else:
            return '', 201


class Statistics(Resource):
    def get(self):
        start = datetime.datetime.now()
        end = start + datetime.timedelta(minutes=1)

        return jsonify(RETURN_TRANSACTIONS)

api.add_resource(Transactions, '/transactions')
api.add_resource(Statistics, '/statistics')

if __name__ == '__main__':
    executor = ThreadPoolExecutor(4)
    executor.submit(count)
    app.run(port='5000', debug=True)
