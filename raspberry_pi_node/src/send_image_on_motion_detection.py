import cv2
import time
import pika
# to run tests outside the RPI environment set Picamera2 and Preview None
try:
    from picamera2 import Picamera2, Preview
except ImportError:
    Picamera2 = Preview = None


# replace with own rabbitmq parameters
RMQ_USER = 'user'
RMQ_PASSWORD = 'password'
RMQ_HOST = 'host'
RMQ_PORT = 5672
RMQ_QUEUE = 'queue'

# parameters for the motion detection algorithm
DELTA_THRESH = 25
MIN_AREA = 1500
DILATE_ITERATIONS = 3

FRAME_RATE_IN_SEC = 1


def prepare_image(img):
    image_prep = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_prep = cv2.GaussianBlur(image_prep, (21, 21), 0)
    return image_prep

def detect_motion(last_img, current_img):
    # prepare images with gray scale and blur
    last_img_prepared = prepare_image(last_img)
    current_img_prepared = prepare_image(current_img)

    # find difference by subtraction
    avg = current_img_prepared.astype(float)
    cv2.accumulateWeighted(last_img_prepared, avg, 0.5)  # blend last into current image
    img_delta = cv2.absdiff(last_img_prepared, cv2.convertScaleAbs(avg))  # calculate the absolute value of the difference

    # highlight significant differences
    img_delta_binary = cv2.threshold(img_delta, DELTA_THRESH, 255, cv2.THRESH_BINARY)[1]
    img_delta_binary = cv2.dilate(img_delta_binary, None, iterations=DILATE_ITERATIONS)

    # find outlines of differing areas
    contours = cv2.findContours(img_delta_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    # detect a motion if at least one area exceeds the threshold
    motion = False
    for contour in contours:
        if cv2.contourArea(contour) > MIN_AREA:
            motion = True
    return motion

def connect_to_message_broker():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD)
    connection_params = pika.ConnectionParameters(
        host=RMQ_HOST,
        port=RMQ_PORT,
        credentials=credentials
    )
    rmq_connection = pika.BlockingConnection(connection_params)
    amqp_channel = rmq_connection.channel()
    amqp_channel.queue_declare(queue=RMQ_QUEUE)
    return rmq_connection, amqp_channel


def watch():
    current_img = None
    last_img = None

    while True:
        current_img = picam2.capture_array()

        if last_img is not None:  # skip motion detection in the first iteration
            motion_detected = detect_motion(last_img, current_img)
            if motion_detected:
                # convert image to bytes
                _, buffer = cv2.imencode('.jpg', current_img)
                img_bytes = buffer.tobytes()
                # send image to the queue
                channel.basic_publish(exchange='', routing_key=RMQ_QUEUE, body=img_bytes)
                print(" [x] Image sent to amqp queue")

        last_img = current_img
        time.sleep(FRAME_RATE_IN_SEC)


if __name__ == "__main__":

    try:
        connection, channel = connect_to_message_broker()
    except Exception as e:
        print(f"Error while connecting to broker: {e}")
        exit(0)

    # initialize the camera
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()

    try:
        watch()

    except KeyboardInterrupt:
        print("Shutting down gracefully...")

    finally:
        picam2.stop()
        connection.close()