## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

This is the writeup itself :)

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

First I carried out the image processing on the following image:

![camera view][writeup1]: ./writeup_content/writeup1.png

By applying the grind onto the image I could obtain reference points to carry out the perspective transform using the cv2 library, modifying the previous image from:

![camera view grid][writeup2]: ./writeup_content/writeup2.png

to 

![transformed][writeup3]: ./writeup_content/writeup3.png

Afterwards I applied color thresholding to the image, obtaining the result in the following binary image:

![transformed][writeup4]: ./writeup_content/writeup4.png

Afterwards I modified the order of the previous steps, overall regarding the obstacles image in order to avoid including the inferior black cone formed when transforming the perspective. Meaning I first applied the color thresholding and then carried out the perspective transform of the image.

Once I tested this, I coded the color thresholding for the obstacles and the rocks. In the case of the obstacles I filtered all pixels opposite to the ground, meaning RGB < (160,160,160). In the case of the rock I filtered for RG > (160,160) and Blue < (110)

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

In the same way I populated the previous point, I informed the code in process_image() function, generating the following video:

![video result][writeup-video1]: ./output/test_mapping.mp4

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

Regarding the perception.py file:

+++I modified the color thresh function in orde to include a new function (color_thresh2) to provide color thresholding for the 3 cases (ground, obstacles, rock).
+++After modifying this function, I informed the perception_step() function. Here I included the variables for image (Rover.img) obtained from the Rover telemetry data, other variables regarding the definition of the images transformation (dst_size, bottom_offset, source, destination) and data required for the coordinates conversion (yaw, xpos, ypos, world_size, scale).
+++After defining these variables, I informed the image processing as in the previous steps.

+++ 1: Image color threshold into 3 images (1 for ground, 1 for obstacles & 1 for rock). I applied this color threshold first in order to avoid including afterwards the bottom corners in black after the perspective transform.

+++ 2: Apply perspective transform.

+++ 3: Update Rover.vision_image with the images with the perspective transform to be shown on the screen.

+++ 4: Convert the image pixel values to rover centric coordinates.

+++ 5: Convert these coordinates to world coordinates in order to update the map.

+++ 6: Update the map view with the previous coordinates and make sure the pixels don't overlap giving priority to the ground pixels, meaning that, if there is a pixel informed as ground, delete the obstacle colour in that pixel.

+++ 7: Obtain polar coordinates for the rover movement, defining the variables Rover.nav_dists and Rover.nav_angles in order for the rover to proceed moving in the file decision.py.

Regarding decision.py file:

First the rover processes if there is a navigation angle defined (obtained from the previous file). In case there is an angle defined, it processes the telemetry information in order to move according to such angle (defined as the average trajectory of the processed ground image)

If the rover can't keep moving forward, it executes the mode "stop" where it analyses telemetry data and steers until it obtains an acceptable trajectory.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

The rover covered mostly all of the ground with a fidelity of more than 60 %, identifying all of the rocks seen in its path.

The results could be improved by increasing the rover speed in order to reduce the timing to cover all of the ground. Include an additional logic to avoid revisiting same sites by checking position on map and increase fidelity by modifying the colouring for overlapping areas (ground vs obstacle).

Also, as pointed out in the project page, I could include an additional logic for measuring position regarding rocks and redirecting the rover towards them until it detects to be near objective and pick them up.  