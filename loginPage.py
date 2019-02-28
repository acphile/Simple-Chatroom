from tkinter import *
from tkinter import messagebox
from Constant import *
import method

class LoginPage:
    def __init__(self, master=None, sock=None):
        self.username = StringVar()
        self.password = StringVar()
        self.sock=sock
        self.flag=None
        
        self.master = master
        master.resizable(width=False, height=False)
        master.geometry('240x150')
        master.title("A Little Chatroom")
        
        Label(master, text = '账户:').grid(row=1, stick=W, padx=10,pady=10)
        self.nameE=Entry(master, textvariable=self.username).grid(row=1, column=1, stick=E,padx=10,pady=10)
        Label(master, text = '密码:').grid(row=2, stick=W, padx=10,pady=10)
        self.pwdE=Entry(master, textvariable=self.password, show='*').grid(row=2, column=1, stick=E,padx=10,pady=10)
        self.Blogin=Button(master, text='登陆', command=self.login).grid(row=3, stick=W, padx=10,pady=10)
        self.Bregister=Button(master, text='注册', command=self.register).grid(row=3, column=1, stick=E,padx=10,pady=10)
        master.mainloop()
        
    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        print(pwd)
        if not user:
            messagebox.showerror('Error',"用户名不能为空")
            #self.pwdE.delete(0, END)
            self.password.set("")
            return
        if not pwd:
            messagebox.showerror('Error',"密码不能为空")
            #self.pwdE.delete(0, END)
            self.password.set("")
            return
            
        msg=str(LOGIN)+user+"\r\n"+pwd
        #self.sock.send(bytes(msg,encoding='utf-8'))
        method.send(self.sock,msg)
        try:
            #receive= self.sock.recv(1024).decode()
            receive,_=method.receive(self.sock)
        except Exception as e:
            print(e)    
            messagebox.showerror('Error',"连接失败，请关闭重连！")
        
        print(receive)
        if receive==str(LOGIN_SUCCESS):
            self.flag=user
            messagebox.showinfo('Info',"登陆成功")
            self.master.destroy()
        elif receive==str(LOGIN_WRONG):
            messagebox.showerror('Error',"用户名不存在或密码错误")
        elif receive==str(LOGIN_REPEAT):
            messagebox.showerror('Error',"该用户已经登陆！")
            
    def register(self):
        def usrsign():
            user = str(ns.get())
            pwd = str(pwds.get())
            pwd1 = str(pwds1.get())
     
            if not user or len(user)==0 or user.find(" ")!=-1 or user.find("\t")!=-1:
                print("用户名不合法")
                messagebox.showerror('Error',"用户名不合法")
                return
            if pwd != pwd1:
                print("输入的两次密码不一致，请重新输入！")
                pwds.set("")
                pwds1.set("")
                messagebox.showerror('Error',"输入的两次密码不一致，请重新输入！")
                return
                
            msg=str(REGISTER)+user+"\r\n"+pwd
            #self.sock.send(bytes(msg,encoding='utf-8'))
            method.send(self.sock,msg)
            
            #data = self.sock.recv(1024).decode()
            try:
                data,_=method.receive(self.sock)
            except Exception as e:
                print(e)    
                messagebox.showerror('Error',"发送失败，请重试！")
            
            if data == str(REGISTER_SUCCESS):
                print("注册成功")
                messagebox.showinfo('Info',"注册成功")
                top2.destroy()
                return
            elif data == str(REGISTER_ERROR):
                print("用户名重复")
                messagebox.showerror('Error',"用户名已存在")
            return
            
        top2 = Toplevel(self.master)
        top2.title("注册")
        top2.geometry("330x200")
        Label(top2, text="用户名:").place(x=50, y=40)
        Label(top2, text="密码:").place(x=50, y=80)
        Label(top2, text="确认密码:").place(x=50, y=120)
     
        ns = StringVar()
        ns.set("")
        entrynames = Entry(top2, textvariable=ns)
        entrynames.place(x=120, y=40)
     
        pwds = Variable()
        entrypwds = Entry(top2, textvariable=pwds,show='*')
        entrypwds.place(x=120, y=80)
     
        pwds1 = Variable()
        entrypwds1 = Entry(top2, textvariable=pwds1,show='*')
        entrypwds1.place(x=120, y=120)
     
        b_sign = Button(top2, text='注册', command=usrsign)
        b_sign.place(x=160, y=150)
     
        top2.mainloop()

        
        

            
            