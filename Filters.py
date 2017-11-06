import numpy as np
import cv2
import heapq


def topo_parabolic_bump_filter(img, x_thresh=(0.5,1),
                               y_thresh=(0,0.0001),
                               min_area=400, ksize=3):
    kernel = np.array([[-1]*ksize+[2]*ksize+[-1]*ksize])
    res = np.abs(cv2.filter2D(img, -1, kernel))
    res = res/np.max(res)
    y_kernel = np.array([[-1],[-1],[0],[1],[1]])
    mask = np.abs(cv2.filter2D(img, -1, y_kernel))
    binary = np.zeros_like(res)
    binary[(res>=x_thresh[0])&(res<=x_thresh[1])&(mask<y_thresh[1])] = 1
    d_kernel = np.ones((3,3),np.uint8)
    binary = cv2.dilate(binary,d_kernel,iterations = 1)
    binary = cv2.erode(binary,d_kernel,iterations = 1)

    n,n_blobs,stats,cent = cv2.connectedComponentsWithStats(binary.astype(np.uint8),
                                                            connectivity=8,ltype=cv2.CV_32S)
    tot = img.shape[0]*img.shape[1]
    areas = stats[:,-1]
    big_segs = heapq.nlargest(6, range(len(areas)), areas.take)
    binary = np.zeros_like(res)
    for i in big_segs[1:]:
        if areas[i]>min_area: binary[n_blobs==i]=1
    return binary

def abs_sobel_thresh(img, orient='x', thresh_min=0, thresh_max=255):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if orient == 'x':
        sb = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    if orient == 'y':
        sb = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    abs_sb = np.absolute(sb)
    sc_sb = np.uint8(abs_sb*255/np.max(abs_sb))
    binary_output = np.zeros_like(sc_sb)
    binary_output[(sc_sb>thresh_min)&(sc_sb<thresh_max)]=1
    return binary_output

def sob_filter(channel, x_thresh=(0.8,1), y_thresh=(0,1),
               a_thresh=(0.01,1.56), grad_thresh=(0,1), ksize=9):
    sobelx = cv2.Sobel(channel, cv2.CV_64F, 1, 0, ksize=ksize) # Take the derivative in x
    sobely = cv2.Sobel(channel, cv2.CV_64F, 0, 1, ksize=ksize) # Take the derivative in y
    abs_sobelx = np.absolute(sobelx) # Absolute x derivative to accentuate lines away from horizontal
    scaled_sobelx = abs_sobelx/np.max(abs_sobelx)
    abs_sobely = np.absolute(sobely) # Absolute y derivative to accentuate lines away from horizontal
    scaled_sobely = abs_sobely/np.max(abs_sobely)

    mg = np.sqrt(np.square(abs_sobelx)+np.square(abs_sobely))
    mg = mg/np.max(mg)

    angle = np.arctan2(abs_sobely, abs_sobelx)

    h_binary = np.zeros_like(h_channel)
    h_binary[(scaled_sobelx>=x_thresh[0]) &
             (scaled_sobelx<=x_thresh[1]) &
             (scaled_sobely>=y_thresh[0]) &
             (scaled_sobely<=y_thresh[1]) &
             (mg>=grad_thresh[0]) &
             (mg<=grad_thresh[1]) &
             (angle>=a_thresh[0]) &
             (angle<=a_thresh[1])] = 1
    return np.dstack((h_binary,h_binary,h_binary))*255.0

def bump_filter(img, thresh=(0.5,1), ksize=3):
    kernel = np.array([[-1]*ksize+[2]*ksize+[-1]*ksize for i in range(1)])
    res = np.abs(cv2.filter2D(img, -1, kernel))
    res = res/np.max(res)
    binary = np.zeros_like(res)
    binary[(res>=thresh[0])&(res<=thresh[1])] = 1
    return binary*255.0 if len(binary.shape)==3 else np.dstack((binary,binary,binary))*255.0
