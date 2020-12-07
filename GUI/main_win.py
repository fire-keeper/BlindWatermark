# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QSize
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QListView,QDialog
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon

from BlindWatermark import watermark , average_ncc, average_psnr, recovery
from Ui_main_win import Ui_MainWindow
from Ui_about import Ui_Dialog
from os import popen
import os
import json
import shutil


class bwm_embed_thread(watermark):
    finish_out = pyqtSignal(str,str,dict)
    assert_ERROR = pyqtSignal(int)
    def __init__(self,parameter,my_file_path):

        watermark.__init__(self, random_seed_wm = parameter['random_seed_wm'],
                                        random_seed_dct = parameter['random_seed_dct'],
                                        mod = parameter['mod'],
                                        mod2 = parameter.get('mod2') if parameter.get('mod2')>0.1 else None,
                                        wm_shape = parameter.get('wm_shape',None),
                                        block_shape = parameter['block_shape'],
                                        dwt_deep = parameter['dwt_deep']
                                        )
        self.ori_img_path = parameter['ori_img']
        self.wm_path = parameter['wm']
        self.out_file_path = my_file_path

    def run(self):
        if os.path.isdir(self.out_file_path):
            if len(self.ori_img_path)>1 and len(self.wm_path)==1:
                #多对一模式
                for ori_img in self.ori_img_path:
                    self.read_ori_img(ori_img)
                    self.read_wm(self.wm_path[0])
                    if self.ori_img_shape[0]*self.ori_img_shape[1]/(4**(self.dwt_deep))>=self.wm_shape[0]*self.wm_shape[1]*self.block_shape[0]*self.block_shape[1]:
                        # return self.bwm.embed2array()
                        out_file_name = os.path.join(self.out_file_path,os.path.split(ori_img)[-1])
                        self.embed(out_file_name)
                    else:
                        self.assert_ERROR.emit(0)
                key_dic = {
                            'random_seed_wm' : self.random_seed_wm,
                            'random_seed_dct' : self.random_seed_dct,
                            'mod' : self.mod,
                            'mod2' : self.mod2,
                            'wm_shape' : self.wm_shape,
                            'block_shape' : self.block_shape,
                            'dwt_deep' : self.dwt_deep
                        }
                self.finish_out.emit(self.out_file_path,'嵌入完成,非一对一',key_dic)
            elif len(self.ori_img_path)==1 and len(self.wm_path)>1:
                for wm_path in self.wm_path:
                    self.read_ori_img(self.ori_img_path[0])
                    self.read_wm(wm_path)
                    if self.ori_img_shape[0]*self.ori_img_shape[1]/(4**(self.dwt_deep))>=self.wm_shape[0]*self.wm_shape[1]*self.block_shape[0]*self.block_shape[1]:
                        # return self.bwm.embed2array()
                        img_name_prefix,img_name_postfix = os.path.splitext(os.path.split(self.ori_img_path[0])[-1])
                        wm_prefix,_ = os.path.splitext(os.path.split(wm_path)[-1])
                        out_file_name = os.path.join(self.out_file_path,"{}_{}{}".format(img_name_prefix,wm_prefix,img_name_postfix))
                        self.embed(out_file_name)
                    else:
                        self.assert_ERROR.emit(0)
                key_dic = {
                            'random_seed_wm' : self.random_seed_wm,
                            'random_seed_dct' : self.random_seed_dct,
                            'mod' : self.mod,
                            'mod2' : self.mod2,
                            'wm_shape' : self.wm_shape,
                            'block_shape' : self.block_shape,
                            'dwt_deep' : self.dwt_deep
                        }
                self.finish_out.emit(self.out_file_path,'嵌入完成,非一对一',key_dic)
            else:
                self.assert_ERROR.emit(1)
        else:
            #一对一模式
            assert len(self.ori_img_path) == len(self.wm_path)==1
            self.read_ori_img(self.ori_img_path[0])
            self.read_wm(self.wm_path[0])

            if self.ori_img_shape[0]*self.ori_img_shape[1]/(4**(self.dwt_deep))>=self.wm_shape[0]*self.wm_shape[1]*self.block_shape[0]*self.block_shape[1]:
                # return self.bwm.embed2array()
                self.embed(self.out_file_path)

                key_dic = {
                    'random_seed_wm' : self.random_seed_wm,
                    'random_seed_dct' : self.random_seed_dct,
                    'mod' : self.mod,
                    'mod2' : self.mod2,
                    'wm_shape' : self.wm_shape,
                    'block_shape' : self.block_shape,
                    'dwt_deep' : self.dwt_deep
                }
                self.finish_out.emit(self.out_file_path,'嵌入完成,保存于',key_dic)
            else:
                self.assert_ERROR.emit(0)

class bwm_extract_thread(watermark):
    finish_out = pyqtSignal(str,str)
    def __init__(self,parameter,my_file_path):

        watermark.__init__(self, random_seed_wm = parameter['random_seed_wm'],
                                        random_seed_dct = parameter['random_seed_dct'],
                                        mod = parameter['mod'],
                                        mod2 = parameter.get('mod2') if parameter.get('mod2')>0.1 else None,
                                        wm_shape = parameter.get('wm_shape',None),
                                        block_shape = parameter['block_shape'],
                                        dwt_deep = parameter['dwt_deep']
                                        )
        self.ori_img_path = parameter['ori_img']
        self.out_file_path = my_file_path

    def run(self):
        # return self.bwm.embed2array()
        if os.path.isdir(self.out_file_path):
            for ori_img in self.ori_img_path:
                file_name = os.path.split(ori_img)[-1]
                self.extract(ori_img,os.path.join(self.out_file_path,"wm_"+file_name))
            self.finish_out.emit(self.out_file_path,'提取完成,非一对一')
        else:
            #单一提取模式
            assert len(self.ori_img_path)==1
            self.extract(self.ori_img_path[0],self.out_file_path)
            self.finish_out.emit(self.out_file_path,'提取完成,保存于')

class open_pic_thread(QThread):
    def __init__(self,file_path):
        QThread.__init__(self)
        self.file_path = file_path
    def run(self):
        popen('start '+self.file_path)

class explorer_thread(QThread):
    def __init__(self, dir_path):
        QThread.__init__(self)
        self.dir_path = dir_path
    def run(self):
        self.dir_path = self.dir_path.replace('/','\\')
        popen('explorer {}'.format(self.dir_path))



class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.my_bwm_parameter = {}
        self.my_recovery_parameter = {}
        self.init_listVIew()
    
    def my_setup(self):
        pass

    def init_listVIew(self):
        self.listView.setViewMode(QListView.ListMode)#或者使用QListView.IconMode  QListView.ListMode
        #self.listView.setMovement(QListView.Static)
        self.listView.setIconSize(QSize(20,20))#图标的大小（原始图标大小如果100,100，此时设置草果原始大小则失效）
        self.listView.setGridSize(QSize(60,40))#每个选项所在网格大小（每个选项外层grid宽高）
        #self.listView.setMaximumHeight(200)#listView整体最大高度
        #self.listView.setMinimumSize(QSize(200,200))#listView最小面积（一般如果设置最大高和宽属性后就不设置这个属性了）
        #self.listView.setMaximumSize(QSize(500,500))#listVIew最大面积（一般如果设置最大高和宽属性后就不设置这个属性了）
        self.listView.setMinimumHeight(80)#listView最小高度

        self.listView.setResizeMode(QListView.Adjust)
        #self.listView.setMovement(QListView.Static)#设置图标可不可以移动，默认是可移动的，但可以改成静态的：


        self.listView_model=QStandardItemModel()
        self.listView.setModel(self.listView_model)

        self.listView.clicked.connect(self.checkItem)

    def checkItem(self,index):

        file_path = (index.data().split('→'))[-1]
        if index.data()[:4]=='使用密钥':
            clipboard = QApplication.clipboard()
            clipboard.setText(file_path) #此处为密钥
        elif index.data()[:5]=='批处理模式':
            pass
        else:
            self.open_pic = open_pic_thread(file_path)
            self.open_pic.finished.connect(self.open_pic.deleteLater)
            self.open_pic.start()
        # QMessageBox.information(self,"ListView",'row:%s, text:%s' % (index.row(), index.data()))

    def assert_error(self,Etype):
        if Etype==0:
            QMessageBox.warning(self,'警告','参数错误,请参考关于中的公式修改参数,使其满足公式',QMessageBox.Ok)
        else:
            QMessageBox.warning(self,'警告','出现多对多的情况，请向开发者汇报(不会真的出现吧)',QMessageBox.Ok)

    def bwm_add_item(self,file_path,action_type=None,key=None):
        #路径中不允许出现\ / : * ? " < > →
        
        if action_type == '嵌入完成,保存于':
            self.listView_model.appendRow(QStandardItem(QIcon(':/icon/key.png'),'使用密钥→'+json.dumps(key)))
            similarity_value = ''
            work_path = self.my_bwm_parameter.get('work_path',None)
            with open('{}key.json'.format(work_path),'w') as f:
                json.dump(key,f)
            if self.checkBox_2.isChecked() and self.my_bwm_parameter.get('ori_img',False):
                psnr_v = average_psnr(self.my_bwm_parameter.get('ori_img',False),file_path)
                ncc_v  = average_ncc(self.my_bwm_parameter.get('ori_img',False),file_path)
                similarity_value = ',psnr:{:.2f},ncc:{:.4f}'.format(psnr_v,ncc_v)
            action_type  = '嵌入完成{},保存于'.format(similarity_value)
            self.listView_model.appendRow(QStandardItem(QIcon(':/icon/image.png'),action_type+'→'+file_path))
        elif action_type == '提取完成,保存于':
            self.listView_model.appendRow(QStandardItem(QIcon(':/icon/image.png'),action_type+'→'+file_path))
        elif action_type == '嵌入完成,非一对一':
            self.listView_model.appendRow(QStandardItem(QIcon(':/icon/image.png'),"批处理模式,嵌入完成!"+'→'+file_path))
        elif action_type == '提取完成,非一对一':
            self.listView_model.appendRow(QStandardItem(QIcon(':/icon/image.png'),"批处理模式,提取完成!"+'→'+file_path))

    def refresh_parameter(self):
        self.my_bwm_parameter['random_seed_wm'] = self.spinBox_3.value()
        self.my_bwm_parameter['random_seed_dct'] = self.spinBox_2.value()
        self.my_bwm_parameter['mod'] = self.doubleSpinBox.value()
        self.my_bwm_parameter['mod2'] = self.doubleSpinBox_2.value()
        self.my_bwm_parameter['wm_shape'] = (self.spinBox_6.value(),self.spinBox_7.value())
        self.my_bwm_parameter['block_shape'] = (self.spinBox_4.value(),self.spinBox_5.value())
        self.my_bwm_parameter['dwt_deep'] = self.spinBox.value()

    def refresh_UI(self,bwm_parameter):
        self.spinBox_3.setValue(bwm_parameter['random_seed_wm'])
        self.spinBox_2.setValue(bwm_parameter['random_seed_dct'])
        self.doubleSpinBox.setValue(bwm_parameter['mod'])
        self.doubleSpinBox_2.setValue( bwm_parameter.get('mod2') if bwm_parameter.get('mod2') else 0)
        self.spinBox_6.setValue(bwm_parameter['wm_shape'][0])
        self.spinBox_7.setValue(bwm_parameter['wm_shape'][1])
        self.spinBox_4.setValue(bwm_parameter['block_shape'][0])
        self.spinBox_5.setValue(bwm_parameter['block_shape'][1])
        self.spinBox.setValue(bwm_parameter['dwt_deep'])
        self.refresh_parameter()

    def show_recovery(self,num,file_path):
        if num == 0:
            QMessageBox.warning(self,"警告",'检测到的特征点过少,请适当调低阈值',QMessageBox.Ok)
        else:
            self.open_pic = open_pic_thread(file_path)
            self.open_pic.finished.connect(self.open_pic.deleteLater)
            self.open_pic.start()
            QMessageBox.information(self,"提示",'检测到{}个特征点,恢复图片已写入'.format(num),QMessageBox.Ok)


    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        my_file_paths,_ = QFileDialog.getOpenFileNames(self, '导入图片', self.my_bwm_parameter.get('work_path','./'))
        if my_file_paths:
            if len(my_file_paths)==1:
                self.my_bwm_parameter['ori_img'] = my_file_paths
                self.label_4.setText(my_file_paths[0].split('/')[-1])
            else:
                if len(self.my_bwm_parameter.get('wm',tuple()))<=1:
                    self.my_bwm_parameter['ori_img'] = my_file_paths
                    self.label_4.setText("多个文件")
                else:
                    QMessageBox.warning(self,"警告",'原图和水印最多只能有一个是多个文件',QMessageBox.Ok)
        
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        my_file_paths,_ = QFileDialog.getOpenFileNames(self, '导入水印', self.my_bwm_parameter.get('work_path','./'))
        if my_file_paths:
            if len(my_file_paths)==1:
                self.my_bwm_parameter['wm'] = my_file_paths
                self.label_5.setText(my_file_paths[0].split('/')[-1])
            else:
                if len(self.my_bwm_parameter.get('ori_img',tuple()))<=1:
                    self.my_bwm_parameter['wm'] = my_file_paths
                    self.label_5.setText("多个文件")
                else:
                    QMessageBox.warning(self,"警告",'原图和水印最多只能有一个是多个文件',QMessageBox.Ok)

    
    @pyqtSlot()
    def on_radioButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        self.pushButton_3.setText('嵌入')

    
    @pyqtSlot()
    def on_radioButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.pushButton_3.setText('提取')
    

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        if self.pushButton_3.text()=='嵌入':
            if bool(self.my_bwm_parameter.get('ori_img',False)) and bool(self.my_bwm_parameter.get('wm',False)):
                self.refresh_parameter()
                if self.my_bwm_parameter['mod'] <0.01:
                    QMessageBox.warning(self,"警告",'第一个量化因子:{}不符合要求'.format(self.my_bwm_parameter['mod']),QMessageBox.Ok)
                else:
                    N_ori_img = len(self.my_bwm_parameter.get('ori_img'))
                    N_wm      = len(self.my_bwm_parameter.get('wm'))
                    if N_ori_img == 1 and N_wm == 1:
                        my_file_path,_ = QFileDialog.getSaveFileName(self, '保存图片', self.my_bwm_parameter.get('work_path','./'),"PNG (*.png);;JPG (*.jpg);;All Files (*)")
                        if my_file_path:
                            self._thread = bwm_embed_thread(self.my_bwm_parameter,my_file_path)
                            self._thread.finished.connect(self._thread.deleteLater)
                            self._thread.finish_out.connect(self.bwm_add_item)
                            self._thread.assert_ERROR.connect(self.assert_error)
                            self._thread.valueChanged.connect(self.BlueProgressBar.setValue)
                            self._thread.start()
                    else:
                        output_path = QFileDialog.getExistingDirectory(self,'设置输出目录',self.my_bwm_parameter.get('work_path','./'))
                        if output_path:
                            self._thread = bwm_embed_thread(self.my_bwm_parameter,output_path)
                            self._thread.finished.connect(self._thread.deleteLater)
                            self._thread.finish_out.connect(self.bwm_add_item)
                            self._thread.assert_ERROR.connect(self.assert_error)
                            self._thread.valueChanged.connect(self.BlueProgressBar.setValue)
                            self._thread.start()
            else:
                QMessageBox.warning(self,"警告",'你需要打开原始图片和水印图片,才能进行嵌入',QMessageBox.Ok)
        elif self.pushButton_3.text()=='提取':
            if bool(self.my_bwm_parameter.get('ori_img',False)):
                self.refresh_parameter()
                if self.my_bwm_parameter['mod'] <0.01:
                    QMessageBox.warning(self,"警告",'第一个量化因子:{}不符合要求'.format(self.my_bwm_parameter['mod']),QMessageBox.Ok)
                elif self.my_bwm_parameter['wm_shape'][0] == 0 or self.my_bwm_parameter['wm_shape'][1] == 0:
                    QMessageBox.warning(self,"警告",'提取时需要设定水印形状',QMessageBox.Ok)
                else:
                    N_ori_img = len(self.my_bwm_parameter.get('ori_img'))
                    if N_ori_img==1:
                        my_file_path,_ = QFileDialog.getSaveFileName(self, '保存图片', self.my_bwm_parameter.get('work_path','./'),"PNG (*.png);;JPG (*.jpg);;All Files (*)")
                        if my_file_path:
                            self._thread = bwm_extract_thread(self.my_bwm_parameter,my_file_path)
                            self._thread.finished.connect(self._thread.deleteLater)
                            self._thread.finish_out.connect(self.bwm_add_item)
                            self._thread.valueChanged.connect(self.BlueProgressBar.setValue)
                            self._thread.start()
                    else:
                        output_path = QFileDialog.getExistingDirectory(self,'设置输出目录',self.my_bwm_parameter.get('work_path','./'))
                        if output_path:
                            self._thread = bwm_extract_thread(self.my_bwm_parameter,output_path)
                            self._thread.finished.connect(self._thread.deleteLater)
                            self._thread.finish_out.connect(self.bwm_add_item)
                            self._thread.valueChanged.connect(self.BlueProgressBar.setValue)
                            self._thread.start()
            else:
                QMessageBox.warning(self,"警告",'你需要打开要提取水印的图片,才能进行提取',QMessageBox.Ok)


    
    @pyqtSlot()
    def on_spinBox_4_editingFinished(self):
        """
        Slot documentation goes here.
        """
        if self.checkBox.isChecked():
            value = self.spinBox_4.value()
            self.spinBox_5.setValue(value)
    
    @pyqtSlot()
    def on_spinBox_5_editingFinished(self):
        """
        Slot documentation goes here.
        """
        if self.checkBox.isChecked():
            value = self.spinBox_5.value()
            self.spinBox_4.setValue(value)

    
    @pyqtSlot()
    def on_pushButton_5_clicked(self):
        """
        设置工作目录
        """
        work_path = QFileDialog.getExistingDirectory(self,'设置工作目录','./')
        if work_path:
            self.my_bwm_parameter['work_path']=work_path+'/'
            if len(work_path)>20:
                smaller_work_path = work_path[:10]+work_path[-10:]
            else:
                smaller_work_path = work_path
            self.label_10.setText(smaller_work_path)
    
    @pyqtSlot()
    def on_pushButton_6_clicked(self):
        """
        从剪切板导入密钥
        """
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        try:
            key = json.loads(text)
            self.refresh_UI(key)
        except json.decoder.JSONDecodeError:
            QMessageBox.warning(self,"警告",'剪切板中的文本不符合key的格式(即json格式)',QMessageBox.Ok)
    
    @pyqtSlot()
    def on_pushButton_7_clicked(self):
        """
        从文件导入密钥
        """
        work_path = self.my_bwm_parameter.get('work_path','.')
        key_path,_ = QFileDialog.getOpenFileName(self, '选择key文件', work_path,"json File (*.json);;All Files (*)")
        if key_path:
            try:
                with open(key_path,'r') as f:
                    key = json.load(f)
                    self.refresh_UI(key)
            except json.decoder.JSONDecodeError:
                QMessageBox.warning(self,"警告",'key文件的文本不符合key的格式(即json格式)',QMessageBox.Ok)

    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        """
        将图片复制到工作目录
        """
        work_path = self.my_bwm_parameter.get('work_path',None)
        ori_img_path = self.my_bwm_parameter.get('ori_img',False)
        wm_path = self.my_bwm_parameter.get('wm',False)
        if bool(ori_img_path):
            if isinstance(ori_img_path,list) and len(ori_img_path)>1:
                QMessageBox.information(self,'信息',"在多个文件的情况下该功能已被禁用",QMessageBox.Ok)
                return
        if bool(wm_path):
            if isinstance(wm_path,list) and len(wm_path)>1:
                QMessageBox.information(self,'信息',"在多个文件的情况下该功能已被禁用",QMessageBox.Ok)
                return
        if not work_path:
            QMessageBox.warning(self,"警告",'未设定工作目录',QMessageBox.Ok)
        else:
            string = 'Done!\n'
            if isinstance(ori_img_path,list):
                ori_img_path = ori_img_path[0]
            if bool(ori_img_path) and os.path.isfile(ori_img_path):
                img_type = os.path.splitext(ori_img_path)[-1]
                try:
                    shutil.copyfile(ori_img_path,work_path+'ori'+img_type)
                    string+=(ori_img_path+' → '+work_path+'ori'+img_type+'\n')
                except shutil.SameFileError:
                    string+='原图片已存在于工作目录\n'
            
            if bool(wm_path) and os.path.isfile(wm_path):
                img_type = os.path.splitext(wm_path)[-1]
                try:
                    shutil.copyfile(wm_path,work_path+'wm'+img_type)
                    string+=(wm_path+' → '+work_path+'wm'+img_type+'\n')
                except shutil.SameFileError:
                    string+='水印图片已存在于工作目录\n'
            QMessageBox.information(self,'信息',string,QMessageBox.Ok)

    @pyqtSlot()
    def on_pushButton_8_clicked(self):
        """
        读取原图
        """
        file_path,_ = QFileDialog.getOpenFileName(self, '读取原图', self.my_bwm_parameter.get('work_path','./'))
        if file_path:
            self.my_recovery_parameter['ori_img'] = file_path
    
    @pyqtSlot()
    def on_pushButton_9_clicked(self):
        """
        读取受到攻击的图片
        """
        file_path,_ = QFileDialog.getOpenFileName(self, '读取受到攻击的图片', self.my_bwm_parameter.get('work_path','./'))
        if file_path:
            self.my_recovery_parameter['attacked_img'] = file_path
    
    @pyqtSlot()
    def on_pushButton_10_clicked(self):
        """
        恢复
        """
        ori_img = self.my_recovery_parameter.get('ori_img',None)
        attacked_img = self.my_recovery_parameter.get('attacked_img',None)
        if not ori_img:
            QMessageBox.warning(self,"警告",'未读取原图',QMessageBox.Ok)
        elif not attacked_img:
            QMessageBox.warning(self,"警告",'未读取受到攻击的图片',QMessageBox.Ok)
        else:
            outfile_path,_ = QFileDialog.getSaveFileName(self, '恢复图片', self.my_bwm_parameter.get('work_path','./'),"PNG (*.png);;All Files (*)")
            if outfile_path:
                rate = self.doubleSpinBox_3.value()
                self.recovery_thread = recovery(ori_img,attacked_img,outfile_path,rate)
                self.recovery_thread.finished.connect(self.recovery_thread.deleteLater)
                self.recovery_thread.num_of_good.connect(self.show_recovery)
                self.recovery_thread.start()

    @pyqtSlot()
    def on_pushButton_11_clicked(self):
        """
        打开工作目录
        """
        work_path = self.my_bwm_parameter.get('work_path',None)
        if work_path:
            self.explorer_thread = explorer_thread(work_path)
            self.explorer_thread.finished.connect(self.explorer_thread.deleteLater)
            self.explorer_thread.start()
        else:
            QMessageBox.warning(self,"警告",'未设定工作目录',QMessageBox.Ok)


    @pyqtSlot()
    def on_help_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
    
    @pyqtSlot()
    def on_support_triggered(self):
        """
        Slot documentation goes here.
        """
        pass
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
    
    
