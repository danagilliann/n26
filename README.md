This is a Flask App. It currently runs on Debug mode. To run enter the following command:

```
$ export FLASK_DEBUG=1
$ FLASK_APP=server.py flask run
```

/transactions operates at O(1)
/statistics operates at O(N)

Initially I had a plan to run count() as a background task to "clean up" `RET_TRANSACTIONS` as the seconds of the app passed. Unfortunately, I had trouble making it work with the `ThreadPoolExecutor`.
