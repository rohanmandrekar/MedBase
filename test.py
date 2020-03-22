import datetime
import pyrebase
import operator
from flask import Flask,request,render_template,redirect,url_for,make_response
from babel.numbers import format_currency

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyAbMrgO71YE2YsMR3qohWtVhntj5yK7DCo",
    "authDomain": "thehealingpath-a0f2f.firebaseapp.com",
    "databaseURL": "https://thehealingpath-a0f2f.firebaseio.com",
    "projectId": "thehealingpath-a0f2f",
    "storageBucket": "thehealingpath-a0f2f.appspot.com",
    "messagingSenderId": "913375614722",
    "serviceAccount": "ServiceAccountKey.json"
  }

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
logflag=0
signupflag=0
data=[]

def getdata():
  global data
  data=[]
  
  if not data:
    patients =db.child(request.cookies.get('uidd')).get().val()     
    #print('patients:',patients)
    for year in patients:
      #print('Year:',year)
      for month in patients[str(year)]:
        #print('Month',month)
        if year.isdigit():
          for day in patients[str(year)][str(month)]:
            for key in patients[str(year)][str(month)][str(day)]:
              d1={}
              d1['Name']=patients[str(year)][str(month)][str(day)][str(key)]['Name']
              d1['Amt']=patients[str(year)][str(month)][str(day)][str(key)]['Amt']
              d1['isPaid']=patients[str(year)][str(month)][str(day)][str(key)]['isPaid']
              d1['Med']=patients[str(year)][str(month)][str(day)][str(key)]['Med']
              d1['Pending']=patients[str(year)][str(month)][str(day)][str(key)]['Pending']
              d1['isPaid']=patients[str(year)][str(month)][str(day)][str(key)]['isPaid']
              d1['Pay']=patients[str(year)][str(month)][str(day)][str(key)]['Pay']
              d1['key']=key
              d1['day']=day[1:]
              d1['month']=month[1:]
              d1['year']=year
              date=str(day[1:]+'/'+str(month[1:])+'/'+str(year))
              x=datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%d/%m/%Y")
              d1['Date']=x
              if(d1['Pending']!="0"):
                d1['isPaid']='3'
              data.append(d1)

@app.route("/profile",methods=["GET","POST"])
def profile():
  return render_template('profile.html')
  
@app.route("/resetpass",methods=["GET", "POST"])
def reset():
  email=request.form['email']
  auth.send_password_reset_email(email)
  return render_template('login.html')

@app.route("/forgot",methods=["GET", "POST"])
def forgot():
  return render_template('forgotlogin.html')

@app.route("/homedefault",methods=["GET", "POST"])
def hello():
    global logflag
    global data
    data=[]
    logflag=0
    
    email=request.form['email']
    password=request.form['pswd']
    try:
      user = auth.sign_in_with_email_and_password(email, password)
      uid = user['localId']
      uname=db.child(uid).child('Username').get().val()
      resp=make_response(render_template('home.html', username=uname, uid=uid))
      resp.set_cookie('uidd',uid)
      resp.set_cookie('unamee',uname)
      return resp

    except:
      logflag=0
      return render_template('login.html',logflag=logflag)
     
      
@app.route("/showdata",methods=["GET", "POST"])
def ok():
  global data

  filterdata=[]
  getdata()
  name=request.form['name']
  med=request.form['med']
  ptype=request.form['ptype']
  d=request.form['day']
  m=request.form['month']
  y=request.form['year']
  isPaid=''
  amteq=request.form['amteq']
  if amteq is not '':
    amteq=int(amteq)
  amtm=request.form['amtm']
  if amtm is not '':
    amtm=int(amtm)
  amtl=request.form['amtl']
  if amtl is not '':
    amtl=int(amtl)
  try:
    isPaid=request.form['radio']
  except:
    print()

  if name is '' and med is '' and ptype is '0' and d is '0' and m is '0' and y is '0' and isPaid is '' and amteq is '' and amtm is '' and amtl is '':
    return render_template('dashboard.html',tdata=data,username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))   

  else:
    for i in data:
      tempname=name
      tempmed=med
      tempptype=ptype
      tempd=d
      tempm=m
      tempy=y
      tempisPaid=isPaid
      if isPaid=="Not Paid":
        tempisPaid='0'
      elif isPaid=="Paid":
        tempisPaid='1'
      elif isPaid=="Partially Paid":
        tempisPaid='3'
      tempamteq=amteq
      tempamtm=amtm
      tempamtl=amtl

      if name is '':
        tempname=i.get('Name')
      if med is '':
        tempmed=i.get('Med')
      if ptype is '0':
        tempptype=i.get('Pay')
      if d is '0':
        tempd=i.get('day')
      if m is '0':
        tempm=i.get('month')
      if y is '0':
        tempy=i.get('year')
      if isPaid is '':
        tempisPaid=i.get('isPaid')
      if amteq is '':
        tempamteq=i.get('Amt')
      if amtl is '':
        tempamtl=i.get('Amt')
      if amtm is '':
        tempamtm=i.get('Amt')

      if i.get('Name')==tempname and i.get('Med')==tempmed and i.get('Pay')==tempptype and i.get('day')==tempd and i.get('month')==tempm and i.get('year')==tempy and str(i.get('isPaid'))==tempisPaid and i.get('Amt')<=tempamtl and i.get('Amt')>=tempamtm and i.get('Amt')==tempamteq:
        filterdata.append(i)           
    return render_template('dashboard.html',tdata=filterdata,username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))

@app.route("/stats", methods=["GET","POST"])
def chart():
   global data

   getdata()
   dic={}
   ptdic={}
   max_pay=''
   max_visit=''
   uniquename=[]
   unique_pat=0
   amount=0
   amount2019=0
   amount2018=0
   perc=0
   unpaid=0
   partial=0
   visits={}
   mvp={}
   if data:
    for i in data:
      # MVP
      if i['Name'] in mvp:
        mvp[i['Name']]+=i['Amt']
      else:
        mvp[i['Name']]=i['Amt']
      max_pay=max(mvp.items(), key=operator.itemgetter(1))[0]
      # END
      #Most Visits
      if i['Name'] in visits:
        visits[i['Name']]+=1
      else:
        visits[i['Name']]=1
      max_visit=max(visits.items(), key=operator.itemgetter(1))[0]
      #End
      # UNPAD/PARTIALLY PAID CARD
      if i['isPaid']=='0':
        unpaid=unpaid+1
      if i['isPaid']=='3':
        partial=partial+1  
        # END
      # AMOUNT EARNED IN 2019
      amount=amount+int(i['Amt'])  
      if(i['year']=='2019'):
        amount2019=amount2019+int(i['Amt'])
      else:
        amount2018=amount2018+int(i['Amt'])
      if amount2018!=0 and amount2019!=0:
        perc=round(((amount2019-amount2018)/(amount2018))*100,2)
      else:
        perc=0
      # END
      # MEDICINE PIE
      if i['Med'] in dic:
        dic[i['Med']]+=1
      else:
        dic[i['Med']]=1 
      # END
    # PAYMENT TYPE
      if i['Pay'] != "Not Paid":
        if i['Pay'] in ptdic:
          ptdic[i['Pay']]+=1
        else:
          if (i['Pay']!="None"):
            ptdic[i['Pay']]=1   
      # END   
      #NO OF PATIENTS
      if (i['Name'] not in uniquename):
        uniquename.append(i['Name'])
        unique_pat+=1  
        #END 
    
   formattedamount=format_currency(amount, 'INR', locale='en_IN')   
   return render_template('stats.html',max_pay=max_pay,max_visit=max_visit ,dic=dic,ptdic=ptdic,username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'),num_of_pat=len(data),amount=formattedamount,perc=perc,unique_pat=unique_pat,unpaid=unpaid,partial=partial)

@app.route("/about",methods=["GET", "POST"])
def aboutus():
  data=[]
  return render_template('about.html',username=request.cookies.get('unamee'), uid=request.cookies.get('uidd'))

@app.route("/signout",methods=["GET", "POST"])
def signoutuser():
  data=[]

  return render_template('login.html')

@app.route("/dashboard")
def sh():
  global data
  getdata()
  return render_template('dashboard.html',tdata=data,username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))

@app.route("/home")
def home1():
  global data
  return render_template('home.html',username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))

@app.route("/addnew",methods=["GET", "POST"])
def addnewpat():
  return render_template('addpatient.html',username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))

@app.route("/addnewmethod",methods=["GET", "POST"])
def addnewmet():
  global data

  mref = firebase.database()
  dict1={}
  pend=0
  name=request.form['name']
  med=request.form['med']
  amt=request.form['amt']
  d=request.form['day']
  m=request.form['month']
  y=request.form['year']
  date=str(d+'/'+str(m)+'/'+str(y))
  x=datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%d/%m/%Y")
  try:
    ptype=request.form['radio']
  except:
    print()
  
  if ptype=='None':
    isPaid='0'
  else:
    pend=request.form['pendamt']
    if not pend:
      pend=0
    isPaid='1'

  dict1['Name']=name
  dict1['Med']=med
  dict1['Amt']=int(amt)
  dict1['Pay']=ptype
  dict1['isPaid']=isPaid
  dict1['Pending']=str(pend)

  key=mref.child(request.cookies.get('uidd')).child(y).child('m'+m).child('d'+d).push(dict1)

  if pend is not 0:
    isPaid='3'

  dict1['key']=key['name']
  dict1['day']=str(d)
  dict1['isPaid']=isPaid
  dict1['month']=str(m)
  dict1['year']=str(y)
  dict1['Date']=x
  data.append(dict1)
  return redirect("dashboard") 
  
@app.route("/signupuser")
def newuser():
  return render_template('signup.html')

@app.route("/newuser",methods=["GET", "POST"])
def newdoc():
    signupflag=0
    email=request.form['email']
    password=request.form['cpswd']
    username=request.form['name']
    try:
      user=auth.create_user_with_email_and_password(email, password)
      uid = user['localId']
      mref = firebase.database()
      mref.child(uid).child('Username').set(username)

      return redirect("")
    except:
      signupflag=0
      return render_template('signup.html',signupflag=signupflag)

    
@app.route("/")
def ini():
    return render_template('login.html')



@app.route("/delpat",methods=["GET", "POST"])
def deletepatient():
  global username
  global data

  data1=[]
  mref = firebase.database()
  k=request.get_json()

  key=k['data'][6]
  y=k['data'][8]
  m=k['data'][9]
  d=k['data'][10]
  mref.child(request.cookies.get('uidd')).child(y).child('m'+m).child('d'+d).child(key).remove()

  for i in data:
    if i['key']!=key:
      data1.append(i)

  data=data1
  return render_template('dashboard.html',tdata=data,username=request.cookies.get('unamee'),uid=request.cookies.get('uidd'))

@app.route("/editpat",methods=["GET", "POST"])
def editpatient():
  global username
  global data

  mref = firebase.database()
  dict1={}

  k=request.get_json()

  name=k['arr'][0]
  med=k['arr'][1]
  amt=int(k['arr'][2])
  pend=str(k['arr'][3])
  pay=k['arr'][4]
  isPaid=str(k['arr'][5])
  key=k['arr'][6]
  y=k['arr'][7]
  m=k['arr'][8]
  d=k['arr'][9]

  dict1['Name']=name
  dict1['Med']=med
  dict1['Amt']=amt
  dict1['Pending']=pend
  dict1['Pay']=pay
  dict1['isPaid']=isPaid
  
  mref.child(request.cookies.get('uidd')).child(y).child('m'+m).child('d'+d).child(key).update(dict1)

  if pend is not '0':
    isPaid='3'

  dict1['key']=key
  dict1['day']=str(d)
  dict1['isPaid']=isPaid
  dict1['month']=str(m)
  dict1['year']=str(y)
  date=str(d+'/'+str(m)+'/'+str(y))
  x=datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%d/%m/%Y")
  dict1['Date']=x

  for i in data:
    if i['key']==key:
      i['Name']=name
      i['Amt']=amt
      i['Med']=med
      i['Pending']=pend
      i['isPaid']=isPaid
      i['Pay']=pay
  return redirect("dashboard") 
    
if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=9000, debug=True)

#[{'Amt': 500, 'Med': 'Alium', 'Name': 'Raj', 'Pay': 'Card', 'Pending': '0', 'isPaid': '1', 'key': '-L_pkq7Mr9ByQWpGXdV8', 'year': '2018', 'month': '1', 'day': '3', 'Date': '03/01/2018'}, 