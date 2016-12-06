import webapp2
import smtplib
import random
import os
import urllib
import jinja2

from db_entities import *
from basehandler import BaseHandler
from basehandler import *
from login import *
from smtplib import SMTPException
from google.appengine.ext import ndb
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class RegistrationMainHandler(BaseHandler):
	def get(self): 
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/MainPage_AccountAdministration.html')
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		_class = user.classlist
		password = user.password
		email = user.email
		template_values = {
			'accounttype': accounttype,
			'account': accountname,
			'class': _class,
			'password': password,
			'email': email
			}
		self.response.write(template.render(template_values))


class AddInstructorHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewInstructor.html')
		template_values = { 'outcome': 'undecided' }
		self.response.write(template.render(template_values))
	def post(self):
		firstNameFromForm = self.request.get('firstname')
		lastNameFromForm = self.request.get('lastname')
		emailAddressFromForm = self.request.get('emailaddress')
		userName = emailAddressFromForm
		outcome = ''

		user = User.query(User.username == userName, User.accounttype == "instructor").fetch()
		#self.response.out.write(user);
		
		if len(user) != 0:
			template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewInstructor.html')
			template_values = { 'outcome': 'duplicate', 'email': userName }
			self.response.write(template.render(template_values))
			
		elif userName == '' or firstNameFromForm == '' or lastNameFromForm == '':
			if userName == '': 
				outcome = "blankEmailAddress"
			elif firstNameFromForm == '': 
				outcome = "blankFirstName"
			else:
				outcome = "blankLastName"

			template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewInstructor.html')
			template_values = { 'outcome': outcome }
			self.response.write(template.render(template_values))
			
		else:
			passWord = str(random.randrange(100000,1000000))
			template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewInstructor.html')
			template_values = { 'outcome': 'unique', 'password': passWord, 'email': userName }
			self.response.write(template.render(template_values))
			newUser = User(username=userName,password=passWord,
				lastname=lastNameFromForm,firstname=firstNameFromForm,
				email=emailAddressFromForm,accounttype="instructor",)
			newUser.put()
			
			
		
		#self.redirect('/registrationhomepage')
class AddStudentHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewStudents.html')

		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		instructors = User.query(User.accounttype == 'instructor').fetch()

		template_values = { 'status' :'initial', 'usertype' : accounttype, 'instructors': instructors}
		
		
		self.response.write(template.render(template_values))
	def post(self):
		currentClass = self.request.get('class')
		textFromForm = self.request.get('textArea').strip() + '*'
		addressList = []

		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype

		instructorAssigned = ""
		if(accounttype == 'admin'): self.request.get('instructorAssigned')

		#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewStudents.html')
		#self.response.out.write(" class = " + currentClass + ", addresses = " + text)
		#self.response.write(template.render())
		
		# Parse each email address
		newAddress =''
		BlankAddy = False
		for ch in textFromForm:
			if ch != ',' and ch !='*':
				newAddress += ch
			elif len(newAddress) > 0:
					addressList.append(newAddress)
					newAddress=''
			else:
				BlankAddy = True
		if len(addressList) == 0: 
			BlankAddy = True
		if not BlankAddy and len(currentClass) != 0:
			# Add the addresses to the datastore
			passwordLog = []
			for address in addressList:
				passWord = str(random.randrange(100000,1000000))
				passwordLog.append([address, passWord])
				newUser = User(
					username=address,
					password=passWord,
					lastname='temp',
					firstname='temp',
					email=address,
					accounttype='student'
					)
				instructor = ''
				if accounttype == 'admin': instructor = self.request.get("instructorAssigned")
				else: instructor = user

				newUser.classlist.append(Class(classname=currentClass, instructor=instructor))
				newUser.put()
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/DisplayNewStudents.html')
		template_values = { "log": passwordLog, "class": currentClass }
		self.response.write(template.render(template_values))

class EditPersonalDataHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditPersonalInformation.html')
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		_class = user.classlist
		password = user.password
		email = user.email
		firstname = user.firstname
		lastname = user.lastname
		template_values = {
			'accounttype': accounttype,
			'firstname' : firstname,
			'lastname' : lastname,
			'accountname': accountname,
			'class': _class,
			'password': password,
			'email': email
			}
		self.response.write(template.render(template_values))
	def post(self):
		fname = self.request.get('firstName')
		lname = self.request.get('lastName')
		pword = self.request.get('passWord')

		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		user.firstname = fname
		user.lastname = lname
		user.password = pword
		user.put()
		#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditPersonalInformation.html')
		#self.response.write("fname = " + fname + ", lname = " + lname + ", pword = " + pword)
		#self.response.write(template.render())
		# Should also notify the instructor as to the student's changes.
		self.redirect('/registrationhomepage')

'''
class EditStudentHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditPersonalInformation.html')
		accountname = self.session.get('account')
		accounttype = user.accounttype
		classes = ''
		if accounttype == 'instructor':
			classes = Class.query(Class.instructor == accountname).fetch()
		else:
			classes = Class.query(Class.classname != '').fetch()
		students = User.query(User.accounttype == 'student').fetch()
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		_class = user.classlist
		password = user.password
		email = user.email
		firstname = user.firstname
		lastname = user.lastname
		template_values = {
			'accounttype': accounttype,
			'classes': classes,
			'SELECTION': False,
			'students' : students
			'firstname' : firstname,
			'lastname' : lastname,
			'accountname': accountname,
			'class': _class,
			'password': password,
			'email': email
			}
		self.response.write(template.render(template_values))
	def post(self):
		studentSelected = self.request.get("studentSelected")
		accountname = User.query(User.username == studentSelected).fetch[0]

		SELECTION = True

		fname = self.request.get('firstName')
		lname = self.request.get('lastName')
		pword = self.request.get('passWord')

		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		user.firstname = fname
		user.lastname = lname
		user.password = pword
		user.put()
		#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditPersonalInformation.html')
		#self.response.write("fname = " + fname + ", lname = " + lname + ", pword = " + pword)
		#self.response.write(template.render())
		# Should also notify the instructor as to the student's changes.
		self.redirect('/registrationhomepage')
'''





'''class EditStudentHandler(BaseHandler):

		def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewStudents.html')
		if accountname != '':
			#user is logged in as accountname
			user = User.query(User.username == accountname).fetch()[0]
		template_values = { 'status' :'initial' }
		self.response.write(template.render(template_values))
'''		



"""
		body = "Congratulations, " + firstNameFromForm + " " + lastNameFromForm + ",\n"
		body += "You have been given an Instructor Account on the University of Wisconsin Course FAQ System.\n"
		body += "Your username is " + userName + " and your temporary password is " + passWord + ".\n"
		
		sender = 'ronald.zalewski@gmail.com'
		receivers = [emailAddressFromForm]

		message = firstNameFromForm + " " + lastNameFromForm + " ,\n"
		message += "You have been assigned an Instructor Account on the\n"
		message += "Course FAQ System at the University of Wisconsin - Milwaukee.\n\n"
		message += "Please visit www.faq.com and use the following to register:\n"
		message += "Account name: " + userName + "\n"
		message += "Temporary password: " + passWord

		try:
   			smtpObj = smtplib.SMTP('localhost')
   			smtpObj.sendmail(sender, receivers, message)         
   			print "Successfully sent email"
		except SMTPException:
   			print "Error: unable to send email"
"""


'''
	def getUserName(fname, lname):
		lenFname = len(fname)
		lenLname = len(lname)
		if(lenFname >= 3):
			newUserName=fname[0:2]
		elif(lenFname == 2):
			newUserName=fname[0:1] + "X"
		if(lenLname >= 3):
			newUserName += lname[0:2]
		elif(lenLname == 2):
			newUserName += lname[0:1] + "X"
		users = User.all()
		noDup = True
		for user in users:
			if (user.username == newUserName):
				noDup = False
		if (noDup):
			return newUserName
'''

"""
class reg_AddOrModifyUsers(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/AddOrModifyUsers.html')
		self.response.write(template.render())

class reg_RegisterInstructorHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/RegisterInstructor.html')
		self.response.write(template.render())

class reg_AddOrEditStudentHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/AddorEditStudent.html')
		self.response.write(template.render())

class reg_AddInstructorHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/AddInstructor.html')
		self.template.write(template.render())
      
class reg_EditInstructorHandler(Basehandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/EditInstructor.html')
		self.template.write(template.render())

class reg_AddStudentHandler(Basehandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/AddStudent.html')
		self.template.write(template.render())

class reg_EditStudentHandler(Basehandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/EditStudent.html')
		self.template.write(template.render())


class reg_RegisterStudentHandler(Basehandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('html/reg_templates/RegisterStudent.html')
		self.template.write(template.render())
"""