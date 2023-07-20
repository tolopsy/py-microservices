import gridfs, pika, json, sys
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth_svc import access, validate
from storage import util
from bson.objectid import ObjectId


server = Flask(__name__)

mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/video")
mongo_audio = PyMongo(server, uri="mongodb://host.minikube.internal:27017/audio")

# Affirm connections
try:
    mongo_video.db.command("ping")
    mongo_audio.db.command("ping")
except:
    sys.exit("mongodb not connected")

try:
    queue_conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", heartbeat=0))
except:
    sys.exit("could not connect to queue broker")



fs_video = gridfs.GridFS(mongo_video.db)
fs_audio = gridfs.GridFS(mongo_audio.db)
channel = queue_conn.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if err:
        return err
    
    return token, 200

@server.route("/signup", methods=["POST"])
def signup():
    msg, err = access.signup(request)
    if err:
        return err
    
    return msg, 200


@server.route("/upload", methods=["POST"])
def upload():
    access_payload, err_response = validate.auth_header(request)

    if err_response:
        return err_response
    
    try:
        access_payload = json.loads(access_payload)
    except Exception as err:
        print(err)
        return "something went wrong", 500

    if not access_payload["can_convert"]:
        return "not authorized", 403
    
    if len(request.files) != 1:
        return "exactly 1 file required", 400

    for _, f in request.files.items():
        err = util.upload(f, fs_video, channel, access_payload)
        if err:
            print(err)
            return "internal server error", 500
    
    return "successful upload", 200


@server.route("/download", methods=["GET"])
def download():
    access_payload, err = validate.auth_header(request)

    if err:
        return err
    
    try:
        access_payload = json.loads(access_payload)
    except Exception as err:
        print(err)
        return "something went wrong", 500

    if not access_payload["can_convert"]:
        return "not authorized", 403

    file_id = request.args.get("file_id")
    if not file_id:
        return "file_id is required", 400
    
    try:
        out = fs_audio.get(ObjectId(file_id))
        return send_file(out, download_name=f"{file_id}.mp3")
    except Exception as err:
        print(f"error while getting file from db and sending to user: {err}")
        return "internal server error", 500



# TODO: All printed errors should be properly logged

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
