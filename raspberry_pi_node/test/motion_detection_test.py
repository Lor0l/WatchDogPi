import unittest
import cv2

from send_image_on_motion_detection import detect_motion

class ConverterTests(unittest.TestCase):

    def test_given_two_different_images_motion_should_be_detected(self):
        img1 = cv2.imread('test_images/human_back.jpg')
        img2 = cv2.imread('test_images/human_front.jpg')

        motion_detected = detect_motion(img1, img2)

        assert motion_detected == True

    def test_given_the_same_image_no_motion_should_be_detected(self):
        img1 = cv2.imread('test_images/human_back.jpg')
        img2 = cv2.imread('test_images/human_back.jpg')

        motion_detected = detect_motion(img1, img2)

        assert motion_detected == False


    def test_test(self):
        BOT = 'mybot'
        TEST = f'test/{BOT}/.de'
        print(TEST)
