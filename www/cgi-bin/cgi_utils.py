import json


def send_response(data, return_code):
    resp = {
        'response': data,
        'return_code': return_code
    }

    print "Content-type: application/json\r\n\r\n";
    print json.dumps(resp)