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
RET_TRANSACTIONS = {
    'sum': 0,
    'avg': 0,
    'max': 0,
    'min': 0,
    'count': 0
}
START_TIME = datetime.datetime.now()

def datetime_to_mili(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def subtract_sec(timestamp, time_now):
    dt_timestamp = datetime.datetime.fromtimestamp(timestamp/1000.)
    timedelta_elapsed = time_now - dt_timestamp
    secs = timedelta_elapsed.total_seconds()

    return int(secs)

def count():
    prev = datetime.datetime.now()
    now = datetime.datetime.now()
    diff = prev - now

    # wait until time difference = 1
    while (diff.total_seconds() < 60):
        now = datetime.datetime.now()
        diff = prev - now

    now = datetime_to_mili(now)

    if now in STATISTICS:
        stat = STATISTICS[now]

        sum_stat = stat['sum']
        avg = stat['avg']
        max_stat = stat['max']
        min_stat = stat['min']
        count_stat = stat['count']

        sum_ret = RET_TRANSACTIONS['sum']
        max_ret = RET_TRANSACTIONS['max']
        min_ret = RET_TRANSACTIONS['min']
        count_ret = RET_TRANSACTIONS['count']

        # remove data from return transactions
        RET_TRANSACTIONS['sum'] = sum_ret - sum_stat
        RET_TRANSACTIONS['avg'] = (sum_ret - sum_stat) / count_ret
        RET_TRANSACTIONS['max'] = max(max_ret, max_stat)
        RET_TRANSACTIONS['min'] = min(min_ret, min_stat)
        RET_TRANSACTIONS['count'] = count_ret - count_stat

# executor = ThreadPoolExecutor(4)
# executor.submit(count)


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
            sum_stat = STATISTICS[timestamp]['sum'] + amount
            count = STATISTICS[timestamp]['count']

            STATISTICS[timestamp] = {
                'sum': sum_stat,
                'avg': sum_stat / count,
                'max': max(STATISTICS[timestamp]['max'], amount),
                'min': min(STATISTICS[timestamp]['min'], amount),
                'count': count
            }

        if RET_TRANSACTIONS['count'] != 0:
            count = RET_TRANSACTIONS['count']
            sum_ret = RET_TRANSACTIONS['sum']

            RET_TRANSACTIONS['sum'] = amount
            RET_TRANSACTIONS['avg'] = (sum_ret + amount) / count
            RET_TRANSACTIONS['max'] = max(RET_TRANSACTIONS['max'], amount)
            RET_TRANSACTIONS['min'] = min(RET_TRANSACTIONS['min'], amount)
            RET_TRANSACTIONS['count'] = count + 1
        else:
            RET_TRANSACTIONS['sum'] = amount
            RET_TRANSACTIONS['avg'] = amount
            RET_TRANSACTIONS['max'] = amount
            RET_TRANSACTIONS['min'] = amount
            RET_TRANSACTIONS['count'] = 1

        if (sec > 60):
            return '', 204
        else:
            return '', 201


class Statistics(Resource):
    def get(self):
        start = datetime.datetime.now()
        end = start - datetime.timedelta(minutes=1)

        for time_mili, data in STATISTICS.items():
            converted_time = datetime.datetime.fromtimestamp(time_mili/1000.)

            if converted_time < end:
                sum_ret = RET_TRANSACTIONS['sum']
                count_ret = RET_TRANSACTIONS['count']
                max_ret = RET_TRANSACTIONS['max']
                min_ret = RET_TRANSACTIONS['min']

                sum_data = data['sum']
                count_data = data['count']

                RET_TRANSACTIONS['sum'] = sum_data + sum_ret
                RET_TRANSACTIONS['avg'] = (sum_data + sum_ret) / (count_ret + count_data)
                RET_TRANSACTIONS['max'] = max(max_ret, data['max'])
                RET_TRANSACTIONS['min'] = min(min_ret, data['min'])
                RET_TRANSACTIONS['count'] = count_ret + count_data

        return jsonify(RET_TRANSACTIONS)


api.add_resource(Transactions, '/transactions')
api.add_resource(Statistics, '/statistics')

if __name__ == '__main__':
    app.run(port='5000', debug=True)
