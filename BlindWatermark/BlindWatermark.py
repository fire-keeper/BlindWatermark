import numpy as np 
import cv2
from scipy.fftpack import dctn,idctn
from pywt import dwt2,idwt2
import os


class watermark():
    def __init__(self,random_seed_wm,random_seed_dct,mod,mod2=None,wm_shape=None):
        # self.wm_per_block = 1
        self.block_shape = (4,4)  #2^n
        self.random_seed_wm = random_seed_wm
        self.random_seed_dct = random_seed_dct
        self.mod = mod
        self.mod2 = mod2
        self.wm_shape = wm_shape


    def init_block_add_index(self,img_shape):
        #假设原图长宽均为2的整数倍,同时假设水印为64*64,则32*32*4
        #分块并DCT
        shape0_int,shape1_int = int(img_shape[0]/self.block_shape[0]),int(img_shape[1]/self.block_shape[1])
        if not shape0_int*shape1_int>=self.wm_shape[0]*self.wm_shape[1]:
            print("水印的大小超过图片的容量")
        self.part_shape = (shape0_int*self.block_shape[0],shape1_int*(self.block_shape[1]))
        self.block_add_index0,self.block_add_index1 = np.meshgrid(np.arange(shape0_int),np.arange(shape1_int))
        self.block_add_index0,self.block_add_index1 = self.block_add_index0.flatten(),self.block_add_index1.flatten()
        self.length = self.block_add_index0.size
        #验证没有意义,但是我不验证不舒服斯基
        assert self.block_add_index0.size==self.block_add_index1.size
        

    def read_ori_img(self,filename):
        ori_img = cv2.imread(filename)
        # self.ori_img_YUV = ori_img
        self.ori_img_YUV = cv2.cvtColor(ori_img, cv2.COLOR_BGR2YUV)
        assert self.ori_img_YUV.shape[0]%2==0
        assert self.ori_img_YUV.shape[1]%2==0

        self.coeffs_Y = dwt2(self.ori_img_YUV[:,:,0],'haar')
        self.ha_Y = self.coeffs_Y[0]
        self.coeffs_U = dwt2(self.ori_img_YUV[:,:,1],'haar')
        self.ha_U = self.coeffs_U[0]
        self.coeffs_V = dwt2(self.ori_img_YUV[:,:,2],'haar')
        self.ha_V = self.coeffs_V[0]


        self.ha_block_shape = (int(self.ha_Y.shape[0]/self.block_shape[0]),int(self.ha_Y.shape[1]/self.block_shape[1]),self.block_shape[0],self.block_shape[1])
        strides = self.ha_Y.itemsize*(np.array([self.ha_Y.shape[1]*self.block_shape[0],self.block_shape[1],self.ha_Y.shape[1],1]))
        
        self.ha_Y_block = np.lib.stride_tricks.as_strided(self.ha_Y.copy(),self.ha_block_shape,strides)
        self.ha_U_block = np.lib.stride_tricks.as_strided(self.ha_U.copy(),self.ha_block_shape,strides)
        self.ha_V_block = np.lib.stride_tricks.as_strided(self.ha_V.copy(),self.ha_block_shape,strides)

        

    def read_wm(self,filename):
        self.wm = cv2.imread(filename)[:,:,0]
        self.wm_shape = self.wm.shape[:2]

        #初始化块索引数组,因为需要验证块是否足够存储水印信息,所以才放在这儿
        self.init_block_add_index(self.ha_Y.shape)

        self.wm_flatten = self.wm.flatten()
        if self.random_seed_wm:
            self.random_wm = np.random.RandomState(self.random_seed_wm)
            self.random_wm.shuffle(self.wm_flatten)

    def block_add_wm(self,block,index,i):
        
        i = i%(self.wm_shape[0]*self.wm_shape[1])

        wm_1 = self.wm_flatten[i]
        block_dct = dctn(block,norm='ortho')
        block_dct_flatten = block_dct.flatten().copy()
        
        block_dct_flatten = block_dct_flatten[index]
        block_dct_shuffled = block_dct_flatten.reshape(self.block_shape)
        U,s,V = np.linalg.svd(block_dct_shuffled)
        max_s = s[0]
        s[0] = (max_s-max_s%self.mod+3/4*self.mod) if wm_1>=128 else (max_s-max_s%self.mod+1/4*self.mod)
        if self.mod2:
            max_s = s[1]
            # s[1] = (max_s-max_s%self.mod2+3/4*self.mod2) if wm_1>=128 else (max_s-max_s%self.mod2+1/4*self.mod2)
            s[1] = (max_s-max_s%self.mod2+3/4*self.mod2) if wm_1<128 else (max_s-max_s%self.mod2+1/4*self.mod2)

        ###np.dot(U[:, :k], np.dot(np.diag(sigma[:k]),v[:k, :]))
        block_dct_shuffled = np.dot(U,np.dot(np.diag(s),V))

        block_dct_flatten = block_dct_shuffled.flatten()
   
        block_dct_flatten[index] = block_dct_flatten.copy()
        block_dct  = block_dct_flatten.reshape(self.block_shape)

        return idctn(block_dct,norm='ortho')



    def embed(self,filename):

        self.embed_ha_Y_block=self.ha_Y_block.copy()
        self.embed_ha_U_block=self.ha_U_block.copy()
        self.embed_ha_V_block=self.ha_V_block.copy()

        self.random_dct = np.random.RandomState(self.random_seed_dct)
        index = np.arange(self.block_shape[0]*self.block_shape[1])

        for i in range(self.length):

            self.random_dct.shuffle(index)
            self.embed_ha_Y_block[self.block_add_index0[i],self.block_add_index1[i]] = self.block_add_wm(self.embed_ha_Y_block[self.block_add_index0[i],self.block_add_index1[i]],index,i)
            self.embed_ha_U_block[self.block_add_index0[i],self.block_add_index1[i]] = self.block_add_wm(self.embed_ha_U_block[self.block_add_index0[i],self.block_add_index1[i]],index,i)
            self.embed_ha_V_block[self.block_add_index0[i],self.block_add_index1[i]] = self.block_add_wm(self.embed_ha_V_block[self.block_add_index0[i],self.block_add_index1[i]],index,i)

        
        
        self.embed_ha_Y_part = np.concatenate(self.embed_ha_Y_block,1)
        self.embed_ha_Y_part = np.concatenate(self.embed_ha_Y_part,1)
        self.embed_ha_U_part = np.concatenate(self.embed_ha_U_block,1)
        self.embed_ha_U_part = np.concatenate(self.embed_ha_U_part,1)
        self.embed_ha_V_part = np.concatenate(self.embed_ha_V_block,1)
        self.embed_ha_V_part = np.concatenate(self.embed_ha_V_part,1)

        self.embed_ha_Y = self.ha_Y.copy()
        self.embed_ha_Y[:self.part_shape[0],:self.part_shape[1]] = self.embed_ha_Y_part
        self.embed_ha_U = self.ha_U.copy()
        self.embed_ha_U[:self.part_shape[0],:self.part_shape[1]] = self.embed_ha_U_part
        self.embed_ha_V = self.ha_V.copy()
        self.embed_ha_V[:self.part_shape[0],:self.part_shape[1]] = self.embed_ha_V_part


        _, (cH, cV, cD) = self.coeffs_Y
        self.embed_coeffs_Y = (self.embed_ha_Y, (cH, cV, cD))
        _, (cH, cV, cD) = self.coeffs_U
        self.embed_coeffs_U = (self.embed_ha_U, (cH, cV, cD))
        _, (cH, cV, cD) = self.coeffs_V
        self.embed_coeffs_V = (self.embed_ha_V, (cH, cV, cD))


        self.embed_img_Y = idwt2(self.embed_coeffs_Y,"haar")
        self.embed_img_U = idwt2(self.embed_coeffs_U,"haar")
        self.embed_img_V = idwt2(self.embed_coeffs_V,"haar")
        self.embed_img_YUV = self.ori_img_YUV.copy()
        self.embed_img_YUV[:,:,0] = self.embed_img_Y
        self.embed_img_YUV[:,:,1] = self.embed_img_U
        self.embed_img_YUV[:,:,2] = self.embed_img_V
        # self.embed_img_YUV = np.concatenate((self.embed_img_Y[:,:,np.newaxis],self.embed_img_U[:,:,np.newaxis],self.embed_img_V[:,:,np.newaxis]),-1)   #-1或者2

        self.embed_img = cv2.cvtColor(self.embed_img_YUV,cv2.COLOR_YUV2BGR)
        # self.embed_img = self.embed_img_YUV
        cv2.imwrite(filename,self.embed_img)

    def block_get_wm(self,block,index):
        block_dct = dctn(block,norm='ortho')
        block_dct_flatten = block_dct.flatten().copy()
        block_dct_flatten = block_dct_flatten[index]
        block_dct_shuffled = block_dct_flatten.reshape(self.block_shape)

        U,s,V = np.linalg.svd(block_dct_shuffled)
        max_s = s[0]
        wm_1 = 255 if max_s%self.mod >self.mod/2 else 0
        if self.mod2:
            max_s = s[1]
            wm_2 = 255 if max_s%self.mod2 >self.mod2/2 else 0
            wm = (wm_1*3+wm_2*1)/4
        else:
            wm = wm_1
        return wm

    def extract(self,filename,out_wm_name):
        if not self.wm_shape:
            print("水印的形状未设定")
            return 0
        
        #读取图片
        embed_img = cv2.imread(filename)



        # embed_img_YUV = embed_img
        embed_img_YUV = cv2.cvtColor(embed_img, cv2.COLOR_BGR2YUV)
        assert embed_img_YUV.shape[0]%2==0
        assert embed_img_YUV.shape[1]%2==0

        embed_img_Y = embed_img_YUV[:,:,0]
        embed_img_U = embed_img_YUV[:,:,1]
        embed_img_V = embed_img_YUV[:,:,2]
        coeffs_Y = dwt2(embed_img_Y,'haar')
        coeffs_U = dwt2(embed_img_U,'haar')
        coeffs_V = dwt2(embed_img_V,'haar')
        ha_Y = coeffs_Y[0]
        ha_U = coeffs_U[0]
        ha_V = coeffs_V[0]
        
        #初始化块索引数组
        try :
            if self.ha_Y.shape == ha_Y.shape :
                self.init_block_add_index(ha_Y.shape)
            else:
                print('你现在要解水印的图片与之前读取的原图的形状不同,这是不被允许的')
        except:
            self.init_block_add_index(ha_Y.shape)


        ha_block_shape = (int(ha_Y.shape[0]/self.block_shape[0]),int(ha_Y.shape[1]/self.block_shape[1]),self.block_shape[0],self.block_shape[1])
        strides = ha_Y.itemsize*(np.array([ha_Y.shape[1]*self.block_shape[0],self.block_shape[1],ha_Y.shape[1],1]))
        
        ha_Y_block = np.lib.stride_tricks.as_strided(ha_Y.copy(),ha_block_shape,strides)
        ha_U_block = np.lib.stride_tricks.as_strided(ha_U.copy(),ha_block_shape,strides)
        ha_V_block = np.lib.stride_tricks.as_strided(ha_V.copy(),ha_block_shape,strides)


        extract_wm   = np.array([])
        extract_wm_Y = np.array([])
        extract_wm_U = np.array([])
        extract_wm_V = np.array([])
        self.random_dct = np.random.RandomState(self.random_seed_dct)

        index = np.arange(self.block_shape[0]*self.block_shape[1])
        for i in range(self.length):
            self.random_dct.shuffle(index)
            wm_Y = self.block_get_wm(ha_Y_block[self.block_add_index0[i],self.block_add_index1[i]],index)
            wm_U = self.block_get_wm(ha_U_block[self.block_add_index0[i],self.block_add_index1[i]],index)
            wm_V = self.block_get_wm(ha_V_block[self.block_add_index0[i],self.block_add_index1[i]],index)
            wm = round((wm_Y+wm_U+wm_V)/3)

            #else情况是对循环嵌入的水印的提取
            if i<self.wm_shape[0]*self.wm_shape[1]:
                extract_wm   = np.append(extract_wm,wm)
                extract_wm_Y = np.append(extract_wm_Y,wm_Y)
                extract_wm_U = np.append(extract_wm_U,wm_U)
                extract_wm_V = np.append(extract_wm_V,wm_V)
            else:
                times = int(i/(self.wm_shape[0]*self.wm_shape[1]))
                ii = i%(self.wm_shape[0]*self.wm_shape[1])
                extract_wm[ii]   = (extract_wm[ii]*times +   wm  )/(times+1)
                extract_wm_Y[ii] = (extract_wm_Y[ii]*times + wm_Y)/(times+1)
                extract_wm_U[ii] = (extract_wm_U[ii]*times + wm_U)/(times+1)
                extract_wm_V[ii] = (extract_wm_V[ii]*times + wm_V)/(times+1)



        wm_index = np.arange(extract_wm.size)
        self.random_wm = np.random.RandomState(self.random_seed_wm)
        self.random_wm.shuffle(wm_index)
        extract_wm[wm_index]   = extract_wm.copy()
        extract_wm_Y[wm_index] = extract_wm_Y.copy()
        extract_wm_U[wm_index] = extract_wm_U.copy()
        extract_wm_V[wm_index] = extract_wm_V.copy()
        cv2.imwrite(out_wm_name,extract_wm.reshape(64,64))

        path,file_name = os.path.split(out_wm_name)
        cv2.imwrite(os.path.join(path,'Y_U_V','Y'+file_name),extract_wm_Y.reshape(64,64))
        cv2.imwrite(os.path.join(path,'Y_U_V','U'+file_name),extract_wm_U.reshape(64,64))
        cv2.imwrite(os.path.join(path,'Y_U_V','V'+file_name),extract_wm_V.reshape(64,64))

from NCC import NCC
def test_ncc(filename1,filename2):
    a = cv2.imread(filename1)
    b = cv2.imread(filename2)
    for i in range(3):
        print(NCC(a[:,:,i],b[:,:,i]))   

if __name__=="__main__":
    bwm1 = watermark(4399,2333,36,20)
    bwm1.read_ori_img("pic/lena_grey.png")
    # bwm1.read_ori_img("lena_extended.png")
    bwm1.read_wm("pic/wm.png")
    bwm1.embed('out.png')
    bwm1.extract("out.png","./out_wm.png")

    test_ncc('pic/lena_grey.png','out.png')

    # bwm2 = watermark(7373,1024,22,12)
    # bwm2.read_ori_img('out.png')
    # bwm2.read_wm('pic/wm2.png')
    # bwm2.embed('out2.png')
    # bwm2.extract('out2.png','./out_wm2.png')

    # bwm1.extract('out2.png','./bwm1_out2.png')
    # bwm2.extract('out.png','./bwm2_out.png')

        
