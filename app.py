
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from ast import literal_eval
import json
from pymongo import MongoClient
import os
import re

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins":"*"}})
client=MongoClient("mongodb+srv://shaktichaturvedi33073:itkahs@cluster0.7cepdv6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db=client.get_database('text_editor')

@app.route("/signup", methods=["GET", "POST"])
def Signup():
    if request.method == 'POST':
        user_input = request.data
        user_input=literal_eval(user_input.decode('utf-8'))
        # print(user_input["user"]["email"])
        # print(type(json.loads(user_input["user"])))
        user_input=json.loads(user_input["user"])
        print(user_input)
        # Check if the email is already registered
        #  print(collection.find_one({"_id": ObjectId("59d7ef576cab3d6118805a20")}))
        
        existing_user = db.user.find_one({'email': user_input["email"]})
        
        if existing_user:
            return jsonify({'message': 'Email already exists'}), 400
        try:
           db.user.insert_one({"name":user_input["name"],"email":user_input["email"], "password":user_input["password"]})
        except Exception as e:
            return "Error in db"
        return jsonify({'message': 'Registration successful'}), 200


@app.route("/login", methods=["GET", "POST"])
def Login():

    if request.method == 'POST':
        user_input = request.data
        user_input=literal_eval(user_input.decode('utf-8'))
       
        
        existing_user = db.user.find_one({'email': user_input["user"]["email"]})
        
        if not existing_user:
            return jsonify({'message': 'No Email exists'}), 400
        
        
        user_db=db.user.find_one({"email":user_input["user"]["email"]})
        
        if user_db['password']==user_input["user"]["password"]:
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}),401


@app.route("/chatbot", methods=["POST"])
def Chatbot():
    message=request.json.get("message")
    print(message)
    message=message.lower()
    ans={"return policy": "You can return the product within 7 days of purchase",
    "order status":"Your order is on the way",
    "cancel order":"You can cancel the order within 24 hours of purchase",
    "payment method":"We accept all types of payment methods",
    "contact":"You can contact us at 1234567890"}
    response=ans.get(message,"I am sorry, I did not understand that")
    print(response)
    return jsonify({"response": response})


@app.route("/form", methods=["POST"])
def Help():
    user_input=request.data
    user_input=literal_eval(user_input.decode('utf-8'))
    db.user_contact.insert_one(({"name":user_input["name"],"email":user_input["email"], "message":user_input["message"]}))
    return jsonify({"message": "successfully submitted"}),  200


def get_collection(collection_name):
    return db[collection_name]

@app.route('/products/<collection_name>', methods=['GET'])
def get_products_by_collection(collection_name):
    collection = get_collection(collection_name)
    products = list(collection.find())
    for product in products:
        product["_id"] = str(product["_id"])
    return jsonify(products), 200


@app.route('/products/search', methods=['GET'])
def search_products():
    query=request.args.get('q',"")
    collection=['men', 'women', 'kids', 'shirt', 'beauty']
    if query in collection:
        clc=get_collection(query)
        products = list(clc.find())
        for product in products:
            product["_id"] = str(product["_id"])
        return jsonify(products), 200

    return jsonify('sorry not found'), 200


@app.route('/api/addresses', methods=['GET'])
def get_addresses():
    addresses = db.addresses.find()
    result = []
    for address in addresses:
        result.append({
            '_id': str(address['_id']),
            'name': address['name'],
            'mobile': address['mobile'],
            'street': address['street'],
            'pinCode': address['pinCode'],
            'city': address['city'],
            'state': address['state']
        })
    return jsonify(result)

@app.route('/api/addresses', methods=['POST'])
def add_address():
    data = request.get_json()
    # print(data)
    address_id = db.addresses.insert_one({
        'name': data['name'],
        'mobile': data['mobile'],
        'street': data['street'],
        'pinCode': data['pinCode'],
        'city': data['city'],
        'state': data['state']
    }).inserted_id
    new_address = db.addresses.find_one({'_id': address_id})
    result = {
        '_id': str(new_address['_id']),
        'name': new_address['name'],
        'mobile': new_address['mobile'],
        'street': new_address['street'],
        'pinCode': new_address['pinCode'],
        'city': new_address['city'],
        'state': new_address['state']
    }
    return jsonify(result), 201


   




if __name__=="__main__":
    app.run(debug=True)



