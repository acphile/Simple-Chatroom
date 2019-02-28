from tkinter import *
from tkinter import messagebox
import tkinter.filedialog
from Constant import *
from Constant import *
import time
import method
import os

class ChatPage:
    def __init__(self, father, user, receiver, sock,state=True):
        self.state=state
        self.user=user
        self.master=Toplevel(father)
        self.master.title("与 {0} 的聊天".format(receiver))
        self.master.geometry("425x400")
        self.receiver=receiver
        self.sock=sock
        
        self.text_recv = Text(self.master, width=58, height=19)
        self.text_recv.place(x=0, y=0)
        self.text_recv.tag_config('green', foreground='#008b00')
        self.text_recv.tag_config('red', foreground='#FF0000')
        self.text_recv.tag_config('blue', foreground='#0000FF')
        self.text_recv.config(state=DISABLED)
        
        self.text_msg = Text(self.master, width=59, height=6)
        self.text_msg.place(x=0, y=275)
        self.sb0 = Scrollbar(self.master, orient="vertical")
        self.sb0.place(x=410, y=275, height=80)
        self.text_msg.config(yscrollcommand=self.sb0.set)
        self.sb0.config(command=self.text_msg.yview)
        
        self.sb = Scrollbar(self.master, orient="vertical")
        self.sb.place(x=410, y=0, height=270)
        self.text_recv.config(yscrollcommand=self.sb.set)

        self.sb.config(command=self.text_recv.yview)
        self.Bsend = Button(self.master, text='发送', command=self.send)
        self.Bsend.place(x=385, y=365)
        self.Bsend_file = Button(self.master, text='传送文件', command=self.upload_file)
        self.Bsend_file.place(x=300, y=365)
    
    
    def show_msg(self,sender,msg,color,is_file=False):
        self.text_recv.config(state=NORMAL)
        self.text_recv.see(END)
        msgcon = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        self.text_recv.insert(END, "{0} {1}\n".format(sender,msgcon), color)
        if is_file==False:
            self.text_recv.insert(END, "{0}\n".format(msg))
        else :
            b1=Button(self.text_recv,text='点击下载',command=lambda: self.recv_file(self.sock,sender,self.user,msg))
            self.text_recv.insert(END, "发送了文件：{0} ".format(msg))
            self.text_recv.window_create(INSERT,window=b1)
            self.text_recv.insert(END, "\n\n")
        self.text_recv.see(END)    
        self.text_recv.config(state=DISABLED)    
        
    def recv_file(self,sock,sender,loc,file_name):
        Msg="{0}{1}\r\n{2}\r\n{3}".format(DOWNFILE,sender,loc,file_name)
        method.send(sock,Msg)
        print("request:",file_name)    
        
    def send(self):
        send_text=self.text_msg.get('0.0', END)
        if send_text is None :
            return 
        if len(send_text)==0:
            return
     
        if self.state==False:
            messagebox.showerror('Error',"对方已下线!")
            return 
            
        self.show_msg("<我>",send_text,"green") 
        
        content=send_text.encode("utf-8")
        Msg="{0}{1}\r\n{2}".format(SENDMSG,self.receiver,len(content))
        method.send(self.sock,Msg,content)
    
        self.text_msg.delete('0.0', END)
        
    def upload_file(self):
        if self.state==False:
            messagebox.showerror('Error',"对方已下线")
            return 
            
        file_path = tkinter.filedialog.askopenfilename(title='选择文件')
        if os.path.exists(file_path)==False:
            return 
        state=method.upload_file(self.sock,file_path,self.receiver)             
        if state==False:
            messagebox.showerror('Error',"文件大小不能超过50M")
            
        self.show_msg("<我>","发送文件：{0}\n".format(file_path),"green")
        print(file_path)
        
        

            
            