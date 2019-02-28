import socket
import sys
import os
import select
from Constant import *

import method
HOST="127.0.0.1"
PORT = 65432       
buffer_size=4096

def broadcast_data(sender, message,addition=b""):
    print("broadcast: ",message)
    for receiver in connections:
        if receiver!=sock and receiver!=sender and conn2user.get(receiver) is not None:
            print(receiver,conn2user.get(receiver))
            try :
                #receiver.sendall(message)
                method.send(receiver,message,addition)
                    
            except Exception as e:
                print("broadcast error",e,receiver)
                #release(receiver)
            

def login(conn,msg):
    try:
        user,pwd=msg.split("\r\n")
        assert user.find("\t")==-1
        assert pwd.find("\t")==-1       
    except Exception as e:
        print("Wrong login",e)
        return str(WRONG_MESSAGE)    
        
    if not os.path.exists("user_list.txt"):
        with open("user_list.txt",'w') as f:
            pass
    if user2conn.get(user) is not None:
        if user2conn[user]!=conn:
            return str(LOGIN_REPEAT)
            
    with open("user_list.txt","r") as f:
        for line in f.readlines():
            u,p=line.strip("\n").split("\t")
            if u==user and pwd!=p: 
                #print(len(user),len(pwd),len(p),len(u))
                return str(LOGIN_WRONG)
            elif u==user and pwd==p:                       
                conn2user[conn]=user
                user2conn[user]=conn
                broadcast_data(conn,"{0}{1}".format(LOGIN_INFO,user)) 
                return str(LOGIN_SUCCESS)
                
    return str(LOGIN_WRONG)

def register(conn,msg):
    try:
        user,pwd=msg.split("\r\n")
        assert user.find("\t")==-1
        assert pwd.find("\t")==-1
    except Exception as e:
        print("Wrong register",e)
        return str(WRONG_MESSAGE)  
        
    if not os.path.exists("user_list.txt"):
        with open("user_list.txt",'w') as f:
            pass
    with open("user_list.txt","r") as f:
        for line in f.readlines():
            u,p=line.strip("\n").split("\t")
            if u==user: 
                return str(REGISTER_ERROR)
                
    with open("user_list.txt","a") as f:
        f.write("{0}\t{1}\n".format(user,pwd))
   
    return str(REGISTER_SUCCESS)
  
def send_msg(conn,text,rest):  
    try:
        sender=conn2user[conn]
        receiver, content_len=text.split("\r\n")
        content_len=int(content_len)       
    except Exception as e:
        print("Wrong message",e)
        return str(WRONG_MESSAGE)
        
    try:
        content=method.receive(conn,content_len-len(rest))
        content=rest+content
        if len(content)!=content_len:
            return "{0}{1}".format(str(SENDMSG_ERROR),receiver)
    except Exception as e:
        print("Wrong text",e)
        return "{0}{1}".format(str(SENDMSG_ERROR),receiver)    
        
    if len(receiver)==0:
        broadcast_data(conn,"{0}{1}\r\n{2}".format(SEND_ALL,sender,content_len),addition=content) 
    else:
        corres=user2conn.get(receiver)
        if corres is None :
            print("NO")
            #conn.send(bytes(str(SEND_NONE)+receiver,encoding="utf-8"))
            Msg=str(SEND_NONE)+receiver
            return Msg             
        #corres.send(bytes("%3d%2d%s%4d%s"%(SEND_PER,len(sender),sender,len_content,content),encoding="utf-8"))        
        Msg="{0}{1}\r\n{2}".format(SEND_PER,sender,content_len)
        method.send(corres,Msg,content)
        
    return None
    
def handle_file(conn,msg,rest):
    try:
        #print("length:",len(msg.split("\r\n")),msg.encode())
        receiver,file_name,file_size=msg.split("\r\n")
        file_size=int(file_size)
        sender=conn2user[conn]
    except Exception as e:
        print("Wrong file info",e)
        return str(WRONG_MESSAGE)
        
    try:
        file_data=method.receive(conn,file_size-len(rest))
        file_data=rest+file_data
        if len(file_data)!=file_size:
            return "{0}{1}".format(str(SENDFILE_ERROR),receiver)
        
    except Exception as e:
        print("Wrong file",e)
        return "{0}{1}".format(str(SENDFILE_ERROR),receiver)
        
    print("receive file: ",file_size,len(file_data))    
    flip="__{0}_{1}__".format(sender,receiver)
    if os.path.exists(flip)==False:
        os.makedirs(flip)
    path=os.path.join(flip,file_name)
    with open(path,"wb") as f:
        f.write(file_data)
        
    if len(receiver)==0:
        broadcast_data(conn,"{0}{1}\r\n{2}".format(SENDFILE_ALL,sender,file_name)) 
    else:
        corres=user2conn.get(receiver)
        if corres is None :
            print("NO")
            Msg=str(SENDFILE_NONE)+receiver
            method.send(conn,Msg)
            return             
               
        Msg="{0}{1}\r\n{2}".format(SENDFILE_PER,sender,file_name)
        method.send(corres,Msg)
        
    return str(SENDFILE_SUCCESS)

def handle_download(conn,msg):
    try:
        #print("length:",len(msg.split("\r\n")),msg.encode())
        sender, loc, file_name=msg.split("\r\n")
        receiver=conn2user[conn]
    except Exception as e:
        print("Wrong info",e)
        return str(WRONG_MESSAGE)
    
    file_path=os.path.join("__{0}_{1}__".format(sender,loc),file_name)
    if os.path.exists(file_path)==False:
        return str(DOWNFILE_NONE)
    file_size=os.stat(file_path).st_size
    method.send(conn,"{0}{1}\r\n{2}".format(str(DOWNFILE_SUCCESS),file_name,file_size),method.read_file(file_path))        
    return None
     
def handle(conn,msg,rest):
    try:
        rtype=int(msg[0])
    except Exception as e:
        print("wrong request!",e)
        method.send(conn,str(WRONG_MESSAGE))
        return
        
    state="None"
    if rtype==LOGIN:
        state=login(conn,msg[1:])
        
    elif rtype==REGISTER:
        state=register(conn,msg[1:])
        #print(state)               
        
    elif rtype==SENDMSG:
        state=send_msg(conn,msg[1:],rest)
        if state is None:
            return 
        
    elif rtype==LOGOUT:
        user=conn2user.get(conn)
        if user is not None:
            del user2conn[user]
            conn2user[conn]=None 
            broadcast_data(conn,"{0}{1}".format(LOGOUT_INFO,user)) 
        return 
        
    elif rtype==ASKUSERS:
        lis=list(user2conn.keys())
        msg="\r\n".join(lis)
        msg=msg.encode("utf-8")
        header=str(ASKUSERS_RET)+str(len(msg))
        method.send(conn,header,msg)
        print(msg)
        return
        
    elif rtype==SENDFILE:
        state=handle_file(conn,msg[1:],rest)
    
    elif rtype==DOWNFILE:
        state=handle_download(conn,msg[1:])
        if state is None:
            return 
            
    print(rtype,state)
    #conn.sendall(bytes(state,encoding="utf-8"))
    method.send(conn,state)
    
def release(conn):
    print(conn,"disconnect")
    connections.remove(conn)
    if user2conn.get(conn2user[conn])==conn:
        user=conn2user[conn]
        broadcast_data(conn,"{0}{1}".format(LOGOUT_INFO,user)) 
        del user2conn[user]
        
    conn.close()    
    del conn2user[conn]
    
if __name__=="__main__":
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    print("start server",HOST,PORT)
    conn2user={}
    user2conn={}
    connections=[sock]
    while True:
        reads,writes,errors=select.select(connections,[],[])
        for cur in reads:
            if cur==sock: #new connection
                conn, addr = sock.accept()
                print("new connection",addr)
                #broadcast_data(conn, bytes("[%s:%s] entered room\n" % addr,encoding="utf-8"))
                connections.append(conn)
                conn2user[conn]=None
                print(connections)
                  
            else: #old connection
                print("now: ",cur)
                data=None                
                try:
                    #data = cur.recv(buffer_size)
                    data,rest=method.receive(cur)
                    
                except Exception as e:
                    print(e)
                    release(cur)
                    continue
                                    
                if data:
                    #content=str(data,encoding = "utf-8")
                    print("request: ",data.encode("utf-8"))
                    if len(data)==0:
                        print("Wrong message",cur)
                        #release(cur) 
                    else :
                        handle(cur,data,rest)
                else:
                    print("something error2")
                    release(cur)
                    
    sock.close()
                
              
            
                
    