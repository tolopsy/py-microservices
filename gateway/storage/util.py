import pika, json, os
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import PERSISTENT_DELIVERY_MODE
from gridfs import GridFS
from werkzeug.datastructures import FileStorage

VIDEO_QUEUE = os.environ["VIDEO_QUEUE"]

def upload(f: FileStorage, fs: GridFS, channel: BlockingChannel, access_payload):
    try:
        file_id = fs.put(f)
    except Exception as err:
        return err
    
    message = {
        "video_id": str(file_id),
        "audio_id": None,
        "username": access_payload["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key=VIDEO_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        # entry point to initiate exponential backoff
        # and maybe log message in a DLQ or DLX
        # so that it is not forgotten.
        return err