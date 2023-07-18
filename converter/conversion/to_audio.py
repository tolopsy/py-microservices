import pika, json, tempfile, os
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import PERSISTENT_DELIVERY_MODE
from bson.objectid import ObjectId
from gridfs import GridFS
import moviepy.editor
from utils import AUDIO_QUEUE


def start(message, fs_video: GridFS, fs_audio: GridFS, channel: BlockingChannel):
    message = json.loads(message)
    video_id = message["video_id"]

    # write video from db into temporary file
    tf = tempfile.NamedTemporaryFile()
    out = fs_video.get(ObjectId(video_id))
    tf.write(out.read())

    # convert video into audio
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # writes audio file to a new temporary file path
    audio_tf_path = "{tempfile_dir}/{video_id}.mp3".format(
        tempfile_dir=tempfile.gettempdir(),
        video_id=video_id
    )
    try:
        audio.write_audiofile(audio_tf_path)
    except Exception as err:
        return f"failed to write audio to file: {err}"

    with open(audio_tf_path, "rb") as f:
        data = f.read()
    
    audio_id = fs_audio.put(data)
    os.remove(audio_tf_path)

    message["audio_id"] = str(audio_id)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=AUDIO_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        print(f"error publishing to audio queue: {err}")
        # entry point to initiate exponential backoff retry
        # and maybe log message in DLX
        # so that it is not forgotten.
        return f"failed to publish to audio queue: {err}"


