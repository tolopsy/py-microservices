import pika, sys, os
from pika.adapters.blocking_connection import BlockingChannel
from comms.email import notify

AUDIO_QUEUE = os.environ["AUDIO_QUEUE"]

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", heartbeat=0))
    channel = connection.channel()

    def callback(ch: BlockingChannel, method, properties, body):
        err = notify(body)
        if err:
            print(f"There has been an error: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=AUDIO_QUEUE, on_message_callback=callback)

    print("Waiting for messages. To exit, press CTRL+C")

    channel.start_consuming()


"""TODO: 
1. Printed errors to be properly logged
2. Handle exceptions around channel.start_consuming
"""

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            # cleanup, if any
            pass
