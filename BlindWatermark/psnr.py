import cv2
import numpy as np
from .tools import cv_imread

def PSNR(img1, img2):
   mse = np.mean( (img1/255. - img2/255.) ** 2 )
   if mse < 1.0e-10:
      return 100
   PIXEL_MAX = 1
   return 20 * np.log10(PIXEL_MAX / np.sqrt(mse))

def test_psnr(filename1,filename2):
    a = cv_imread(filename1)
    b = cv_imread(filename2)
    for i in range(3):
        print(PSNR(a[:,:,i],b[:,:,i]))