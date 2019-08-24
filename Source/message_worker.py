from flask import Flask, Response, request

import instrumentation
import time
import json
import random

# Configure instrumentation for flask app
app = Flask(__name__)
instrumentation.configure(app, 'message-worker')


@app.route('/process/<msgid>', methods=['POST'])
def process(msgid):
    time.sleep(random.choice([0.1, 0.2, 0.5, 1.0]))
    result = {'errors': 0, 'msgid': msgid}
    return Response(response=json.dumps(result),
                    status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9000', debug=False, threaded=True)
1