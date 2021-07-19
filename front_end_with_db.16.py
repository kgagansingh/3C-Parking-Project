#logs:
    #added decryption
    #email and sms server timed out failure fixed

import sqlite3
import cv2
from pyzbar.pyzbar import decode
from twilio.rest import Client
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from email.mime.base import MIMEBase
#from email import encoders
#import numpy as np
#import zbar
import pyttsx3
import socket


#decryption requirement
key='YMCA'
table=[]
for i in range(256):
    temp=[]
    for j in range(i,256):
        temp.append(chr(j));
    for j in range(i):
        temp.append(chr(j))
    table.append(temp)


#decryption function
def decrypt(s):
    global key;
    global table
    res=""
    size=len(s);
    j=0
    for i in range(size):
        if(j>3):
            j=0;
        row=ord(key[j])
        for k in range(256):
            if(table[row][k]==s[i]):
                res+=table[0][k]
    return res;



#connecting with sqllite3
conn=sqlite3.connect("parking.db")
db=conn.cursor()


#Account access in twillio
ac='ACfa0cc1561b5df4659eba4d3588f4ac84'
tok=''
#client=Client(ac,tok)


#configuring text to speak
engine=pyttsx3.init()
voices=engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)


#select cam function
def select_cam():
    
    print("\nPlease Select camera from the Available Options:")
    speak("\nPlease Select camera from the Available Options:")
    
    idx=-1
    cam_avail=0
    i=1
    while True:
        while(i<21):

            cap=cv2.VideoCapture(i-1,cv2.CAP_DSHOW)
            if(cap.isOpened()):       #if camera opens
                cam_avail=1
                while True:
                    _,frame=cap.read()
                    cv2.imshow(f'''Cam {i}:Press 'y' to select this Cam else press 'Escape' ''',frame)
                    t=cv2.waitKey(1)
                    if t== 27:          #if escape pressed
                        break;
                    elif(t==ord('y') or t==ord('Y')):       #if y pressed
                    
                        print(f'\nCamera: {i} has been Successfully Selected')
                        speak(f'Camera: {i} has been Successfully Selected')
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        return i-1
                cap.release()
                cv2.destroyAllWindows()
                
            cap.release()
            i+=1
        
        if(cam_avail==0):
            print("\nNo Operational Camera Found")
            speak("No Operational Camera Found")
            
        elif(idx==-1):
            print('\nOperational Camera Found but not Selected by the User')
        choice=input("\ndo you want to try again?\ny/n: ").lower()
        if(choice=='n'):
            return -1
        else:
            i=1


#internet connectivuity check
def test_connection():
    try:
        socket.create_connection(("Google.com",80))
        return 1
    except :
        return 0


#speak function
def speak(s):
    engine.say(s)
    engine.runAndWait()
    
#note to exit the app anytime
print("Note: Press Escape to quit the Apllication\n")

#user input to  clear files or not
choice=input("Do you want to Clear all the Occupied Spots?\ny/n: ")
choice=choice.lower()

# update clearing 
if(choice=='y'):
    
    #confirmation
    temp=input("Please Confirm to Clear all Spots?\ny/n: ")
    temp=temp.lower()
    if(temp=='y'):
        #dekleting already exixted tables
        db.execute('drop table if exists car')
        db.execute('drop table if exists bike')
        
        db.execute('drop table if exists bike_entry')
        db.execute('drop table if exists car_entry')
        
        #creating new tables
        db.execute("create table bike(spot integer(10) primary key, status integer(1))")
        db.execute("create table car(spot integer(10) primary key, status integer(1))")
        db.execute('create table bike_entry(uid varchar(30) primary key,spot integer(1))')
        db.execute('create table car_entry(uid varchar(30) primary key,spot integer(1))')
        
        #taking number of spots from the user
        car=int(input("Enter the Number of Car Parking Spots: "))
        bike=int(input("Enter the Number of Bike Parking Spots: "))
        
        #creting rows in the tables of parking spots
        i=1
        while(i<=car or i<=bike):
            if(i<=car):
                db.execute(f'Insert into car values ({i}, 0)')
            if(i<=bike):
                db.execute(f'Insert into bike values ({i}, 0)')
            i+=1
        conn.commit()


#sending mail
def email_sender(to,name,text,flag):
    
     
    #Admin Credentials
    frm='kgagansingh@gmail.com'
    pas=''
    
    
    #filling up msg parts
    msg=MIMEMultipart()
    msg['from']=frm
    msg['to']=to
    msg['subject']=f'JCBOSEUST Parking System Alerts ({flag})'
    body=text
    msg.attach(MIMEText(body,'plain'))
    
    #converting msg to string
    msg.as_string()
    
    
    if(test_connection()):
        #engaging servers
        server=smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(frm,pas)
        
        #sending message
        server.send_message(msg)
        server.quit()
        
    else:
    
        print("\nInternet Connectivity Lost, Automated E-mail Would not be Sent")
        speak("Internet Connectivity Lost, Automated E-mail Would not be Sent")


#sending text message
def send_message(f_name,l_name,typ,spot,flag):
    
    #Getting time stamp
    time=datetime.now()
    date=time.strftime("%d/%m/%Y")
    time=time.strftime("%H:%M:%S")
    
    text=""
    name=f_name+' '+l_name
    
    #Entry Text
    if(flag=='Entry'):
        
        #Creating text message
        line_1=f'Welcome {name} to the Parking of JCBOSEUST for Your {typ.title()}\'s Parking, \n'
        line_2=f'Parking Time: {time}, \n'
        line_3=f'Parking Date: {date}, \n'
        line_4='Today\'s Parking Spot is: ' + str(spot)
        text=line_1+line_2+line_3+line_4
        
    #Exit Text
    else:
        
        line_1=f'Thankyou {name} for using Parking of JCBOSEUST for Your {typ.title()}\'s Parking, \n'
        line_2=f'Exit Time: {time}, \n'
        line_3=f'Exit Date: {date}, \n'
        text=line_1+line_2+line_3
    
    
    #Sending Text message
    if(test_connection()):
        client=Client(ac,tok)
        client.messages.create(body=text,from_='+19513388449',to=num)
        email_sender(e_id,name,text,flag)
    else:
        
        print("\nInternet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
        speak("Internet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")


#scanning qr
def scan(idx):
    
    res=""
    cap=cv2.VideoCapture(idx,cv2.CAP_DSHOW)
    
    print("System is Ready,Please Scan your QR now\n")
    speak("System is Ready,Please Scan your QR now")
    
    while True:
        _,frame=cap.read()
        
        # if flag==True:
        #     frame = cv2.flip(frame, 1)     #flipping for mirroring
        
        decoded=decode(frame)
        
        for obj in decoded:
            res+=obj.data.decode('utf-8')
       
        if(res!=''):
            break
        
        cv2.imshow('QRScanner',frame)
        if cv2.waitKey(1)== 27:         #esc to quit camera
            break;
    
    cap.release()
    cv2.destroyAllWindows()
    return res



#finding nearest availabke space    
def find_avail(typ):
    q=f'''select * from {typ} where status=0 LIMIT 1'''
    db.execute(q)
    res=db.fetchall()
    if(len(res)==0):
        return -1
    return res[0][0]


#adding or deleting user from the database
def check(uid,typ):
    if(typ=='car'):
        q=f'''select * from car_entry where uid='{uid}' LIMIT 1'''
        db.execute(q)
        res=db.fetchall()
        if(len(res)==1):
            q=f'''delete from car_entry where uid='{uid}' '''
            db.execute(q)
            q=f'update car Set status=0 where spot={res[0][1]}'
            db.execute(q)
            conn.commit()
            return 0
        else:
            spot=find_avail('car')
            if(spot==-1):
                return -1
            tup=(uid,spot)
            q=f'insert into car_entry (uid,spot) values {tup}'
            db.execute(q)
            q=f'update Car Set status=1 where spot={spot}'
            db.execute(q)
            conn.commit()
            return spot
        
    
    if(typ=='bike'):
        q=f'''select * from bike_entry where uid='{uid}' LIMIT 1'''
        db.execute(q)
        res=db.fetchall()
        if(len(res)>=1):
            q=f'''delete from bike_entry where uid='{uid}' '''
            db.execute(q)
            q=f'update Bike Set status=0 where spot={res[0][1]}'
            db.execute(q)
            conn.commit()
            return 0
        else:
            spot=find_avail('bike')
            if(spot==-1):
                return -1
            tup=(uid,spot)
            q=f'insert into bike_entry (uid,spot) values {tup}'
            db.execute(q)
            q=f'update Bike Set status=1 where spot={spot}'
            db.execute(q)
            conn.commit()
            return spot


#selecting camera using function
idx=select_cam()


while True:
    
    if(idx==-1):    #checking if an operational camera is accepted by the user
        print("\nSorry, This Apllication Requires an Operational Camera")
        speak("Sorry, This Apllication Requires an Operational Camera")
        break
    
    res=""
    res=scan(idx)
    if(res==''):
         print("Scanning Interrupted by User\n")
         speak("Scanning Interrupted by user")
         
         chck=input("Do you want to Exit the Application?\ny/n?: ")
         chck=chck.lower()
         if(chck=='y'):
             break;
         else:
             continue
    
    
    
    print("Scanning Completed\n")
    speak("Scanning Completed")
    
    #decryption of data
    res=decrypt(res)
    
    #Slitting Values into list
    details=list(res.split())
        #UID,f_name,l_name,num,e_id,dl,typ=res.split()
    
    
    #Authorisation
    t=len(details)
    if(t!=8 or str(details[7])!='YMCA'):
        
        print("Authorisation Failed, Please try Again")
        speak("Authorisation Failed, Please try Again")
        cv2.waitKey(1000)
        continue
        
    UID=details[0]
    f_name=details[1]
    l_name=details[2]
    num=details[3]
    e_id=details[4]
    dl=details[5]
    typ=details[6]
    name=f_name+" "+l_name
    
    spot=0
    if(typ=='bike'): 
        spot=check(UID,typ)
        if spot == 0:                                 #already parked vehicle
                                   
            
                        
            if(test_connection()):
                
                print(f"Thankyou {name} for using parking")
                speak(f"Thankyou {name} for using parking")
                
                print("\nPlease Wait for Next Scanning")
                speak("Please Wait for Next Scanning")
                
                send_message(f_name, l_name, typ, spot, 'Exit')
                
            else:
                
                print("\nInternet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                speak("Internet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                
                print(f"Thankyou {name} for using parking")
                speak(f"Thankyou {name} for using parking")
            
            continue
        else:                                          #new vehicle
            if(spot==-1):
                
                print("Parking is full\n")
                speak("Parking is full")
                
                continue
            
            
            
            if(test_connection()):
                
                print(f"Welcome {name}, Your bike\'s spot is {spot}")
                speak(f"Welcome {name}, Your bike\'s spot is {spot}")
                
                print("\nPlease Wait for Next Scanning")
                speak("Please Wait for Next Scanning")
                
                send_message(f_name, l_name, typ, spot, 'Entry')
            else:
                
                print("\nInternet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                speak("Internet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                
                print(f"Your bike\'s spot is {spot}")
                speak(f"Your bike\'s spot is {spot}")
    
    else:
        spot=check(UID,typ)
        if spot == 0:                                     #For already parked vehicle
            
            
            
            if(test_connection()):
                
                print(f"Thankyou {name} for using parking")
                speak(f"Thankyou {name} for using parking")
                
                print("\nPlease Wait for Next Scanning")
                speak("Please Wait for Next Scanning")
                
                send_message(f_name, l_name, typ, spot, 'Exit')
            else:
                
                print("\nInternet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                speak("Internet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                print(f"Thankyou {name} for using parking")
                speak(f"Thankyou {name} for using parking")
    
            continue
        
        else:                                             #New vehicles
            if(spot==-1):
                
                print("Parking is full\n")
                speak("Parking is full")
                
                continue
            
            
            
            if(test_connection()):
                print(f"Welcome {name}, Your Car\'s spot is {spot}")
                speak(f"Welcome {name}, Your Car\'s spot is {spot}")
                
                print("\nPlease Wait for Next Scanning")
                speak("Please Wait for Next Scanning")    
                
                send_message(f_name, l_name, typ, spot, 'Entry')
            else:
                
                print("\nInternet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                speak("Internet Connectivity Lost, Automated E-mail and Text Message Would not be Sent")
                
                print(f"Your Car\'s spot is {spot}")
                speak(f"Your Car\'s spot is {spot}")
            
print("Thank you For using J C Bose University's Parking Application, Have a Good Day")
speak("Thank you For using J C Bose University's Parking Application, Have a Good Day")
