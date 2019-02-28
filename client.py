import socket
import select
import sys
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import tkinter.filedialog
import _thread
import os

import time
import method
from loginPage import *
from chatPage import ChatPage

HOST = "127.0.0.1"
PORT = 65432      
User = None
user2room={}
files=[]

def recv_file(sock,sender,loc,file_name):
    Msg="{0}{1}\r\n{2}\r\n{3}".format(DOWNFILE,sender,loc,file_name)
    method.send(sock,Msg)
    print("request:",file_name)    
    
def show_msg(sender,msg,color,is_file=False):
    text_recv.config(state=NORMAL)
    text_recv.see(END)
    msgcon = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    text_recv.insert(END, "{0} {1}\n".format(sender,msgcon), color)
    if is_file==False:
        text_recv.insert(END, "{0}\n".format(msg))
    else :
        b1=Button(text_recv,text='点击下载',command=lambda: recv_file(sock,sender,"",msg))
        text_recv.insert(END, "发送了文件：{0} ".format(msg))
        text_recv.window_create(INSERT,window=b1)
        text_recv.insert(END, "\n\n")
    text_recv.see(END)        
    text_recv.config(state=DISABLED)
    
def room_exists(room):
    if room is None:
        return False
    if int(room.master.winfo_exists())==0:
        return False
    return True
        
def listener(sock,root):
    print("then?")
    listen_lis=[sock]
    while True:
        reads,writes,errors=select.select(listen_lis,[],[])
        for master in reads:
            if master==sock:
                """
                content = master.recv(4096)
                if not content :
                    print('Disconnected from chat server')
                data=str(content,encoding = "utf8")
                """
                try:
                    data, rest=method.receive(master)
                except Exception as e:
                    print(e)    
                    messagebox.showerror('Error',"接收出错")
                    continue
                
                if len(data)==0:
                    print('wrong data')
                    continue
                try:                        
                    msg_type=int(data[0:3])
                    if (msg_type==LOGIN_INFO):
                        new_user=data[3:]
                        user_list.append(new_user)
                        show_msg("<System>","{0} login!\n".format(new_user),"red")
                        
                        room=user2room.get(new_user) 
                        if room is not None:
                            room.show_msg("<System>","{0} login!\n".format(new_user),"red")
                            room.state=True
                            
                        userBox.insert(END,new_user)      
                        
                    elif (msg_type==LOGOUT_INFO):
                        out_user=data[3:]
                        userBox.delete(user_list.index(out_user))      
                        show_msg("<System>","{0} logout!\n".format(out_user),"red")
                        
                        room=user2room.get(out_user) 
                        if room_exists(room)==True:
                            room.show_msg("<System>","{0} logout!\n".format(out_user),"red")
                            room.state=False
                            
                        print("Cur: ",user_list,out_user)
                        user_list.remove(out_user)
                    
                    elif (msg_type==SENDMSG_ERROR):
                        messagebox.showerror("Error","消息发送出现错误！请重试！")
                        
                    elif (msg_type==SEND_ALL):
                        sender,content_len=data[3:].split("\r\n")
                        content_len=int(content_len)
                        content=method.receive(master,content_len-len(rest))
                        content=rest+content
                        assert len(content)==content_len
                        content=content.decode("utf-8")
                            
                        show_msg(sender,content,'blue')                  
                    
                    elif (msg_type==SEND_NONE):
                        receiver=data[3:]
                        room=user2room.get(receiver) 
                        if room_exists(room)==True:
                            room.show_msg("<System>","Error! {0} is offline! \n".format(receiver),"red")
                            
                    elif (msg_type==SEND_PER):
                        sender,content_len=data[3:].split("\r\n")
                        content_len=int(content_len)
                        content=method.receive(master,content_len-len(rest))
                        content=rest+content
                        assert len(content)==content_len
                        content=content.decode("utf-8")
                            
                        if room_exists(user2room.get(sender))==False: 
                            user2room[sender]=ChatPage(top1,User,sender,sock)
                        user2room[sender].show_msg(sender,content,'blue')
                        
                    elif (msg_type==SENDFILE_SUCCESS):
                        messagebox.showinfo('Info',"发送成功!")
                        print("send file successfully")
                        
                    elif (msg_type==SENDFILE_ERROR):
                        receiver=data[3:]
                        room=user2room.get(receiver) 
                        if room_exists(room)==True:
                            room.show_msg("<System>","Error! 文件传输出错！ \n".format(receiver),"red")
                            
                    elif (msg_type==SENDFILE_ALL):
                        sender,content=data[3:].split("\r\n")
                        show_msg(sender,content,'blue',is_file=True)        
                        
                    elif (msg_type==SENDFILE_NONE):
                        receiver=data[3:]
                        room=user2room.get(receiver) 
                        if room_exists(room)==True:
                            room.show_msg("<System>","Error! {0} is offline! \n".format(receiver),"red")    
                            
                    elif (msg_type==SENDFILE_PER):
                        sender,content=data[3:].split("\r\n")
                        if room_exists(user2room.get(sender))==False: 
                            user2room[sender]=ChatPage(top1,User,sender,sock)
                        user2room[sender].show_msg(sender,content,'blue',is_file=True)
                     
                    elif (msg_type==DOWNFILE_NONE):
                        messagebox.showerror("Error","该文件已不存在！")
                        
                    elif (msg_type==DOWNFILE_SUCCESS):
                        file_name, file_size=data[3:].split("\r\n")
                        file_size=int(file_size)
                        file_data=method.receive(master,file_size-len(rest))
                        file_data=rest+file_data
                        assert file_size==len(file_data)
                        print("receive file: ",file_name) 
                        
                        file_path=tkinter.filedialog.askdirectory()
                        file_path=os.path.join(file_path,file_name)
                        with open(file_path,"wb") as f:
                            f.write(file_data)
                        messagebox.showinfo('Info',"下载成功！\n已保存到："+file_path)
                        
                    elif (msg_type==WRONG_MESSAGE):
                        messagebox.showerror("Error","请求错误！请重试！")
                except Exception as e:
                    print(msg_type,data,e)
                                        
def ask_user_list(sock):
    msg=str(ASKUSERS)
    #sock.send(bytes(msg,encoding="utf-8"))
    method.send(sock,msg)
    lis=[]
    try:
        data, rest=method.receive(sock)
        assert data[:3]==str(ASKUSERS_RET)
        lis_len=int(data[3:])
        print(lis_len)
        lis=method.receive(sock,lis_len-len(rest))
        lis=rest+lis
        assert len(lis)==lis_len
        lis=lis.decode("utf-8")
    except Exception as e:
        print(e)
        return None
        
    return lis.split("\r\n")
 
def send_all(): 
    print("Now: ",user_list)
    send_text=text_msg.get('0.0', END)
    if send_text is None :
        return 
    if len(send_text)==0:
        return
     
    show_msg("<我>",send_text,"green") 
    
    content=send_text.encode("utf-8")
    Msg="{0}{1}\r\n{2}".format(SENDMSG,"",len(content))
    method.send(sock,Msg,content)
    
    text_msg.delete('0.0', END)
    
def send_file_all():
    file_path = tkinter.filedialog.askopenfilename(title='选择文件')
    if os.path.exists(file_path)==False:
        return 
    state=method.upload_file(sock,file_path,"")             
    if state==False:
        messagebox.showerror('Error',"文件大小不能超过50M")
        
    show_msg("<我>","发送文件：{0}\n".format(file_path),"green")
    print(file_path)
    
def launch_private(event):
    choice=userBox.get(userBox.curselection())
    print("select:",choice,type(choice),User) 
    if (choice==User):
        return
    if room_exists(user2room.get(choice))==False:
        user2room[choice]=ChatPage(top1,User,choice,sock)    
        
if __name__=="__main__":
    root = tk.Tk()
   
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST,PORT))
        print(sock)
    except:
        print("Fail to connect (%s, %s)"% (HOST,PORT))
        exit()
    
    print("begin")
    login=LoginPage(master=root,sock=sock)        
    if login.flag is None:
        print("finish")
        exit()
    else :
        print(login.flag)
        User=login.flag
        
    print("build room")
    
    user_list=ask_user_list(sock)
    if user_list is None:
        print("连接失败！")
        exit()
        
    top1 = Tk()
    top1.title("聊天室 {0}".format(User))
    top1.geometry("600x400+200+20")

    text_recv = Text(top1, width=58, height=19)
    text_recv.place(x=0, y=0)
    text_recv.tag_config('green', foreground='#008b00')
    text_recv.tag_config('red', foreground='#FF0000')
    text_recv.tag_config('blue', foreground='#0000FF')
    text_recv.config(state=DISABLED)
    
    text_msg = Text(top1, width=58, height=6)
    text_msg.place(x=0, y=275)
    sb0 = Scrollbar(top1, orient="vertical")
    sb0.place(x=410, y=275, height=80)
    text_msg.config(yscrollcommand=sb0.set)
    sb0.config(command=text_msg.yview)
    
    sb = Scrollbar(top1, orient="vertical")
    sb.place(x=410, y=0, height=270)
    text_recv.config(yscrollcommand=sb.set)
    sb.config(command=text_recv.yview)
    
    userBox = Listbox(top1, width=23, height=18)
    userBox.place(x=423, y=20)
    userBox.bind('<Double-Button-1>',launch_private)
    
    sb1 = Scrollbar(top1)
    sb1.place(x=586, y=22, height=341)   
    userBox.config(yscrollcommand=sb1.set)
    sb1.config(command=userBox.yview)
    for user in user_list:
        userBox.insert(END,user)
     
    Label(top1, text="在线成员", font=('黑体', 10)).place(x=480, y=0)
     
    _thread.start_new_thread(listener,(sock,top1))
    
    Bsend_all = Button(top1, text='发送', command=send_all)
    Bsend_all.place(x=385, y=365)
    
    Bsend_file = Button(top1, text='传送文件', command=send_file_all)
    Bsend_file.place(x=300, y=365)
    #root.withdraw()
    
    top1.mainloop()
    
    

        
   
    