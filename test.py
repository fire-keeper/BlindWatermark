import cv2
import numpy as np
from BlindWatermark import watermark

def attack(fname,type):
    img = cv2.imread(fname)    
        
    if type == "ori":  
        return img 

    if type == "blur":  
        kernel = np.ones((3,3),np.float32)/9
        return cv2.filter2D(img,-1,kernel)

    if type=="rotate180":
        return rotate_about_center(img,180)
        
    if type=="rotate90":
        return rotate_about_center(img,90)
                
    if type=="chop10":
        w,h = img.shape[:2]
        img[w-int(w*0.1):,:]=img[:int(w*0.1),:]
        return img
    
    if type=="chop5":
        w,h = img.shape[:2]
        img[w-int(w*0.05):,:]=img[:int(w*0.05),:]
        return img

    if type=="chop30":
        w,h = img.shape[:2]
        img[w-int(w*0.3):,:]=img[:int(w*0.3),:]
        return img
        
    if type == "gray":
        return  cv2.imread(fname,cv2.IMREAD_GRAYSCALE)    

    if type == "redgray":
        return  img[:,:,0]

    if type == "saltnoise":  
        for k in range(1000):
            i = int(np.random.random() * img.shape[1])
            j = int(np.random.random() * img.shape[0])
            if img.ndim == 2:
                img[j, i] = 255
            elif img.ndim == 3:
                img[j, i, 0] = 255
                img[j, i, 1] = 255
                img[j, i, 2] = 255
        return img


    # if type == "vwm":
    #     # vwm = script.VisWatermark 
    #     mark =  cv2.imread('./data/wm.png')  
    #     params = {}
    #     params['position']      = (30,30)
    #     img =vwm.watermark_image(img, mark, params)
    #     return img

    
    if type == "randline":  
        cv2.rectangle(img,(384,0),(510,128),(0,255,0),3)
        cv2.rectangle(img,(0,0),(300,128),(255,0,0),3)
        cv2.line(img,(0,0),(511,511),(255,0,0),5)
        cv2.line(img,(0,511),(511,0),(255,0,255),5)
        
        return img

    if type == "cover":  
        cv2.circle(img,(256,256), 63, (0,0,255), -1)
        font=cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img,'Just DO it ',(10,500), font, 4,(255,255,0),2)
        return img


    if type == "brighter10":  
        w,h = img.shape[:2]
        for xi in range(0,w):
            for xj in range(0,h):
                img[xi,xj,0] = int(img[xi,xj,0]*1.1)
                img[xi,xj,1] = int(img[xi,xj,1]*1.1)
                img[xi,xj,2] = int(img[xi,xj,2]*1.1)
        return img

    if type == "darker10":  
        w,h = img.shape[:2]
        for xi in range(0,w):
            for xj in range(0,h):
                img[xi,xj,0] = int(img[xi,xj,0]*0.9)
                img[xi,xj,1] = int(img[xi,xj,1]*0.9)
                img[xi,xj,2] = int(img[xi,xj,2]*0.9)
        return img


    if type == "largersize":  
        w,h=img.shape[:2]
        return cv2.resize(img,(int(h*1.5),w))

    if type == "smallersize":  
        w,h=img.shape[:2]
        return cv2.resize(img,(int(h*0.5),w))
    if type == "jpeg_90":
        return (90,img)

    if type == "jpeg_85":
        return (85,img)

    if type == "jpeg_80":
        return (80,img)

    if type == "jpeg_70":
        return (70,img)
    if type == "jpeg_60":
        return (60,img)
    if type == "jpeg_50":
        return (50,img)
    if type == "jpeg_40":
        return (40,img)
    if type == "jpeg_30":
        return (30,img)
    return img
    
    


attack_dic ={}
# attack_dic['ori']          = '原图'
attack_dic['blur']         = '模糊'
# #attack_dic['rotate180']    ='旋转180度'
# #attack_dic['rotate90']     = '旋转90度'
# attack_dic['chop5']        = '剪切掉5%'
# attack_dic['chop10']       = '剪切掉10%'
attack_dic['chop30']       = '剪切掉30%'
attack_dic['saltnoise']    ='椒盐噪声'
# # attack_dic['vwm']          = '增加明水印'
attack_dic['randline']     = '随机画线'
attack_dic['cover']        = '随机遮挡'
# attack_dic['brighter10']   = '亮度提高10%'
# attack_dic['darker10']     = '亮度降低10%'
# #attack_dic['largersize']   = '图像拉伸'
# #attack_dic['smallersize']  = '图像缩小'
# #attack_dic['gray']         ='自然灰度处理'
# #attack_dic['redgray']      ='红色灰度处理'
#attack_dic['jpeg_90']     = 'jepg压缩,压缩率90'
#attack_dic['jpeg_85']     = 'jepg压缩,压缩率85'
#attack_dic['jpeg_80']     = 'jepg压缩,压缩率80'
#attack_dic['jpeg_70']     = 'jepg压缩,压缩率70'
#attack_dic['jpeg_60']     = 'jepg压缩,压缩率60'
#attack_dic['jpeg_50']     = 'jepg压缩,压缩率50'
#attack_dic['jpeg_40']     = 'jepg压缩,压缩率40'
#attack_dic['jpeg_30']     = 'jepg压缩,压缩率30'


if __name__ == "__main__":
    bwm = watermark(4399,2333,32,20)
    bwm.read_ori_img("pic/lena_grey.png")
    bwm.read_wm("pic/wm.png")
    bwm.embed('out.png')
    imgname = 'lena.png'
    imgname_JPG = 'lena.jpg'
    for k,v in attack_dic.items():
        if k in ['jpeg_90','jpeg_85','jpeg_80','jpeg_70','jpeg_60','jpeg_50','jpeg_40','jpeg_30']:
            QUALITY,wmd = attack('out.png',k)
            cv2.imwrite('./output/attack/'+k+'_'+imgname_JPG,wmd,[int(cv2.IMWRITE_JPEG_QUALITY),QUALITY])
        else:
            wmd = attack('out.png',k)
            cv2.imwrite('./output/attack/'+k+'_'+imgname,wmd)
    for k,v in attack_dic.items():
        if k in ['jpeg_90','jpeg_85','jpeg_80','jpeg_70','jpeg_60','jpeg_50','jpeg_40','jpeg_30']:
            bwm.extract('./output/attack/'+k+'_'+imgname_JPG,'extract/'+k+"_wm.png")
        else:
            bwm.extract('./output/attack/'+k+'_'+imgname,'extract/'+k+"_wm.png")