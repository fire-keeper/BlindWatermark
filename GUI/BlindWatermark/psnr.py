import cv2
import numpy as np


def PSNR(img1, img2):
    mse = np.mean( (img1/255. - img2/255.) ** 2 )
    if mse < 1.0e-10:
        return 100
    PIXEL_MAX = 1
    return 20 * np.log10(PIXEL_MAX / np.sqrt(mse))

def average_psnr(filename1,filename2):
    a = cv2.imread(filename1)
    b = cv2.imread(filename2)
    out=0
    for i in range(3):
        out+=PSNR(a[:,:,i],b[:,:,i])
    return out/3

def test_psnr(filename1,filename2):
    a = cv2.imread(filename1)
    b = cv2.imread(filename2)
    for i in range(3):
        print(PSNR(a[:,:,i],b[:,:,i]))