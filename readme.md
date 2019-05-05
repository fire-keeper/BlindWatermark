# 盲水印

## 如何使用

```
# python代码
bwm1 = watermark(4399,2333,36,20)
#4399和2333是两个随机种子,36和20是用于嵌入算法的除数,理论上第一个除数要大于第二个,除数越大鲁棒性越强,但是除数越大,输出图片的失真越大,需要权衡后决定
bwm1.read_ori_img("pic/lena_grey.png")
bwm1.read_wm("pic/wm.png")
bwm1.embed('out.png')
bwm1.extract("out.png","out_wm.png")
```





## 效果展示

要嵌入水印的原图`lena_grey.png`和水印图片`wm.png`

![lena](./pic/lena_grey.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/200)  ![watermark](./pic/wm.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/100) 

嵌入后的图片

![嵌入水印后的图片](./pics_for_show/grey/output/attack/ori_lena.png)

提取出的图片

![提取出的图片](./pics_for_show/grey/extract/ori_wm.png)

#### 各种攻击以及提取出的水印

| 攻击方式     | 攻击后的图片                                                 | 提取出的水印                                           |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------ |
| 模糊         | ![blur_lena.png](./pics_for_show/grey/output/attack/blur_lena.png) | ![blur_wm.png](./pics_for_show/grey/extract/blur_wm.png) |
| 用图像覆盖   | ![cover_lena.png](./pics_for_show/grey/output/attack/cover_lena.png) | ![](./pics_for_show/grey/extract/cover_wm.png)           |
| 用线条覆盖   | ![randline_lena.png](./pics_for_show/grey/output/attack/randline_lena.png) | ![](./pics_for_show/grey/extract/randline_wm.png)        |
| 亮度调高10%  | ![brighter10_lena.png](./pics_for_show/grey/output/attack/brighter10_lena.png) | ![](./pics_for_show/grey/extract/brighter10_wm.png)      |
| 亮度调低10%  | ![darker10_lena.png](./pics_for_show/grey/output/attack/darker10_lena.png) | ![](./pics_for_show/grey/extract/darker10_wm.png)        |
| 添加椒盐噪声 | ![saltnoise_lena.png](./pics_for_show/grey/output/attack/saltnoise_lena.png) | ![](./pics_for_show/grey/extract/saltnoise_wm.png)       |
| 裁剪5%并填充 | ![](./pics_for_show/grey/output/attack/chop5_lena.png)         | ![](./pics_for_show/grey/extract/chop5_wm.png)           |
| 裁剪10%      | ![](./pics_for_show/grey/output/attack/chop10_lena.png)        | ![](./pics_for_show/grey/extract/chop10_wm.png)          |
| 裁剪30%      | ![](./pics_for_show/grey/output/attack/chop30_lena.png)        | ![](./pics_for_show/grey/extract/chop30_wm.png)          |

#### 针对jpeg压缩, 经检验单独对Y通道解水印效果最好,以下解出的水印均来自Y通道

| 压缩因子 | 压缩后的图片                                           | 提取出的水印                                          |
| -------- | ------------------------------------------------------ | ----------------------------------------------------- |
| 90       | ![](./pics_for_show/grey/output/attack/jpeg_90_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_90_wm.png) |
| 85       | ![](./pics_for_show/grey/output/attack/jpeg_85_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_85_wm.png) |
| 80       | ![](./pics_for_show/grey/output/attack/jpeg_80_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_80_wm.png) |
| 70       | ![](./pics_for_show/grey/output/attack/jpeg_70_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_70_wm.png) |
| 60       | ![](./pics_for_show/grey/output/attack/jpeg_60_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_60_wm.png) |
| 50       | ![](./pics_for_show/grey/output/attack/jpeg_50_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_50_wm.png) |
| 40       | ![](./pics_for_show/grey/output/attack/jpeg_40_lena.jpg) | ![](./pics_for_show/grey/extract/Y_U_V/Yjpeg_40_wm.png) |

#### 水印防破解

如果有不良商家要破坏我们的水印再加上他的水印时, 如果他知道了我们的加密方式(不知道我们的随机种子和除数)时, 破解影响应该是最大的, 针对这种情况作出演示

现在网络上有两种图片A,B. A是我们嵌入水印后发表出去的, B是破解者在A上用相同的添加盲水印方式添加了自己的水印生成的. 然而我们使用我们的参数(随机种子和除数)可以从A,B中提取出我们的水印, 但是用破解者的参数进行提取时,不能从A中提取出破解者的水印,,只能从B中提取出破解者的水印

这便能说明这张图的创作者究竟是谁, 我认为这对保护创作者的权益是至关重要的一步

破解者的水印![](pic/wm2.png)

| 介绍                                                      | 图片                                        | 提取出的水印                                     |
| --------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------ |
| 我们嵌入水印的图片A                                       | ![](./pics_for_show/grey/anti-crack/out.png)  | ![](./pics_for_show/grey/anti-crack/out_wm.png)    |
| 破解者在上面这种我们已经嵌入水印的图中再次嵌入水印的图片B | ![](./pics_for_show/grey/anti-crack/out2.png) | ![](./pics_for_show/grey/anti-crack/out_wm2.png)   |
| 用我们的参数提取破解者的图片B                             |                                             | ![](./pics_for_show/grey/anti-crack/bwm1_out2.png) |
| 用破解者的参数提取我们的图片A                             |                                             | ![](./pics_for_show/grey/anti-crack/bwm2_out.png)  |

