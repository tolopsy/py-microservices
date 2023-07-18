import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth_svc import access, validate
from storage import util


server = Flask(__name__)

server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"
# server.config["MONGO_URI"] = "mongodb://localhost:27017/videos"

mongo = PyMongo(server)
print(mongo.cx.server_info())

fs = gridfs.GridFS(mongo.db)

queue_conn = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
# queue_conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))

print(f"{queue_conn.is_open} is rabbitmq state")
channel = queue_conn.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if err:
        return err
    
    return token, 200


@server.route("/upload", methods=["POST"])
def upload():
    access_payload, err = validate.auth_header(request)

    if err:
        return err
    
    try:
        access_payload = json.loads(access_payload)
    except Exception as err:
        print(err)
        # should log exception here since we expect a json formatted response
        # from auth service if auth header is validated.
        return "something went wrong", 500

    if not access_payload["admin"]:
        return "not authorized", 403
    
    if len(request.files) != 1:
        return "exactly 1 file required", 400

    for _, f in request.files.items():
        print(f)
        print("that was file")
        err = util.upload(f, fs, channel, access_payload)
        if err:
            print(err)
            return err
    
    return "successful upload", 200


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    print("olorunagbaye")
    server.run(host="0.0.0.0", port=8080, debug=True)
