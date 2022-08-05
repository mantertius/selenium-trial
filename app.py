from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from datetime import date as dt
from main import pipeline

class Driver(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('date', required=True)

        args = parser.parse_args()
       

        date = args['date']

        if date == 'hoje':
            today = dt.today()
            date = today.strftime("%d/%m/%Y")
    
        notfound, done = pipeline(date)
        notfound = dict(notfound)
        done = dict(done)
        return {'notfound':notfound}, 200        
    

app = Flask(__name__)
api = Api(app)

@app.route('/ecg/inserir',methods=['POST','GET'])
def inserir():
    if request.method == 'POST':
        json = request.json
        date = json['date']
        
        if date == 'hoje':
                today = dt.today()
                date = today.strftime("%d/%m/%Y")
        
        notfound, done = pipeline(date)
        notfound = dict(notfound)
        done = dict(done)
        return {'notfound':notfound}, 200
    else:
        today = dt.today()
        date = today.strftime("%d/%m/%Y")
        notfound, done = pipeline(date)
        notfound = dict(notfound)
        done = dict(done)
        return {'notfound':notfound, 'done':done}, 200


#api.add_resource(Driver,'/ecg/inserir')

if __name__ == '__main__':
    notfound = []
    finalizado_name = []
    finalizado_path = {}
    app.run(debug=True)