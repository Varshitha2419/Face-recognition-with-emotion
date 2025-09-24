import io
from base64 import b64decode
from flask import Flask, request, redirect, url_for, render_template, session
import firebase_admin
import random
from firebase_admin import credentials, firestore
from flask import Flask, request, redirect, url_for, render_template, session
import firebase_admin
import random
from firebase_admin import credentials, firestore
import numpy as np
import cv2
from PIL import Image
from datetime import datetime
from tkinter import messagebox
import cv2
import os
from csv import reader
import cv2
from deepface import DeepFace

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)
app.secret_key = "OnlineAgriCropBidding@123"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Start capturing video
cap = cv2.VideoCapture(0)

@app.route('/usercheckemotions1', methods=['POST','GET'])
def usercheckemotions1():    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Convert grayscale frame to RGB format
            rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                # Extract the face ROI (Region of Interest)
                face_roi = rgb_frame[y:y + h, x:x + w]
        
                # Perform emotion analysis on the face ROI
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

                # Determine the dominant emotion
                emotion = result[0]['dominant_emotion']

                # Draw rectangle around face and label with predicted emotion
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                # Display the resulting frame
                cv2.imshow('Real-time Emotion Detection', frame)

                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release the capture and close all windows
            cap.release()
            cv2.destroyAllWindows()
        return render_template("usercheckemotions.html")
    except Exception as e:
        return str(e)
    
@app.route('/usercheckemotions')
def usercheckemotions():
    try:
        return render_template("usercheckemotions.html")
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/usermainpage')
def usermainpage():
    try:
        return render_template("usermainpage.html")
    except Exception as e:
        return str(e)

@app.route('/staffforgotpassword')
def staffforgotpassword():
    try:
        return render_template("staffforgotpassword.html")
    except Exception as e:
        return str(e)

@app.route('/staffenterotppage')
def staffenterotppage():
    try:
        return render_template("staffenterotppage.html")
    except Exception as e:
        return str(e)

@app.route('/staffchecking', methods=['POST'])
def staffchecking():
    try:
        if request.method == 'POST':
            uname = request.form['uname']
            email = request.form['email']
        print("Uname : ", uname, " Email : ", email);
        db = firestore.client()
        dbref = db.collection('newstaff')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            if uname == temp['UserName'] and email == temp['EmailId']:
                session['username'] = uname
                session['emailid'] = email
                session['userid'] = temp['id']
                flag = True
                break
        if (flag):
            otp = random.randint(1000, 9999)
            print("OTP : ", otp)
            session['toemail'] = email
            session['uname'] = uname
            session['otp'] = otp
            print("User Id : ", session['userid'])
            return render_template("staffgenerateotp.html", uname=uname, toemail=email, otp=otp,
                                                        redirecturl= 'http://127.0.0.1:5000/staffenterotppage')
        else:
            return render_template("staffforgotpassword.html", msg="UserName/EmailId is Invalid")
    except Exception as e:
        return str(e)

@app.route('/staffcheckotppage', methods=['POST'])
def staffcheckotppage():
    if request.method == 'POST':
        storedotp=session['otp']
        enteredotp = request.form['otp']
        print("Entered OTP : ", enteredotp, " Stored OTP : ", storedotp)
        if(int(storedotp)==int(enteredotp)):
            return render_template("staffpasswordchangepage.html", msg="You can update your password")
        else:
            return render_template("staffenterotppage.html", msg="Incorrect OTP")
    return render_template("staffenterotppage.html", msg="Incorrect OTP")

@app.route('/staffpasswordchangepage', methods=['POST'])
def staffpasswordchangepage():
    print("Password Change Page")
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']

        db = firestore.client()
        newstaff_ref = db.collection('newstaff')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        id=""
        for doc in data:
            print("Document : ", doc)
            if(doc['UserName']==uname):
                id=doc['id']
        db = firestore.client()
        data_ref = db.collection(u'newstaff').document(id)
        data_ref.update({u'Password': pwd})
        print("Password Updated Success")
        return render_template("stafflogin.html", msg="Password Updated Success")
    return render_template("stafflogin.html", msg="Password Not Updated")

@app.route('/index')
def indexpage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/logout')
def logoutpage():
    try:
        session['id']=None
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/about')
def aboutpage():
    try:
        return render_template("about.html")
    except Exception as e:
        return str(e)

@app.route('/services')
def servicespage():
    try:
        return render_template("services.html")
    except Exception as e:
        return str(e)

@app.route('/gallery')
def gallerypage():
    try:
        return render_template("gallery.html")
    except Exception as e:
        return str(e)

@app.route('/adminlogin', methods=['GET','POST'])
def adminloginpage():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname'].lower()
        pwd = request.form['pwd'].lower()
        print("Uname : ", uname, " Pwd : ", pwd)
        if uname == "admin" and pwd == "admin":
            return render_template("adminmainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("adminlogin.html", msg=msg)

@app.route('/userlogin', methods=['GET','POST'])
def userlogin():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']

        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            if uname == temp['UserName'] and pwd == temp['Password']:
                session['userid'] = temp['id']
                flag = True
                break
        if (flag):
            return render_template("usermainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("userlogin.html", msg=msg)

@app.route('/stafflogin', methods=['GET','POST'])
def staffloginpage():
    msg=""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        dbref = db.collection('newstaff')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        flag = False
        for temp in data:
            if uname == temp['UserName'] and pwd == temp['Password']:
                session['userid'] = temp['id']
                flag = True
                break
        if (flag):
            return render_template("staffmainpage.html")
        else:
            msg = "UserName/Password is Invalid"
    return render_template("stafflogin.html", msg=msg)

@app.route('/staffviewprofile')
def staffviewprofile():
    try:
        id = session['userid']
        db = firestore.client()
        dbref = db.collection('newstaff')
        userdata = dbref.get()
        data={}
        for doc in userdata:
            temp = doc.to_dict()
            if(id==temp['id']):
                data = {'id':temp['id'],
                    'FirstName':temp['FirstName'],
                    'LastName':temp['LastName'],
                    'EmailId':temp['EmailId'],
                    'UserName': temp['UserName'],
                    'PhoneNumber':temp['PhoneNumber']}
                break
        print("User Data ", data)
        return render_template("staffviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewprofile')
def userviewprofile():
    try:
        id=session['userid']
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data={}
        for doc in userdata:
            temp = doc.to_dict()
            if(id==temp['id']):
                data = {'id':temp['id'],
                    'FirstName':temp['FirstName'],
                    'LastName':temp['LastName'],
                    'EmailId':temp['EmailId'],
                    'PhoneNumber':temp['PhoneNumber'],
                    'UserName':temp['UserName']}
                break
        print("User Data ", data)
        return render_template("userviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/newuser', methods=['POST','GET'])
def newuser():
    try:
        msg=""
        print("Add New User page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                        'FirstName': fname, 'LastName': lname,
                        'UserName': uname, 'Password': pwd,
                        'EmailId': email, 'PhoneNumber': phnum,
                        'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newuser')
            newuser_ref.document(id).set(json)
            print("User Inserted Success")
            msg = "New User Added Success"
        return render_template("newuser.html", msg=msg)
    except Exception as e:
        return str(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/adminaddstaff', methods=['POST','GET'])
def adminaddstaff():
    try:
        print("Add New Staff page")
        msg=""
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname,'LastName':lname,
                    'UserName': uname,'Password':pwd,
                    'EmailId': email,'PhoneNumber':phnum,
                    'Address': address}
            db = firestore.client()
            newdb_ref = db.collection('newstaff')
            id = json['id']
            newdb_ref.document(id).set(json)
            msg="New Staff Added Success"
        return render_template("adminaddstaff.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/contact', methods=['POST','GET'])
def contactpage():
    try:
        msg=""
        if request.method == 'POST':
            cname = str(request.form['fname']) + " " + str(request.form['lname'])
            subject = request.form['subject']
            message = request.form['message']
            email = request.form['email']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'ContactName': cname, 'Subject': subject,
                    'Message': message,
                    'EmailId': email}
            db = firestore.client()
            newdb_ref = db.collection('newcontact')
            id = json['id']
            newdb_ref.document(id).set(json)
            msg = "New Contact Added Success"
        return render_template("contact.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/adminviewusers')
def adminviewusers():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newuser')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Users Data " , data)
        return render_template("adminviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewemotions')
def userviewemotions():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newemotions')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Data " , data)
        return render_template("userviewemotions.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/staffviewemotions')
def staffviewemotions():
    try:
        db = firestore.client()
        data_ref = db.collection('newemotions')
        newdata = data_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Data " , data)
        return render_template("staffviewemotions.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewemotions')
def adminviewemotions():
    try:
        db = firestore.client()
        data_ref = db.collection('newemotions')
        newdata = data_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Data " , data)
        return render_template("adminviewemotions.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/staffviewusers')
def staffviewusers():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newuser')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Users Data " , data)
        return render_template("staffviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewstaffs')
def adminviewstaffs():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newstaff')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Users Data " , data)
        return render_template("adminviewstaffs.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewcontacts')
def adminviewcontacts():
    try:
        db = firestore.client()
        newdata_ref = db.collection('newcontact')
        newdata = newdata_ref.get()
        data=[]
        for doc in newdata:
            data.append(doc.to_dict())
        print("Contact Data " , data)
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminmainpage')
def adminmainpage():
    try:
        return render_template("adminmainpage.html")
    except Exception as e:
        return str(e)

@app.route('/staffmainpage')
def staffmainpage():
    try:
        return render_template("staffmainpage.html")
    except Exception as e:
        return str(e)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.debug = True
    app.run()