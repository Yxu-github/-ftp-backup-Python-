#encoding:utf-8
#name:mod_config.py
import configparser
import os,time
from ftpclass3 import Xfer


def write_log(log_str):
    '''
    记录日志
    :param log_str:日志
    :return:
    '''
    time_now = time.localtime()
    date_now = time.strftime('%Y-%m-%d-%H:%M:%S', time_now)
    format_log = '%s ---> %s \n' % (date_now, log_str)
    print(format_log)
    with open("log2.txt","a+") as f:
        f.write(format_log)
def debug_print( s):
    write_log(s)

if __name__=='__main__':

    print(os.getcwd())
    __SECTION="users"
    xfer=Xfer()
    conf=configparser.ConfigParser()
    root_dir = os.path.split(os.path.realpath(__file__))[0]
    try:
        conf.read(os.path.join(root_dir,'key.ini'))
    except Exception:
        debug_print("打开设置文件时错误")
    for __SECTION in conf.sections():
        debug_print(str(__SECTION))
        try:
            host=conf.get(__SECTION,"host")
        except Exception:
            debug_print("服务器地址未设置")
            continue
        try:
            username=conf.get(__SECTION,"username")
        except Exception:
            username=None
        try:
            pwd=conf.get(__SECTION,"password")
        except Exception:
            pwd=None

        xfer.setFtpParams(host,username,pwd)
        try:
            debug_print("尝试对%s服务器进行登录"%host)
            xfer.login()
        except:
            debug_print("登录失败")
        try:
            localpath=(conf.get(__SECTION,"localpath"))
        except Exception:
            debug_print("缺少本地目录设置")
            continue
        xfer.set_localpath(localpath)
        try:
            remotepath=conf.get(__SECTION,"remotepath")
        except Exception:
            debug_print("缺少远程目录设置")
            continue
        xfer.set_remotepath(remotepath)
        try:
            for i in conf.get(__SECTION,"file_type").split(','):
                xfer.set_filetype(i)
        except Exception:
            xfer.set_filetype('*')

        try:
            Backup=conf.getboolean(__SECTION,"backup")
        except:
            Backup=False
        try:
            Restore=conf.getboolean(__SECTION,"restore")
        except:
            Restore=False
        if (Backup==Restore):
            debug_print("备份和恢复的设置相同，请检查")
            continue
        if (Backup):
            xfer.backup()
        if (Restore):
            xfer.restore()
        xfer.clearEnv()
