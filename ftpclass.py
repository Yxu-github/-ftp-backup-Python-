# -*- coding: utf-8 -*-
import sys
import os
import json
import time
from ftplib import FTP
from PopupProgressBar import PopupProgressBar


class Xfer(object):
    '''''
    @note: upload local file or dirs recursively to ftp server
    '''

    def __init__(self):

        self.__ftp = FTP()
        self.__ftp.encoding='utf-8'
        self.__port = 21
        self.__timeout = 60
        self.__Local=''
        self.__Remote=''
        self.__log_file=None
        self.__labelText = None  # Tkinter.StringVar()
        self.__file_list=[]
        self.__file_type=set()
        self.initEnv()
        #self.readData()
    def __del__(self):
        pass
    def set_filetype(self,newtype):
        '''
        将新的文件类型加入到设置中
        :param newtype: 新的文件类型
        :return:
        '''
        self.debug_print("尝试将%s类型文件加入设置"%newtype)
        if newtype in self.__file_type:
            self.debug_print("该类型已在设置中")
            return
        self.__file_type.add(newtype)
        self.debug_print("成功将%s类型文件加入设置" % newtype)

    def delete_filetype(self,deletetype):
        '''

        :param deletetype:将deletetype这一文件类型从设置中删除
        :return:
        '''
        self.debug_print("尝试将%s类型文件从设置中删除" % deletetype)
        if (deletetype in self.__file_type):
            self.__file_type.remove(deletetype)
            self.debug_print("成功将%s类型文件从设置中删除" % deletetype)
            return
        self.debug_print("该类型并未在设置之中，跳过")

    def clear_filetype(self):
        '''
        将文件类型设置清空
        :return:
        '''
        self.debug_print("已将文件设置清空")
        self.__file_type.clear()

    def set_localpath(self,localpath):
        '''
        设置本地备份目录
        :param localpath:本地目录
        :return:
        '''
        self.debug_print("将%s设置为本地目录"%localpath)
        self.__Local=localpath

    def set_remotepath(self,remotepath):
        '''
        设置远程目录
        :param remotepath:远程目录
        :return:
        '''
        self.debug_print("将%s设置为远程目录"%remotepath)
        self.__Remote=remotepath

    def setFtpParams(self, ip, uname='', pwd='', port=21, timeout=60):
        '''
        初始化ftp客户端
        :param ip: ip地址
        :param uname: 用户名
        :param pwd: 密码
        :param port: 端口号
        :param timeout: 超时设置
        :return:
        '''
        self.ip = ip
        self.uname = uname
        self.pwd = pwd
        self.__port = port
        self.__timeout = timeout
        self.__ftp.encoding='utf-8'

    def initEnv(self):
        '''
        环境初始化
        :return:
        '''
        if self.__ftp is None:
            self.__ftp = FTP()
        if (not self.__log_file):
            self.__log_file=open("log.txt",'a')

    def clearEnv(self):
        '''
        环境清理
        :return:
        '''
        self.debug_print("close()--->FTP退出")
        if self.__ftp:
            self.__ftp.close()
        self.__log_file.close()
        self.clear_filetype()

    def login(self):
        '''
        连接ftp
        :return:
        '''
        self.initEnv()
        try:
            self.debug_print('尝试连接%s'%self.ip)
            self.__ftp.connect(self.ip, self.__port, self.__timeout)
            self.debug_print('成功连接%s'%self.ip)
            self.debug_print('尝试以%s登录到%s'%(self.uname,self.ip))
            self.__ftp.login(self.uname, self.pwd)
            self.debug_print('成功登录到%s-%s' % (self.uname, self.ip))
            self.debug_print(self.__ftp.getwelcome())
        except Exception as err:
            self.debug_print("FTP 连接或登录失败，错误描述为 :%s"%err)
    def is_same_size(self,local_file,remote_file):
        '''
        判断远程和本地同名文件是否大小一致（若大小一致则不需要继续操作）
        :param local_file: 本地文件
        :param remote_file: 远程文件
        :return:1：大小一致，0：大小不一致
        '''
        try:
            remote_file_size=self.__ftp.size(remote_file)
        except Exception as err:
            remote_file_size=-1
        try:
            local_file_size=os.path.getsize(local_file)
        except Exception as err:
            local_file_size=-1
        if (remote_file_size==local_file_size):
            return 1
        else:
            return 0

    def uploadDir(self, localdir='./', remotedir='./'):
        '''
        上传文件夹
        :param localdir:本地目录
        :param remotedir: 远程目录
        :return:
        '''
        if not os.path.isdir(localdir):
            self.debug_print("本地目录 %s 不存在"%localdir)
            return
        try:
            self.__ftp.cwd(remotedir)
            self.debug_print("切换至远程目录：%s"%self.__ftp.pwd())
        except Exception:
            try:
                self.__ftp.mkd(remotedir)
                self.debug_print("尝试创建远程目录 :%s"%self.__ftp.pwd())
                self.__ftp.cwd(remotedir)
            except Exception as e:
                self.debug_print("在访问远程目录%s 是发生错误，错误描述为%s"%(remotedir,e))
                return

        for file in os.listdir(localdir):
            src = os.path.join(localdir, file)
            if os.path.isfile(src):
                self.uploadFile(src, file)
            elif os.path.isdir(src):
                try:
                    self.__ftp.mkd(file)
                except Exception as e :
                    self.debug_print("远程目录%s已存在，具体错误描述为：%s"%(file,e))
                self.debug_print("uploadDir--->上传目录：%s"%file)
                self.uploadDir(src, file)
            else:
                self.debug_print("uploadDir--->上传文件:%s"%file)
                self.uploadFile(src,file)
        self.__ftp.cwd('..')

    def uploadFile(self, localpath, remotepath):
        '''
        从本地上传文件到ftp
        :param localpath:本地文件
        :param remotepath: 远程文件
        :return:
        '''
        self.transfer_size=0
        if not os.path.isfile(localpath):
            self.debug_print("找不到%s"%localpath)
            return
        file_suffix=localpath.split('.')[-1]
        if (file_suffix not in self.__file_type and '*' not in self.__file_type):
            self.debug_print("跳过不在设置内的文件：%s"%file_suffix)
            return
        if self.is_same_size(localpath,remotepath):
            self.debug_print('跳过相等的文件：%s'%localpath)
            return
        buf_size=1024
        self.bar = PopupProgressBar('ftp transfer file:'+localpath)
        self.bar.start()
        self.file_size=os.path.getsize(localpath)
        self.__ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'),buf_size,callback=self.__process_print)
        self.debug_print("上传 %s 成功"%localpath)


    def downloadFile(self, remotepath="./", localpath='./'):
        '''
        下载文件
        :param remotepath: 远程文件路径
        :param localpath: 本地文件路径
        :return:
        '''
        self.transfer_size = 0
        if (self.is_same_size(localpath,remotepath)):
            return
        file_suffix=remotepath.split('.')[-1]
        if (file_suffix not in self.__file_type and '*' not in self.__file_type):
            self.debug_print("跳过不在设置内的文件：%s"%file_suffix)
            return
        try:
            buf_sz=1024
            self.bar = PopupProgressBar('ftp transfer file:' + localpath)
            self.bar.start()
            self.file_size = self.__ftp.size(remotepath)
            self.file=open(localpath,"wb")
            self.__ftp.retrbinary('RETR ' + remotepath, self.__file_write)
            self.file.close()

        except Exception as err:
            self.debug_print("下载文件%s时发生错误，错误描述为：%s"%(remotepath,err))
            return

    def downloadDir(self,remoteDir='./',localDir='./'):
        '''
        下载文件夹
        :param remoteDir:远程目录
        :param localDir: 本地目录
        :return:
        '''
        try:
            self.__ftp.cwd(remoteDir)
            self.debug_print("切换至远程目录:%s"%self.__ftp.pwd())
        except Exception as err:
            self.debug_print("访问远程文件夹%s时发生错误，错误描述为：%s"%(remoteDir,err))
            return
        if not os.path.isdir(localDir):
            self.debug_print("未找到本地文件夹%s,开始创建"%localDir)
            try:
                os.mkdir(localDir)
                self.debug_print("成功创建本地文件夹%s"%localDir)
            except Exception as err:
                self.debug_print("创建本地文件夹时发生错误，错误描述为%s"%err)
        self.__file_list=[]
        self.__ftp.dir(self.__get_dir_info)
        remote_files=self.__file_list
        self.__file_list=[]
        for item in remote_files:
            file_type=item[0]
            file_name=item[1]
            local_file=os.path.join(localDir,file_name)
            if (file_type[0]=='d'):
                self.debug_print("download_Dir--->下载子目录: %s"%file_name)
                self.downloadDir(file_name,local_file)
            elif file_type[0]=='-':
                self.debug_print("download_Dir--->下载文件: %s"%file_name)
                self.downloadFile(file_name,local_file)
        self.__ftp.cwd('..')
        self.debug_print("返回上层目录:%s"%self.__ftp.pwd())

    def backup(self):
        '''
        根据已设置好的本地目录和远程目录将文件上传至ftp服务器进行备份
        :return:
        '''
        if (not self.__Local):
            self.debug_print("尚未设置本地目录")
            return
        if (not self.__Remote):
            self.debug_print("尚未设置远程目录")
            return
        self.debug_print("开始从本地目录:%s 备份到远程目录：%s"%(self.__Local,self.__Remote))


        self.uploadDir(self.__Local,self.__Remote)
        self.debug_print("备份成功")

    def restore(self):
        '''
        根据已设置好的本地目录和远程目录将文件从ftp服务器上下载进行还原
        :return:
        '''
        if (not self.__Local):
            self.debug_print("尚未设置本地目录")
            return
        if (not self.__Remote):
            self.debug_print("尚未设置远程目录")
            return
        self.debug_print("开始从远程目录:%s 恢复到远程目录：%s"%( self.__Remote, self.__Local))
        self.downloadDir(self.__Remote,self.__Local)
        self.debug_print("恢复成功")

    def __process_print(self,block):
        '''
        用于显示下载和上传的进度条
        :param block:文件块
        :return:
        '''
        self.transfer_size=self.transfer_size+len(block)
        self.bar.value=self.transfer_size/self.file_size*100
        self.bar.text=format(self.transfer_size/self.file_size*100,'.2f')+'%'
        if self.bar.value>=100:
            time.sleep(0.2)
            self.bar.stop()

    def __file_write(self,data):
        '''用于下载时文件写入和显示下载进度'''
        self.file.write(data)
        self.__process_print(data)

    def debug_print(self,s):
        self.write_log(s)

    def write_log(self,log_str):
        '''
        记录日志
        :param log_str:日志
        :return:
        '''
        time_now=time.localtime()
        date_now=time.strftime('%Y-%m-%d-%H:%M:%S',time_now)
        format_log='%s ---> %s \n'%(date_now,log_str)
        print(format_log)
        self.__log_file.write(format_log)

    def deal_error(self,err):
        '''
        处理错误异常
        :param err:异常
        :return:
        '''
        self.write_log('发生错误:%s'%err)
        sys.exit()

    def __get_dir_info(self,line):
        '''
        获取文件信息，进行回调
        :param line:
        :return:
        '''
        file_arr=self.__get_file_info(line)
        if (file_arr[1] not in ['.','..']):
            self.__file_list.append(file_arr)

    def __get_file_info(self,line):
        '''
        获取文件信息，进行回调
        :param line:
        :return:
        '''
        l=line.split(' ')
        if (l):
            return l[0],l[-1]
        else:
            return None

if __name__ == '__main__':
    srcDir = r"D:\somedata"
   # srcFile = r'C:\sytst\sar.c'
    xfer = Xfer()
    #xfer.setFtpParams("118.25.85.251", "xuyi2", "12345687")
    xfer.login()
    xfer.restore()
    #xfer.uploadDir(srcDir)
   # xfer.downloadDir('./',"D:\\backup")
 #   xfer.upload(srcFile)
