<div align="center" id="top"> 
  <img src=images/platform_front.jpg width="300" />
  <img src=images/platform_back.jpg width="370" />
  &#xa0;
</div>

<h1 align="center"> Jetson Linefollower </h1>
<h2 align="center"> Linefollower with image processing based on Jetson Nano  </h2>


<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/Status-done-green?style=for-the-badge&logo=appveyor">
    <img alt="Repository size" src="https://img.shields.io/github/languages/code-size/KamilGos/OptiBot?style=for-the-badge">
</p>


<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0;
  <a href="#package-content">Content</a> &#xa0; | &#xa0;
  <a href="#eyes-implementation">Implementation</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="#technologist-author">Author</a> &#xa0; | &#xa0;
</p>

<br>

## :dart: About ##

The project involved developing a line tracking algorithm based on image processing algorithms.It was aimed to replace the commonly used reflection sensors in favour of a camera. In order totest the algorithms, the project also assumed the creation of a mobile platform. Project assumedto create the final system using Python language and Robot Operating System (ROS).

The project was a success. Image processing algorithms, regulator algorithms, as well as atest platform, were prepared and robot successfully followed the line. The whole system wasimplemented independently using both raw Python language and ROS. The system has beensuccessfully tested. There was also no discrepancy between the two implementations (Pythonand ROS).

[![Result](https://www.youtube.com/watch?v=YFPQv9tbDRQ
/0.jpg)](https://www.youtube.com/watch?v=YFPQv9tbDRQ)


## :eyes: Implementation ##

The following sections describe the most important components of the system. The software part of system was implemented using the following tools:
* Python (version: 3.9.1)
* ROS (version: melodic with Python3)
* OpenCV (version: 4.5.1)

<h2 align="left">1. Mobile Platform </h2>
The platform consist of the following elements:

* four-wheel chassis with rear wheels driven by two independent 5V DC motors and front axle controlled by one servo,
* motors controller,
* 2 PWM signal generators,
* Li-Po battery for powering both DC motors,
* DC-DC converter,
* Jetson Nano Developer Kit,
* Uninterruptible Power Supply UPS T-208 for powering Jetson Nano,
* Wi-Fi card with antennas,
* RGB camera.

<div align="center" id="electronics"> 
  <img src=images/linefollower_flow.png width="700" />
  &#xa0;
</div>

The main processing unit is Jetson Nano Developer Kit. It is powering by an independent uninterruptible power supply that delivers enough power to run Jetson in high power mode. It is connected with Jetson using a delivered coupler. Directly to Jetson the WiFi network card is connected so it is passable to establish wireless connection between Jetson and any other computer. To increase the signal strength, two additional antennas were attached to the network card. Next element is the camera. It is connected with Jetson nano through MIPI CSI-2 interface. This type of connection gives very fast data transmission which is extremely useful for image processing applications. To control engines the Pulse Width Modulation signal generator and motors controller (h-bridge) were used. Jetson Nano is connected with PWM generator (adjusted to 1kHz) using the I2C interface. The PWM signal then goes to the H-bridge, is processed (amplified) and goes to the motors' clamps, so they rotate in the expected direction and at the expected speed. To control servo motor another PWM signal generator is used. This one is adjusted to work wich 50Hz frequency which is needed to control servo. It is also connected to Jetson Nano using the I2C interface. The generated PWM signal goes directly to the servo, so one can control its rotation. The whole system (excluding Jetson Nano) is powering by Li-Po battery through DC/DC converter.


<h2 align="left">2. Algorithm structure </h1>
<div align="center" id="ros"> 
  <img src=images/system_flow.png width="500" />
  &#xa0;
</div>

The whole system consist of several dependent parts that communicate together. It was divided into 5 modules. First one is the image processing module, whose job is to extract the line from picture and calculate the error. Next module is the regulator. It transform error signal to control signal. Two modules supporting PWM generators were also created. One is designed to control DC motors and the other to control the servo deflection. The final executor of all modules function is main loop, which performs the superior function in the system. It continuously executes the algorithm thanks to which the robot is able to follow the line.


<h2 align="left">3. Image processing </h1>
<div align="center" id="ros"> 
  <img src=images/im_pr.png width="500" />
  &#xa0;
</div>
 
The image processing module is responsible for extracting line form pictures. First of all, it reads the new frame from the camera. As the frames are quite large and no full area processing is required, each image is cropped. Figure 1 shows the original size frame. The red lines visible in the picture are related to a cropped area. In the next step, the colour space transformation from RGB to grayscale is performed. It reduces the image from 3 dimensions to only one, where all pixels are in grayscale. The next four steps are Gaussian blur, thresholding, erosion and dilation. The output of those algorithms is presented in figure 2. At that moment, the frame consists of a filtered white line and black background. The next phase is to extract the position of the line. For this purpose, the contours finding algorithm is used. Found contours are visible in the figure 3. Then, the idea is to find the centroid of the area defined by the contours. This goal can be achieved by using the method of moments. Figure 4 shows found centroid marked as a green dot. Also, it presents the methodology of error calculation. The error is calculated as the difference between the centre of contours area and the middle point of a considered frame. In this case, the error is $+156$. In the next phase, this value is sent to the controller module.


## :memo: License ##

This project is under license from MIT.

## :technologist: Author ##

Made with :heart: by <a href="https://github.com/KamilGos" target="_blank">Kamil Goś</a>

&#xa0;

<a href="#top">Back to top</a>






