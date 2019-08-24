from flask import Flask, Response, request
from urllib.request import Request as UrlRequest
from urllib.request import urlopen as urlopen

import instrumentation
import time
import json
import random
import uuid

# Configure instrumentation for flask app
app = Flask(__name__)
instrumentation.configure(app, 'message-server')


# Recorder function used to create instrumentation record for the segment.
# response is the object returned by decorated function, options is a dict
# comprising of arguments to decorated function.
def recorder_segment(response, options):
    json_data = response.json
    resp_data = {'id': json_data['notificationid'], 'channel': json_data['channel']}
    searchable_data = {'messageid': options['msgid']}
    non_searchable_data = {'notification': resp_data}
    return instrumentation.Record(searchable=searchable_data,
                                  non_searchable=non_searchable_data)


# Function below is decorated with instrumentation.record specifying a recorder
# function. As the optional segment name is not specified here, instrumentation
# record returned by the recorder is stored in current segment.
@app.route('/dispatch/<msgid>', methods=['POST'])
@instrumentation.record(recorder_segment)
def dispatch(msgid):
    content = request.json
    result = process_message(msgid, content['message'], content['priority'])
    code = random.choice([200, 400, 500])
    return Response(response=json.dumps(result),
                    status=code,
                    mimetype='application/json')


def process_message(msgid, message, priority):
    req = UrlRequest('http://localhost:9000/process/{}'.format(msgid), method='POST')
    trace_id = instrumentation.current_trace_id()
    parent_id = instrumentation.current_segment_id()
    req.add_header('X-Amzn-Trace-Id', 'Root={};Parent={}'.format(trace_id, parent_id))
    urlopen(req).read()
    channel = 'sms' if priority == 'High' else 'email'
    notification_processor = sms_processor if channel == 'sms' else email_processor
    notificationid = notification_processor(msgid, message)
    return {'notificationid': notificationid, 'channel': channel}


@instrumentation.record(subsegment='sms')
def sms_processor(msgid, message):
    print('sending message {} via sms'.format(msgid, message))
    time.sleep(0.5)
    return 'sms:{}'.format(uuid.uuid1())


@instrumentation.record(subsegment='email')
def email_processor(msgid, message):
    print('sending message {} via email'.format(msgid, message))
    time.sleep(0.75)
    return 'email:{}'.format(uuid.uuid1())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=False, threaded=True)
