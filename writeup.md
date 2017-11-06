## Advanced Lane Finding

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

## Result
![GIF of processed project video][video1]
---

[//]: # (Image References)
[mask]: ./output_images/mask.png "mask"

[image0]: ./output_images/calibrated_chessboard/calibration1_compare.jpg "Undistorted_Chess"
[image1]: ./output_images/undistorted_test_images/test4_compare.jpg "Undistorted"
[image2]: ./test_images/straight_lines1_compare.jpg "Road Transformed"
[image3]: ./examples/binary_combo_example.jpg "Binary Example"
[image4]: ./output_images/birds-eye/straight_lines2_compare.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./output_images/project_video.gif "Video"
[ch0]: ./output_images/channel0.gif "channel 0"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README

You're reading it!

### Camera Calibration

#### 1. How I computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in the second code cell of the IPython notebook located in "./pipeline.ipynb", with function named `calibration_matrix`.

I first experimented with the function `cv2.findChessboardCorners` to find what is the right grid size for each calibration image. I found the folloing table:

|  image file name |  grid size |
|---|---|
|  `calibration1.jpg` |  (9,5) |
|  `calibration4.jpg` |  (6,5) |
|  `calibration5.jpg` |  (7,6) |
|  others |  (9,6) |

Then for each chessboard image, I computed that coordinates of corners with `cv2.findChessboardCorners`. These corner coordinates were stored in the list `imgpoints`. Correspondingly the list `objpoints` stores the indices of the corners (which looks like (i,j), and determines the location of the Corresponding corner in that image).

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to one of the chessboard image using the `cv2.undistort()` function. The figure below shows a comparison between before and after the undistortion:

![original vs undistorted chessboard][image0]

### Pipeline (single images)

I defined a class called `LaneFinder` which can be found in `LaneFinder.py` or `pipeline.ipynb`. This class has a method called `pipeline`. This method takes into the original image and run the following steps:

#### 1. Distortion correction.

Achieved by the following codes:

```
warped_img = cv2.undistort(img, self.calibration_matrix, self.calibration_dist,
                           None, self.calibration_matrix)
```

Here `self.calibration_matrix`, `self.calibration_dist` are initiated using the method described in the camera calibration section above. I apply the distortion correction to one of the test images like this one:
![original vs undistorted trip image][image1]

#### 2. Perspective Transformation.

In the 3rd code cell in `./pipeline.ipynb`, there is a function
`perspective_transformation` which computes the transformation matrix.

In the function, I used an image with straight line to find the following 4 points:
```
(592, 453), (695,453), (970, 630), (348, 630)
```

These 4 points should be mapped to the vertices of a rectangle in the birdview image. I set the birdview to be 720x720. The map is as shown below:

| Source        | Destination   |
|:-------------:|:-------------:|
| (592, 453)     | (200, 200)    |
| (695,453)   | (520, 200)      |
| (970, 630)    | (520, 50)     |
| (348, 630)    | (200, 50 )    |


Apply the transformation to an image I got:

![birdview][image2]

#### 3. Filtering.

Codes in `pipeline`:
```
L = self.prepare_channels(warped_img)
```

`prepare_channels` is a method of `LaneFinder`. It does two things:

1. Call `LaneFinder.channel_decompose`, which applies different filters to the bird-eye-view image. The result of each filter is a grayscale (value range 0.0~1.0) or binary image. There can be multiple filters and thus multiple resulting images. We call them different channels and return them as `[channel0, channel1, ...]`. This function can be override in the future for more complicated task. Here are some examples of my filters:

Filter0: Take the Value component in the HSV space, and threshold pixels with values > 200. (Turns out this single filter is enough for the project video)

![value > 200][ch0]

Filter1:

2. Multiply each channel by a mask. The mask is generated and visualized in "Define Mask" section in `./pipeline.ipynb`. This helps reducing some pixels that we know irrelevant for sure.

![mask][mask]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

Then I did some other stuff and fit my lane lines with a 2nd order polynomial kinda like this:

![alt text][image5]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in lines # through # in my code in `my_other_file.py`

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines # through # in my code in `yet_another_file.py` in the function `map_lane()`.  Here is an example of my result on a test image:

![alt text][image6]

---

### Pipeline (video)
#### 1. Extra steps in video pipeline.
* Lowpass filter along time: The smoothing window size can be set when initializing `LaneFinder`. By default I set it to be 5.

* Apply a distortion correction to raw images.

#### 2. My final video output.

Here's a [link to my video result](https://youtu.be/IbYR-s7BySw)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  
