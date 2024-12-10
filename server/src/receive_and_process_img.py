import cv2
import numpy as np
import requests
from requests import RequestException
import os
import pika
import sys
from datetime import datetime


RMQ_USER = 'pi'
RMQ_PASSWORD = 'pw'
RMQ_HOST = 'rabbitmq'
RMQ_QUEUE = 'images'
RMQ_PORT = 5672

# parameters for storing uploaded files in two categories
BASE_STORAGE_PATH = '/app/storage'
HUMAN = 'human'
NON_HUMAN = 'non_human'

# replace with your char id and bot
CHAT_ID = 'your_chat_id'
BOT = 'your_bot'
UPLOAD_URL = f'https://api.telegram.org/{BOT}/sendPhoto'


def notify_bot(body):
    files = {'photo': body}
    data = {'chat_id': CHAT_ID}
    try:
        response = requests.post(UPLOAD_URL, files=files, data=data)
        print('Response status code:', response.status_code)
    except RequestException as e:
        print(f'Failed to send photo : {e}')

def define_callback():
    def callback(ch, method, properties, body):
        # decode binary image data
        np_array = np.frombuffer(body, dtype=np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            print('Image could not be decoded')
            return

        time_stamp = datetime.now().strftime('%H:%M:%S')
        humans, _ = hog.detectMultiScale(image, winStride=(10, 10), padding=(32, 32), scale=1.05)
        if len(humans) > 0:
            print("Human detected notify bot and save image")
            notify_bot(body)
            filename = BASE_STORAGE_PATH + '/' + HUMAN + '/' + time_stamp + '.jpg'
            cv2.imwrite(filename, image)
        else:
            print("No human detected save image")
            filename = BASE_STORAGE_PATH + '/' + NON_HUMAN + '/' + time_stamp + '.jpg'
            cv2.imwrite(filename, image)

    return callback

def connect_to_broker():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD)
    connection_params = pika.ConnectionParameters(
        host=RMQ_HOST,
        port=RMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    return connection, channel

def create_directories():
    os.makedirs(os.path.join(BASE_STORAGE_PATH, HUMAN), exist_ok=True)
    os.makedirs(os.path.join(BASE_STORAGE_PATH, NON_HUMAN), exist_ok=True)
    print("Directories created successfully!")


if __name__ == '__main__':
    create_directories()

    # initialize people detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # connect to broker and set up message queue
    connection, channel = connect_to_broker()
    callback = define_callback()
    channel.queue_declare(queue=RMQ_QUEUE)
    channel.basic_consume(
        queue=RMQ_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )

    try:
        print(' [x] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

    finally:
        connection.close()
