#logs:
    #email sender fixer for timed out connection
    #login test connection check updated
    #lstrip and rstrip added
    
    
from tkinter import *
import socket
from PIL import ImageTk,Image
import pyqrcode
#from pyzbar.pyzbar import decode
#from PIL import Image
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



#admin email id
frm=""
pas=""

#encryption table( veingere's cipher)
key='YMCA'
table=[]
for i in range(256):
    temp=[]
    for j in range(i,256):
        temp.append(chr(j));
    for j in range(i):
        temp.append(chr(j))
    table.append(temp)


#encryption function
def encrypt(s):
    global key;
    global table
    res=""
    size=len(s);
    j=0
    for i in range(size):
        if(j>3):
            j=0;
        row=ord(key[j])
        col=ord(s[i])
        res+=table[row][col]
    return res;


#check internet Connection
def check_connection():
    try:
        socket.create_connection(("google.com",80))
        return 1
    except:
        return 0


#confirmation email with QR

def email_sender(to,f_name,l_name,file_1,file_2,num,dl,UID):
    
    name=f_name+' '+l_name
    
    #Admin Credential
    global frm
    global pas
    
    
    #filling up msg parts
    
    msg=MIMEMultipart()
    msg['from']=frm
    msg['to']=to
    msg['subject']=f'({UID}) Welcome {name} to JCBOSEUST Parking System'
    #print(msg['subject'])
    body=f'Dear Sir/Ma\'am,\nYou have Successfully been registered to the JCBOSEUST\'s Parking System with Following Information:\nName: {name}\nContact Number: {num}\nDriving License Number: {dl}\nPlease find the attachment and Keep it safe\nThanks and Regards,\nJCBOSEUST\nFaridabad,Haryana'
    #print(body)
    
    #attachments

    msg.attach(MIMEText(body,'plain'))
    x=open(file_1,'rb')
    y=open(file_2,'rb')
    
    #breaking and reading attachments
    
    p = MIMEBase('application', 'octet-stream')
    q = MIMEBase('application', 'octet-stream')
    p.set_payload((x).read())
    q.set_payload((y).read())
    
    #encoding attachments
    
    encoders.encode_base64(p)
    encoders.encode_base64(q)
    
    #adding attachments
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % file_1)
    q.add_header('Content-Disposition', "attachment; filename= %s" % file_2)
    msg.attach(p)
    msg.attach(q)
    
    #converting msg to string
    msg.as_string()
    
    if(check_connection()):
    
        try:
            #engaging servers
            server=smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()
            server.login(frm,pas)
            
            #sending message
            server.send_message(msg)
            server.quit()
            
        except Exception:
            display='1 Error(s) Found:\nInternet Connectivity Lost'
            window_new_main(display,'failed')
    else:
        display='1 Error(s) Found:\nInternet Connectivity Lost'
        window_new_main(display,'failed')
    
    

    
#button action
def submit_action():
    
    #calculating errors
    error=0
    sp1=check_spaces(UID)
    sp2=check_spaces(f_name)
    sp3=check_spaces(l_name)
    sp4=check_spaces(num)
    sp5=check_spaces(e_id)
    sp6=check_spaces(dl)
    sp7=check_num(num)
    sp8=0 #check_mail(e_id)
    sp9=not check_connection() 
    sp10=0
    if(sp1==0):
        sp10=check_UID(UID.get())
    error=sp1+sp2+sp3+sp4+sp5+sp6+sp7+sp8+sp9+sp10
    
    #failed window
    
    dispay=""
    if(error!=0):
        dispay=f"\n{error} Error(s) Found\n"
        if(sp1!=0):
            dispay+=f"\nUnique Id: {sp1} Space(s)"
        
        if(sp2!=0):
            dispay+=f"\nFirst Name: {sp2} Space(s)"
        
        if(sp3!=0):
            dispay+=f"\nLast Name: {sp3} Space(s)"
            
        if(sp4!=0):
            dispay+=f"\nPhone Number: {sp4} Space(s)"
            
        if(sp5!=0):
            dispay+=f"\nEmail Id: {sp5} Space(s)"
            
        if(sp6!=0):
            dispay+=f"\nDriving License: {sp6} Space(s)"
        
        if(sp7!=0):
            dispay+='\nInvalid Phone Number'
        
        if(sp8!=0):
            dispay+='\nPlease Register with a valid Gmail Account'
        
        if(sp9!=0):
            dispay+='\nInternet Connectivity Lost'
            
        if(sp10!=0):
            dispay+='\nUnique ID Contains Special Characters'
        
        window_new_main(dispay,'failed')
        return
        
    res=""
    if(len(num.get())==13):
        res=f"{var.get()}{UID.get().lstrip().rstrip()} {f_name.get().title().lstrip().rstrip()} {l_name.get().title().lstrip().rstrip()} {num.get().lstrip().rstrip()} {e_id.get().lstrip().rstrip()} {dl.get().lstrip().rstrip()}"
    else:
        res=f"{var.get()}{UID.get().lstrip().rstrip()} {f_name.get().title().lstrip().rstrip()} {l_name.get().title().lstrip().rstrip()} {'+91'+num.get().lstrip().rstrip()} {e_id.get().lstrip().rstrip()} {dl.get().lstrip().rstrip()}"
        
    #print(res)
    
    
    # Creating QR for Car
    
    file_name_car=UID.get()+'_car.png'
    rescar=res+' '+'car YMCA'
    rescar=encrypt(rescar)       #encryption
    qrcar=pyqrcode.create(rescar)
    qrcar.png(file_name_car,scale=10)
    
    
    #Creating QR for bike
    
    file_name_bike=UID.get()+'_bike.png'
    resbike=res+' '+ 'bike YMCA'
    resbike=encrypt(resbike)    # encrypt data
    qrbike=pyqrcode.create(resbike)
    qrbike.png(file_name_bike,scale=10)
    #print(rescar)
    #print(resbike)
    
    temp_UID=f"{var.get()}{UID.get()}"
    
    #sending QR to user's Email
    email_sender(e_id.get(),f_name.get().title(),l_name.get().title(),file_name_car,file_name_bike,num.get(),dl.get(),temp_UID)

    #deleting files
    
    os.unlink(file_name_car)
    os.unlink(file_name_bike)
    
    #successfull window
    window_new_main('Successful','success')
    

#exit button action
def exit_action_main(win):
    
    #clearing Screen

    f_name.delete(0,END)
    l_name.delete(0,END)
    num.delete(0,END)
    e_id.delete(0,END)
    dl.delete(0,END)
    UID.delete(0,END)
    c.deselect()
    
    #destroy exit window
    win.destroy()


#new window function
def window_new_main(text,status):
    
    win=Tk()
    
    win.title("Status")
    win.iconbitmap('icon.ico')
    
    if(status=="failed"):
        Label(win,text=f"Registration Failed",font="Times 13 bold",bg="red").grid(row=0,column=0)
        Label(win,text=f"{text}",font="Times 13 bold").grid(row=2,column=0)
        b2=Button(win,fg='red',text='EXIT',bg='light Green',command=win.destroy).grid(row=4,column=0)
    else:
        Label(win,text=f"Registration Successfull",font="Times 13 bold",bg="green").grid(row=0,column=0)
        b2=Button(win,fg='red',text='EXIT',bg='light Green',command=lambda :exit_action_main(win)).grid(row=4,column=0)
    
    win.mainloop()



#checking if spaces entered
def check_spaces(value):
    temp=list(value.get().split())
    if(len(temp)!=1):
        return 1
    return 0


#check correctness of the number
def check_num(num):
    temp=num.get()
    x=len(temp)
    error=0
    if(x!=10 and x!=13):
        error+=1
    if(x==13 and temp[0]!='+'):
        return error+1
    l=ord('0')
    h=ord('9')
    for i in range(1,x):
        t=ord(temp[i])
        if(t<l or t>h):
            error+=1
            break
    return error


#check correctness of the mail id    
def check_mail(mail):
    temp=mail
    size=len(temp)
    exten=''
    for i in range(size):
        if(temp[i]=='@'):
            exten=temp[i:size:]
            break
    test='@gmail.com'
    exten=exten.lower()
    if(test==exten):
        return 0
    return 1


#checking special characters from UID
def check_UID(uid):
    ln=ord('0')
    hn=ord('9')
    la=ord('a')
    ha=ord('z')
    lA=ord('A')
    hA=ord('Z')
    for i in uid:
        x=ord(i)
        if((x>=ln and x<=hn) or (x>=la and x<=ha) or (x>=lA and x<=hA)):
           continue
        else:
            return 1;
    return 0;


 #exit button action
def exit_action_log(win1,win2):
    
    win1.destroy()
    
    #destroy exit window
    win2.destroy()


#status new window
def window_new_login(text,status,win_log):
    
    win=Tk()
    
    win.title("Status")
    win.iconbitmap('icon.ico')
    
    if(status=="failed"):
        Label(win,text=f"Authorisation Failed",font="Times 13 bold",bg="red").grid(row=0,column=0)
        Label(win,text=f"{text}",font="Times 13 bold").grid(row=2,column=0)
        b2=Button(win,fg='red',text='EXIT',bg='light Green',command=win.destroy).grid(row=4,column=0)
    else:
        Label(win,text=f"Authorisation Successfull",font="Times 13 bold",bg="green").grid(row=0,column=0)
        b2=Button(win,fg='red',text='EXIT',bg='light Green',command=lambda :exit_action_log(win,win_log)).grid(row=4,column=0)
    
    win.mainloop()



#check user
def test_user(user,passw,win):
    if(check_mail(user)):
       window_new_login("Please Enter a Valid Gmail ID","failed",win)
       return;
     
    if(check_connection()==0):
        window_new_login("Internet Connectivity Lost","failed",win)
    else:
        try:
            server=smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()
            server.login(user, passw)
            global frm,pas
            frm=user
            pas=passw
            server.quit()
            window_new_login("Authorisation Successfull","Success",win)
            
        except Exception:
            window_new_login("Internet Connectivity Lost or Invalid Credentials","failed",win)
 
        


#login window
def login():
    win_log=Tk()
    
    # #width x hieght
    win_log.geometry('310x145')
    win_log.maxsize(310,145)
    win_log.minsize(310,145)
    
    win_log.title("Admin's Login Page")
    win_log.iconbitmap('icon.ico')
    
    Label(win_log,text="JCBOSEUST Paking",font='times 14 bold').grid(row=0,column=0,columnspan=2)
    Label(win_log,text="Welcome to Admin Control",font='times 12 bold').grid(row=1,column=0,columnspan=2)
    
    Label(win_log,text="Gmail Id",font='times 10 bold').grid(row=6,column=0)
    e_id = Entry(win_log, width=40, borderwidth=5)
    e_id.grid(row=6,column=1)

    Label(win_log,text="Password",font='times 10 bold').grid(row=7,column=0)
    pas=Entry(win_log, width=40, borderwidth=5)
    pas.config(show='*')
    pas.grid(row=7,column=1)
    
    b=Button(win_log,fg='red',text='Login',bg='light Green',command=lambda: test_user(e_id.get(),pas.get(),win_log)).grid(row=10,column=1)
        
    win_log.mainloop()




#main 

login()

if(frm!="" and pas!=""):                #if id and password is correct
    
    root=Tk()
    
    # #width x hieght
    root.geometry('595x380')
    root.maxsize(595,380)
    root.minsize(595,380)
    root.title("3-C Parking for JCBOSEUST")
    root.iconbitmap('icon.ico')
    
    
    Label(root,text="JCBOSEUST Paking",font='times 14 bold').grid(row=0,column=0,columnspan=2)
    Label(root,text="Welcome to Admin Control",font='times 12 bold').grid(row=1,column=0,columnspan=2)
    
    #logo of ymca
    
    my_img=ImageTk.PhotoImage(Image.open('logo.png'))
    Label(image=my_img).grid(row=2,column=0,columnspan=2)
    
    Label(root,text="*All Sections are Mandatory to Fill (Without Spaces)\n",fg='red').grid(row=4,column=0)
    
    #checkbox
    
    var=StringVar()
    c=Checkbutton(root,text="Employee",font='times 10 bold',variable=var,onvalue='E',offvalue='S')
    c.deselect()
    c.grid(row=5,column=1)
    
    
    #Inputs
    
    Label(root,text="Unique ID",font='times 10 bold').grid(row=6,column=0)
    UID = Entry(root, width=50, borderwidth=5)
    UID.grid(row=6,column=1)
    
    Label(root,text="First Name",font='times 10 bold').grid(row=7,column=0)
    f_name=Entry(root, width=50, borderwidth=5)
    f_name.grid(row=7,column=1)
    
    Label(root,text="Last Name",font='times 10 bold').grid(row=8,column=0)
    l_name=Entry(root, width=50, borderwidth=5)
    l_name.grid(row=8,column=1)
        
    Label(root,text="Phone Number",font='times 10 bold').grid(row=9,column=0)
    num=Entry(root, width=50, borderwidth=5)
    num.grid(row=9,column=1)
    
    Label(root,text="Mail ID",font='times 10 bold').grid(row=10,column=0)
    e_id=Entry(root, width=50, borderwidth=5)
    e_id.grid(row=10,column=1)
    
    Label(root,text="Driving License Number",font='times 10 bold').grid(row=11,column=0)
    dl=Entry(root, width=50, borderwidth=5)
    dl.grid(row=11,column=1)
    
    
    #SUbmit button
    Button(root,fg='red',text='Submit',bg='light Green',command=submit_action).grid(row=13,column=1)
    
    root.mainloop()