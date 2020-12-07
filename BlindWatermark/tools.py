import cv2
import numpy as np 
import os

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8),cv2.IMREAD_COLOR)
    return cv_img

def cv_imwrite(path,img):
    suffix = os.path.splitext(path)[-1]
    cv2.imencode(suffix, img)[1].tofile(path)

def recovery(ori_img,attacked_img,outfile_name = './recoveried.png',rate=0.7):
    img = cv2.imread(ori_img)
    img2 = cv2.imread(attacked_img)

    height = img.shape[0]
    width  = img.shape[1]
    # Initiate SIFT detector
    orb = cv2.ORB_create(128)
    MIN_MATCH_COUNT=10
    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img,None)
    kp2, des2 = orb.detectAndCompute(img2,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)



    des1 = np.float32(des1)
    des2 = np.float32(des2)

    matches = flann.knnMatch(des1,des2,k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < rate*n.distance:
            good.append(m)

    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv2.findHomography( dst_pts,src_pts, cv2.RANSAC,5.0)
        out = cv2.warpPerspective(img2, M, (width,height)) #先列后行
        cv2.imwrite(outfile_name,out)
    