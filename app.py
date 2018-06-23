# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests
import pymongo
import datetime
import random

from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from pymongo import MongoClient

Base = declarative_base()

# ---------------- General Functions needed for parts of the Webhook -----------------------

#The following method/function is used for logging inside a MongoDB
def logThis(jsonobject):
    client = MongoClient('mongodb://webhook:test1234@ds163700.mlab.com:63700/heroku_7v64g95t')
    db=client.heroku_7v64g95t
    collection=db.logs
    tempstring = json.dumps(jsonobject)
    new_json = json.loads(tempstring, object_hook=remove_dot_key)
    collection.insert(new_json)

#This is used to remove any dots from the keys in the JSON, because that's not allowed in MongoDB (we're using 3.4.x, it would be allowed in 3.6.1 but pymongo would still not allow for it...)
def remove_dot_key(obj):
    for key in obj.keys():
        new_key = key.replace(".","")
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj

class obj(Base):
    __tablename__ = 'sessions'
    session_id = Column(String, primary_key=True)
    aorb = Column(String)

def getAB(session_dialogflow):
    engine = create_engine('postgres://gfrntxrxeqrjve:4114c77276ac0b99b4618a9670b84b08d5e9ee05e311ff11a95c721cb27d117d@ec2-54-247-100-44.eu-west-1.compute.amazonaws.com:5432/d2lhs9sdnsr655')
    connection = engine.connect()
    AorB = connection.execute('select * from sessions where session_id=' + "'" + session_dialogflow + "'")
    print(AorB)
    if AorB is None:
        return "Error"
    else:
        rows_count = 0
        for row in AorB:
            rows_count += 1
        if not rows_count:
            decision = bool(random.getrandbits(1))
            print(decision)
            if decision is True:
                Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)
                sess = Session()
                A = obj(session_id=session_dialogflow, aorb='A')
                sess.add(A)
                connection.close()
                return 'A'
            else:
                Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)
                sess = Session()
                B= obj(session_id=session_dialogflow, aorb='B')
                sess.add(B)
                connection.close()
                return 'B'
        else:
            for row in AorB:
                col = "aorb"
                returnString = row[col]
            return returnString

# ------------------------------ Actual Webhook work starts from here ------------------------------------------

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print("Response:")
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    
    return r

def processRequest(req):
    req['datetime'] = str(datetime.datetime.now())
    stringwithsession = req["queryResult"]["outputContexts"][0]["name"]
    session_dialogflow = stringwithsession[0:77]
    print(session_dialogflow)
    ABtest = getAB(session_dialogflow)

    logThis(req)
    intent = req["queryResult"]["intent"]["displayName"]
    print(intent)

    if intent == "Default Welcome Intent":
       if ABtest == "A":
        return {
            "fulfillmentText": "Hello World A",
            "source": "webhook-EH"
        }
       if ABtest == "B":
            return {
                "fulfillmentText": "Hello World B",
                "source": "webhook-EH"
            }

    else:
        return{}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')