'''
To run:
    FLASK_APP=hello.py flask run
'''
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# convert stock csv to json format
def toJson(data): 
        json = {}

        for line in data:
                json[line[0]] = {
                        'Open' : line[1],
                        'High' : line[2],
                        'Low' : line[3],
                        'Close' : line[4],
                        'AdjVol' : line[5], 
                        'Vol' : line[6], 
                }
        return json

# read json, convert to csv, and write to file
def toCsv(json): 
        csv = "Date,Open,High,Low,Close,Adjacency Volume,Volume\n"
        for element in json:
                csv += element + ',' + json[element]['Open'] + ',' + json[element]['High'] + ',' + json[element]['Low'] + ',' + json[element]['Close'] + ',' + json[element]['AdjVol'] + ',' + json[element]['Vol'] +'\n'
        f1 = open('../../AAPL.csv', 'w')
        f1.write(csv)
        f1.close()
        print(csv)
        return csv

# read file and return matrix in list format
def rawData():
        f1 = open('../../AAPL.csv', 'r') # put AAPL.csv in ../ instead of ../../
        s1 = f1.readlines()
        f1.close()

        s1 = s1[1:len(s1)]
        for i in range(len(s1)): 
                s1[i] = s1[i].split(',')
                rowSize = len(s1[i])
                s1[i][6] = s1[i][rowSize-1][0:len(s1[i][rowSize-1])-1] # trim \n from end of line
        return s1

@app.route('/getData/<date>', methods=['GET'])
@app.route('/getData', methods=['GET', 'POST'])
def getData(date = None):
        if request.method == 'GET':
                data = toJson(rawData())

                # no parameter
                if date == None:
                        return data
                # has parameter
                else:
                        if date in data:
                                return data[date]
                        else:
                                return 'Input Not Valid'
        # POST Method
        elif request.method == 'POST':
                start = request.json['start']
                end = request.json['end']
                
                data = rawData()
                
                i = 1
                curDate = data[0][0]
                # find first occurence
                while (curDate!=start and i < len(data)):
                        curDate = data[i][0]
                        i+=1

                # add start to list
                inRange = [data[i-1]]
                # append until end of list or end of range is found
                while (curDate!=end and i < len(data)):
                        curDate = data[i][0]
                        inRange.append(data[i])
                        i+=1
                print("Start: " + start + " End: " + end)
                print(toJson(inRange))
                return toJson(inRange)

@app.route('/addData', methods=['POST'])
# append data to end
def addData():
        data = toJson(rawData())
        for newData in request.json:
                if newData not in data: 
                        data[newData] = request.json[newData]
        return toCsv(data)

@app.route('/calculate10DayAverage', methods=['GET'])
# based on closing prices
# uses rawData() to parse end of list
def calc10Day():
        data = rawData()
        if len(data) >= 10:
                tenDays = data[len(data)-10:len(data)]
        else:
                tenDays = data

        sum = 0
        for i in range(len(tenDays)):
                sum += float(tenDays[i][4])
        return str(sum/len(tenDays))

@app.route('/updateData', methods=['PUT'])
# Can be used as addData
def updateData():
        # Convert to json for ease of access
        data = toJson(rawData())
        # reset old data per each element in payload
        for newData in request.json:
                if newData in data:
                        data[newData] = request.json[newData]
        # rewrite file
        return toCsv(data)


@app.route('/deleteData', methods=['DELETE'])
# delete data with given date
def deleteData():
        # convert to json
        data = toJson(rawData())
        # delete entry
        del data[request.json['Date']]
        # rewrite file
        return toCsv(data)

if __name__ == '__main__':
        app.run()
