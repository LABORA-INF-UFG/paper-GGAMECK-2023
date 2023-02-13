from flask import Flask,request,json
import pprint
import json

TRIGGER_ALLERT = 'ContainerCpuUsage'

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Webhook for trigger optimization'

#Code to receive alert
@app.route('/alert',methods=['POST'])
def alert():
    data = request.json
    pprint.pprint(data)
    for i in data['alerts']:   
        if i['labels']['alertname'] == TRIGGER_ALLERT:
            print('Alert to call optimization')
            #TODO: Call optimization 

#Code to validate json input and extract alert
def read_json():
    with open('alert-example.json') as json_file:
        data = json.load(json_file)
        pprint.pprint(data)
    for i in data['alerts']:   
        if i['labels']['alertname'] == TRIGGER_ALLERT:
            print('ALERT FIRED')

#Main method
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
    #read_json()