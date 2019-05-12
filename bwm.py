import argparse
from BlindWatermark import watermark
from BlindWatermark import test_ncc

if __name__=='__main__':
    parser = argparse.ArgumentParser(usage="嵌入或者解出盲水印.", description="help info.")
    parser.add_argument("--key",'-k', default=(4399,2333,32),type=float, help="依次输入2个随机种子和除数(正数),除数可以是一个或者两个,之间用空格隔开.", dest="key",nargs='*')
    parser.add_argument('-d','--dwt_deep',default=1,type=int,help="设定小波变换的次数,次数增加会提高鲁棒性,但会减少图片承载水印的能力,通常取1,2,3",dest="dwt_deep")
    parser.add_argument('-bs','--block_shape',default=4,type=int,help='设定分块大小,因为限定长宽相同,所以只需要传一个整数就行了,对于大图可以使用更大的数,如8,更大的形状使得对原图影响更小,而且运算时间减少,但对鲁棒性没有提高,注意太大会使得水印信息超过图片的承载能力', dest="block_shape")
    parser.add_argument('-em','--embed',default=False, action="store_true", dest="embed")
    parser.add_argument('-ex','--extract',default=False, action="store_true", dest="extract")
    parser.add_argument("--read",'-r', help="要嵌入或提取水印的图片的路径", dest="ori_img")
    parser.add_argument("--read_wm",'-wm', help="要嵌入的水印的路径", dest="wm")
    parser.add_argument("--wm_shape",'-ws', help="要解出水印的形状", dest="wm_shape",nargs=2)
    parser.add_argument("--out_put",'-o', help="图片的输出路径", dest="output")
    parser.add_argument("--show_ncc",'-s', help="展示输出图片和原图的NC值(相似度)", default=False, action="store_true", dest="show_ncc") 
    args = parser.parse_args()
    print(args)
    

    if (args.embed and args.extract) or ((not args.embed) and (not args.extract)):
        #args.embed 和 args.extract 有且只有一个为True
        print("('-em','--embed')和('-ex','--extract') 必须有且只有一个")
        exit()
    elif args.embed:
        #嵌入水印
        if len(args.key)==3:
            random_seed1,random_seed2,mod1 = args.key
            bwm = watermark(int(random_seed1),int(random_seed2),mod1,block_shape = (args.block_shape,args.block_shape),dwt_deep=args.dwt_deep)
        elif len(args.key)==4:  
            random_seed1,random_seed2,mod1,mod2 = args.key
            bwm = watermark(int(random_seed1),int(random_seed2),mod1,mod2,block_shape = (args.block_shape,args.block_shape),dwt_deep=args.dwt_deep)
        else:
            print("您输入了{}个key,但是本程序现在只支持3个或者4个key".format(len(args.key)))
            exit()
        
        bwm.read_ori_img(args.ori_img)
        bwm.read_wm(args.wm)
        bwm.embed(args.output)
        if args.show_ncc:
            test_ncc(args.ori_img,args.output)

    elif args.extract:
        try:
            wm_shape0,wm_shape1 = args.wm_shape
            wm_shape0,wm_shape1 = int(wm_shape0),int(wm_shape1)
        except Exception as e:
            print("输入的水印形状",args.wm_shape,"不符合规定")
            print(e)
            exit()
        if len(args.key)==3:
            random_seed1,random_seed2,mod1 = args.key
            bwm = watermark(int(random_seed1),int(random_seed2),mod1,wm_shape=(wm_shape0,wm_shape1),block_shape = (args.block_shape,args.block_shape),dwt_deep=args.dwt_deep)
        elif len(args.key)==4:  
            random_seed1,random_seed2,mod1,mod2 = args.key
            bwm = watermark(int(random_seed1),int(random_seed2),mod1,mod2,wm_shape=(wm_shape0,wm_shape1),block_shape = (args.block_shape,args.block_shape),dwt_deep=args.dwt_deep)
        bwm.extract(args.ori_img,args.output)
        if args.show_ncc:
            if args.wm:
                test_ncc(args.wm,args.output)
            else:
                print("当要展示输出水印和原水印的相似度时需要给出原水印的路径")

