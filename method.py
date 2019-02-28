import socket
import os
from Constant import *
buffer_size=2048
max_file_size=1024*1024*50

def read_file(file_path):
    with open(file_path,"rb") as f:
        content=f.read()
    return content
    
def upload_file(sock,file_path,receiver):
    file_name=os.path.basename(file_path)
    file_size=os.stat(file_path).st_size
    
    if file_size>max_file_size:
        return False
        
    file_info="{0}{1}\r\n{2}\r\n{3}".format(str(SENDFILE),receiver,file_name,file_size)    
    file_content=read_file(file_path)    
    send(sock,file_info,file_content)
        
    return True
 
def send(sock,header,msg=b""):
    byte_msg=bytes(header+"\n\n",encoding="utf-8")+msg    
    #length=len(byte_msg)
    #print(length)
    #sock.sendall(bytes(str(length),encoding="utf-8"))
    sock.sendall(byte_msg)
   
def receive(sock,recv_size=None):
    if recv_size is None:
        data=sock.recv(1024)   
        for i in range(len(data)-1):
            if data[i]==10 and data[i+1]==10:
                header=data[:i].decode("utf-8")
                rest=data[i+2:]
                return header,rest
        return data.decode("utf-8"),""
        
    cur_data=b""
    size=0
    while size<recv_size:
        data=sock.recv(buffer_size)
        if len(data)==0:
            break
        size+=len(data)
        cur_data+=data
    return cur_data
    
        
    
    