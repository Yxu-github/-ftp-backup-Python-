# 根据配置文件借助ftp进行本地文件自动备份或自动恢复的Python脚本

### Xfer.py 
ftp相关操作
### main.py
脚本主体
## 具体使用方式
创建key.ini
自己写一个section，并设置好host,username,password,localpath(本地文件目录),remotepath（远程文件目录）,file_type（要操作的文件类型）,backup（是否进行备份）,restore（是否进行恢复）
