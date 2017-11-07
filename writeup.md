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
[image5]: ./output_images/test6_poly_fit.png "Fit Visual"
[image6]: ./output_images/test6_final.png "Output"
[video1]: ./output_images/project_video.gif "Video"
[ch0]: ./output_images/channel0.gif "channel 0"
[filter1]: ./output_images/channel1.gif "channel 1"
[filter2]: ./output_images/challenge_video_hsv_saturation_1_2.gif "saturation_1_2"
[filter3]: ./output_images/challenge_video_saturation_100_180.gif "100_180"

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

There are two classes I created to handle the pipeline.

Class `Lane` can be found in `Lane.py`. This class store the detected lane pixels, fit polynomials, and analyzes curvature and center offset.

Class `LaneFinder` can be found in `LaneFinder.py`. This class has a method called `pipeline`. This method takes into the original image and run the following steps:

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
| (970, 630)    | (520, 30)     |
| (348, 630)    | (200, 30 )    |


Apply the transformation to an image I got:

![birdview][image2]

#### 3. Filtering.

Codes in `pipeline`:
```
L = self.prepare_channels(warped_img)
```

`prepare_channels` is a method of `LaneFinder`. It does two things:

1. Call `LaneFinder.channel_decompose`, which applies different filters to the bird-eye-view image. The result of each filter is a grayscale (value range 0.0~1.0) or binary image. There can be multiple filters and thus multiple resulting images. We call them different channels and return them as `[channel0, channel1, ...]`. This function can be override in the future for more complicated task.

2. Multiply each channel by a mask. The mask is generated and visualized in "Define Mask" section in `./pipeline.ipynb`. This helps reducing some pixels that we know irrelevant for sure.

![mask][mask]

Here are some examples of my filters:
* Filter0: Take the Value component in the HSV space, and threshold pixels with values > 200. (This filter gives the main channel to process the project video)

![value > 200][ch0]
* Filter1: `topo_parabolic_bump_filter` in `Filters.py`. it first applies a high-pass Laplacian-like filter
```
[[-1, ...,-1, -1, 2,..., 2, 2, -1,,,,, -1, -1]]
```
to capture objects with width = number of repetition of 2,
 and then applies a low pass filter with kernel:
```
[[-1],
  ...
 [-1],
 [2],
  ...
 [2],
 [1],
  ...
 [1]]
```
to remove flat blobs. Then morphological transformations were used to remove noises. This filter is relatively stable when applied to red channel even if there are shadows. It picks more white lane points on the project video than Filter0.

![filter][filter1]
* Filter2: Saturation component in the HSV representation is between 1 and 2. Good for white lanes in different lighting condition

![saturation_1_2][filter2]

[filter3]: ./output_images/challenge_video_saturation_100_180.gif "100_180"

* Filter2: Saturation component in the HSV representation is between 100 and 180. Good for yellow lanes in different lighting condition

![saturation_100_180][filter3]


#### 4. Identified lane-line pixels and polynomial fitting

I separated the searching for left lane-line and right lane-line. There are several reason to do this. First, in many cases only one of the lane-line is recognizable. In such case, getting one is still better than none. Second, in my pipeline, I decomposed the image into different channels with different filters. Some channels may capture one of the lane really well and lose the other lane completely. So it's better to keep the two lane-line searching process independent to each other.

The codes are in `LaneFinder.init_lane_finder(side)`. It will search for left lane-line if `side=0` and right lane-line if `side=1`. The pseudo code of this step can be summarized below:

1. channel = the first channel
2. In the channel image, in a prescribed region, search for peak to determine the location of the first window (`LaneFinder.initial_window_finder`).
3. Check the peak is valid by compare it to a threshold (might be different for each channels). If check failed, move to the next channel and return to 2. This allow the algo to choose the right channel with enough signals.
4. With the initial window location found, find window for each level (`LaneFinder.find_window_per_level`).
5. Filter out pixels within each window. They are considered candidate lane pixels.
6. Fit a polynomial to the candidate lane pixels. (`Lane.polyfit_left` and `Lane.polyfit_right`)
7. Compare candidate lane pixels to the fitted polynomial. If they are too far away (>median) from the polynomial, they are considered as outliers. Remove outliers, the rest will be considered as lane pixels.
8. Feed the lane pixels into the polynomial and compute the mse, if the error is greater than a threshold, move to the next channel, and go to 2.
9. Once both lane-line are found, check if the two lane intersect in the birdview image. If yes, that's a invalid lane, move to the next channel, and go to 2. (In practice we always search left lane-line first, so channels should be ranked so that best for left lane goes first)
10. After searching all channels, if only one lane was find, parallelly shift the lane in the birdview image to get the other.

More details can be found in the comments in the function.

The result of this step:

![alt text][image5]

#### 5. Curvature and Position

This was done with the method `Lane.analyze` in `Lane.py`. In particular Line146-152 calculate the radius of curvature of the lane, while Line154-156 calculate the position of the vehicle with respect to center. Negative means the vehicle is to the left of the lane center.

#### 6. Plotted back down onto the road.

The detected lane pixels, fitted polynomial curve and lane region are draw onto a birdview canvas by `LaneFinder.draw_lane`. Then the codes below:

```
overlay = cv2.warpPerspective(self.draw_lane(), self.M_inv,
                                  (self.original_image_size[1],self.original_image_size[0]),
                                  flags=cv2.INTER_LINEAR)
cv2.addWeighted(img, 1, overlay, 1, 0.0)
```
apply inverted perspective transformation and overlay it to the original image.

Extra text information is shown on the image with `LaneFinder.draw_result`

Here is an example of my result on a test image:

![alt text][image6]

---

### Pipeline (video)
#### 1. Initialize in video pipeline.

Initialize lowpass filter along time:
```
    self.past_left_fitx = np.array([[np.nan]*smooth_window]*img_size[0])
    self.past_right_fitx = np.array([[np.nan]*smooth_window]*img_size[0])
```
`past_left_fitx` and `past_right_fitx` will store the x coordinates on the polynomial curve in the past `smooth_window` frames, where `smooth_window` can be set when initializing `LaneFinder`. By default I set it to be 5.

#### 2. Apply image pipeline.

Apply image pipeline with the following change: If the lane-line has been found in the previous frame, then search lane pixels in a tubular neighborhood of the previous lane-line (See `LaneFinder.tube_lane_finder`). The width of this tubular neighborhood is an adaptive parameter. It starts with a small value 10, if the pixels detected this way failed any of the threshold test, polynomial fitting test, or lane width/interection test, increase the neighborhood width and redo the search. Finally, if the search failed with a neighborhood width 100, it will give up and do a fresh searching as in the image pipeline. If all effort failed, use the lane info from the previous frame.

#### 3. My final video output.

Here's a [link to my video result](https://youtu.be/IbYR-s7BySw). Or it can be found in `output_videos/project_video_output.mp4`

---

### Discussion

#### 1. Problems / issues and future improvement

The main problem of the pipeline is lack of adaptiveness. Allowing multiple channels helps this issue but it's far from satisfactory. In reality we cannot manually select parameters in the filters to address different situation. This is where CNN should help a lot. By training with videos + left/right steering, we should be able to create a CNN whose first few layers can capture the lanes nicely. The output of these layers then can be used to override the method `LaneFinder.channel_decompose`.

Another issue is that we are assuming perspective transformation to be constant along time. On a bumpy road, the camera will tilde up and down. If we apply the same perspective transformation, the road won't look parallel in the birds-eye view image. This will also affect computation of curvature. Since this happens to both lane-line in a symmetric fashion, it is less likely to influence the computation of center offset.
