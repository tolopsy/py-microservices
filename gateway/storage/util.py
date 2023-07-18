import pika, json
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import PERSISTENT_DELIVERY_MODE
from gridfs import GridFS
from werkzeug.datastructures import FileStorage

def upload(f: FileStorage, fs: GridFS, channel: BlockingChannel, access_payload):
    try:
        print("now putting")
        file_id = fs.put(f)
        print("finished putting")
    except Exception as err:
        print(err)
        return "internal server error", 500
    
    message = {
        "video_id": str(file_id),
        "audio_id": None,
        "username": access_payload["username"],
    }

    try:
        print("now publishing")
        # TODO: video routing key should be placed in VIDEO_QUEUE os env
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(err)
        print("inside gateway storage")
        # entry point to initiate exponential backoff
        # and maybe log message in a DLQ or DLX
        # so that it is not forgotten.
        pass