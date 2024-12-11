# WatchDogPi
Course: Applying IoT<br>
Semester: 7


This is the result of the semester project at the Applying IoT course at the XAMK South-Eastern Finland University of 
Applied Sciences during my semester abroad. <br>
<br>
The WatchDogPi system has a Raspberry Pi with a camera as sensor node that observes an area. When a motion is detected,
the Raspberry Pi send the most recent image via a RabbitMQ message queue to a server. The server than uses the openCV 
HOG Descriptor People Detector to search for humans in this image. If a human can be detected, the server uploads 
the image to a Telegram Bot that than notifies the user with posting the image to a chat.

## Used Technologies 
<img src="images/technologies.png" alt="technologies.png" style="width: 100%">

## System Overview 

<img src="images/system_overview.png" alt="sytem_overview.png" style="width: 100%">

## Algorithm Overview
The diagrams model the processing steps done by the python scripts on a high level. This design step helped to 
understand how the system should work and what functionality had to be implemented.

<div align="center">

| **Raspberry Pi**                                                                           | **Server**                                                                                 |
|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| <img src="images/sensor_algorithm_model.png" alt="sensor_algorithm_model.png" width="382"> | <img src="images/server_algorithm_model.png" alt="server_algorithm_model.png" width="382"> |

</div>

## Motion Detection in Pictures
To detect a motion in the observed scene the sensor node continuously takes images and calculates the difference between
the two most recent ones. If the area of the calculated difference is bigger than a threshold a motion is detected. 

<img src="images/subtraction_algorithm_in_pictures.png" alt="system_overview_in_pictures.png" style="width: 100%">

With few adjustments in the code the areas that have changed can be highlighted by drawing the outlines or a frame. It
was a lot of fun playing around with the motion detection and setting the parameters right. For the forest view for 
example it was necessary to find a sweet spot in between the differences created by the leafs in 
wind and actual humans. 

<div align="center">

| <img src="images/marked_motion_night.jpg" alt="marked_motion_night.jpg" width="382"> | <img src="images/marked_motion_woods.png" alt="marked_motion_woods.png" width="382"> |
|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|

</div>
