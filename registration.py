import webapp2
import smtplib
import random
import os
import urllib
import jinja2
import re
import time

from db_entities import *
from basehandler import BaseHandler
from basehandler import DefaultDraw
from basehandler import *
from login import *
from smtplib import SMTPException
from google.appengine.ext import ndb
from webapp2_extras import sessions
from google.appengine.api.mail import EmailMessage
from google.appengine.api import app_identity
from google.appengine.ext import ndb

from strings import *


JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Register():
	@staticmethod
	def make_mail_message(sender,to,subject,body):
		EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
		email = None
		if EMAIL_REGEX.match(to):
			email = EmailMessage()
			email.sender = sender
			email.to = to
			email.subject = subject
			email.body = body
			email.check_initialized()
		return email
	
	
class RegistrationMainHandler(DefaultDraw):
	template_path_get ='./html/reg_templates/MainPage_AccountAdministration.html'
	def get(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):
			user = User.query(User.username == accountname).fetch()[0]
			template_values = {
				'user': user
			}
			self.draw(user, template_values)
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')

class AddInstructorHandler(DefaultDraw):
	template_path_get = './html/reg_templates/AddNewInstructor.html'
	template_path_post = './html/reg_templates/AddNewInstructor.html'
	def get(self):
		accountname = self.session.get('account');
		if self.validate_user(accountname, SADMIN):
			user = None
			if 'account' in self.session:
				user = User.query(User.username == self.session.get('account')).fetch()
				if len(user) == 1:
					user = user[0]
				else:
					user = None
			template_values = { 'outcome': 'undecided' }
			self.draw(user, template_values)
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
	def post(self):
		accountname = self.session.get('account');
		if self.validate_user(accountname, SADMIN):
			firstNameFromForm = self.request.get('firstname')
			lastNameFromForm = self.request.get('lastname')
			emailAddressFromForm = self.request.get('emailaddress')
			userName = emailAddressFromForm
			outcome = ''
			suser = None
			if 'account' in self.session:
				suser = User.query(User.username == self.session.get('account')).fetch()
				if len(suser) !=0:
					suser = suser[0]
				else:
					suser = None
			user = User.query(User.username == userName, User.accounttype == "instructor").fetch()
			if len(user) != 0:
				self.template_path_post = './html/reg_templates/AddNewInstructor.html'
				template_values = { 'outcome': 'duplicate', 'email': userName }
				self.draw(suser, template_values)
				
			elif userName == '' or firstNameFromForm == '' or lastNameFromForm == '':
				if userName == '': 
					outcome = "blankEmailAddress"
				if firstNameFromForm == '': 
					outcome = "blankFirstName"
				else:
					outcome = "blankLastName"

				self.template_path_post = './html/reg_templates/AddNewInstructor.html'
				template_values = { 'outcome': outcome }
				self.draw(suser, template_values)
				
			else:
				sender = 'Question App Support <admin@{}.appspotmail.com>'.format(app_identity.get_application_id())
				to = emailAddressFromForm
				subject = 'Activation Your Account'
				body = 'Please click the following link to create your account  http://{}.appspot.com/registerinstructor?username={}'.format(app_identity.get_application_id(),emailAddressFromForm.split('@')[0])
				email = Register().make_mail_message(sender,to,subject,body)
				if email != None:
					email.send()
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')	

class AddStudentHandler(DefaultDraw):
	template_path_get = './html/reg_templates/AddNewStudents.html'
	def get(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):
			user = User.query(User.username == accountname).fetch()[0]
			accounttype = user.accounttype
			instructors = User.query(User.accounttype == 'instructor').fetch()
			template_values = { 'status' :'initial', 'usertype' : accounttype, 'instructors': instructors}
			self.draw(user, template_values)
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
	def post(self):
		accountname = self.session.get('account')


		if self.validate_user(accountname, SADMIN):	
			classFromForm = None
			if len(Class.query(Class.classname == self.request.get('class')).fetch()) == 0:
				classFromForm = Class(classname=self.request.get('class'))
				classFromForm.put()
			else:
				classFromForm = Class.query(Class.classname == self.request.get('class')).fetch()[0]
			textFromForm = self.request.get('textArea').strip()
			user = User.query(User.username == accountname).fetch()[0]
			accounttype = user.accounttype
			instructorAssigned = self.request.get('instructorAssigned')
			instructor = User.query(User.username == instructorAssigned).fetch()[0]
			instructor.classlist.append(classFromForm)
			instructor.put()
			#split on commas
			emails = textFromForm.split(',')
			for address in emails:
				#check for valid email syntax
				EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
				#if valid
				if not EMAIL_REGEX.match(address):
					pass
				else:
					students = User.query(User.username == address.split('@')[0]).fetch()
					if len(students) == 0:
						sender = 'Question App Support <admin@{}.appspotmail.com>'.format(app_identity.get_application_id())
						to = address
						subject = 'Activate Your Account'
						body = 'Please click the following link to create your account  http://{}.appspot.com/register?username={}&classkey={}'.format(app_identity.get_application_id(),address.split('@')[0],classFromForm.key.urlsafe())
						email = Register().make_mail_message(sender,to,subject,body)
						if email != None:
							email.send()
					else:
						student = students[0]
						classList = student.classlist
						#already in class
						if (classFromForm in classList):
							pass
						#add student to new class
						else:
							student.classlist.append(classFromForm)
							student.put()
			self.success_redirect('DSUBMIT_SUCCESS', '/registrationhomepage')
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
		
class EditPersonalDataHandler(DefaultDraw):
	template_path_get = './html/reg_templates/EditPersonalInformation.html'
	def get(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):	
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
			self.draw(user, template_values)
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')

	def post(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):	
			fname = self.request.get('firstName')
			lname = self.request.get('lastName')
			pword = self.request.get('passWord')

			
			user = User.query(User.username == accountname).fetch()[0]
			user.firstname = fname
			user.lastname = lname
			user.password = pword
			user.put()
			#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditPersonalInformation.html')
			#self.response.write("fname = " + fname + ", lname = " + lname + ", pword = " + pword)
			#self.response.write(template.render())
			# Should also notify the instructor as to the student's changes.
			self.success_redirect('DSUBMIT_SUCCESS', '/registrationhomepage')
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
class EditReviewStudentsHandler(DefaultDraw):
	template_path_get = './html/reg_templates/EditReviewStudents.html'
	template_path_post = './html/reg_templates/EditReviewStudents.html'
	def get(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):	
			user = User.query(User.username == accountname).fetch()[0]
			if (user.accounttype == 'admin'):
				classes = Class.query(Class.classname != '')
			else:
				classes = user.classlist
				#classes = []
				#for _class in user.classlist:
				#	classes.append(_class)

			template_values = {
				'user': user,
				'classes': classes,
				'nextAction': 'show classlist'
				}
			self.draw(user, template_values)
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
			
	def post(self):
		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):
			user = User.query(User.username == accountname).fetch()[0]
			class_selection = self.request.get('selection')
				
			#class_selection = Class(classname = class_selection.classname)
			#self.response.out.write('class_selection:')
			#self.response.out.write(class_selection)

			#students = User.query(User.accounttype == 'student').fetch()
			#self.response.out.write('students:')
			#self.response.out.write(students)

			#stdnts = User.query(User.classlist.classname == class_selection.classname)
			
			class_select = Class.query(Class.classname == class_selection).fetch()
			if len(class_select) > 0:
				class_select = class_select[0]
				#self.response.write(" ** CLASSNAME ** = " + class_select.classname)
				usersInClass = User.query(User.classlist == class_select).fetch()

				#self.response.write(' USERSINCLASS: ')
				#self.response.write(usersInClass)
				template_values = {
					'user': user,
					'class': class_select,
					'users': usersInClass,
					'nextAction': 'show students in class'
				}
				self.draw(user, template_values)
			elif class_selection == 'all':
				template_values = {
					'user': user,
					'class': Class(classname='All Students'),
					'users': User.query().fetch(),
					'nextAction': 'show students in class'
				}
				self.draw(user, template_values)
			else:
				self.error_redirect('DSUBMIT_NO_CLASS_SELECTED', '/editreviewstudents')
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
class DisplayStudentsHandler(DefaultDraw):
	template_path_post = './html/reg_templates/EditReviewStudents.html'
	def post(self):
		accountname = self.session.get('account')
		userSelection = self.request.get('userSelection')
		if self.validate_user(accountname, SADMIN):
			if userSelection != '':
				user = User.query(User.username == accountname).fetch()[0]
				accounttype = user.accounttype
				userChosen = User.query(User.username == userSelection).fetch()[0]
				

				template_values = {
					'user': user,
					'userChosen': userChosen,
					'nextAction': 'show student data'
				}
				self.draw(user, template_values)
			else:
				self.error_redirect('DSUBMIT_NO_SELECTION', '/editreviewstudents')
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')		

class SaveDataHandler(DefaultDraw):
	template_path_post = './html/reg_templates/EditReviewStudents.html'
	def post(self):

		accountname = self.session.get('account')
		if self.validate_user(accountname, SADMIN):
			suser = User.query(User.username == accountname).fetch()
			if len(suser) !=0:
				suser = suser[0]
			else:
				suser = None
			user_key = self.request.get('user_key')
			if user_key != '':
				fname = self.request.get('firstName')
				lname = self.request.get('lastName')
				pword = self.request.get('passWord')
				user = ndb.Key(urlsafe=user_key).get()
				user.firstname = fname
				user.lastname = lname
				user.password = pword
				user.put()
			self.success_redirect('DSUBMIT_SUCCESS', '/registrationhomepage')
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/logout')
class RegisterHandler(DefaultDraw):
	template_path_get = './html/reg_templates/register.html'
	def get(self):		
		username = self.request.get('username')
		classkey = self.request.get('classkey')
		error = self.request.get('error')
		errormessage = ''
		accounttype = 'student'
		if error == 1 or error == '1':
			errormessage = "Password needs to be at least 8 characters long"
		elif error == 2 or error == '2':
			errormessage = "Passwords do not match"
		elif error == 3 or error == '3':
			errormessage = "First name or Last name not filled in"

		template_values = { 'classkey' : classkey, 'username' : username, 'accounttype': accounttype, 'error':errormessage}
		self.draw(None, template_values)
	def post(self):
		uname = self.request.get('username')
		pword = self.request.get('password')
		pword2 = self.request.get('password2')
		fname = self.request.get('firstname')
		lname = self.request.get('lastname')
		eml = self.request.get('email')
		key = self.request.get('classkey')
		type = 'student'
		
		if(fname == None) or (lname == None) or (pword == None) or (len(pword)) < 8 or pword != pword2:
		#error codes
		#1 pwd not long enough
		#2 pwd no match
		#3 fname,lname not filled out
			if (len(pword)) < 8:
				self.redirect('/register?username=' + uname + '&classkey='+key+'&error=1')
			if pword != pword2:
				self.redirect('/register?username=' + uname + '&classkey='+key+'&error=2')
			if "@" not in eml:
				self.redirect('/register?username=' + uname + '&classkey='+key+'&error=4')
			if "." not in eml:
				self.redirect('/register?username=' + uname + '&classkey='+key+'&error=4')
			self.redirect('/register?username=' + uname + '&classkey='+key+'&error=3')
		else:
			newStudent = User(username = uname,password = pword,lastname = lname,firstname = fname,email = eml,accounttype = type)
			classy = Key(urlsafe = key).get()
			newStudent.classlist.append(classy)
			newStudent.put()
			time.sleep(2)
			self.success_redirect('DSUBMIT_ACCT_SUCCESS', '/')
				
class RegisterInstructorHandler(DefaultDraw):
	template_path_get = '/html/reg_templates/RegisterInstructor.html'
	def get(self):

		username = self.request.get('username')
		classkey = self.request.get('classkey')
		error = self.request.get('error')
		errormessage = ''
		accounttype = 'instructor'
		if error == 1 or error == '1':
			errormessage = "Password needs to be at least 8 characters long"
		elif error == 2 or error == '2':
			errormessage = "Passwords do not match"
		elif error == 3 or error == '3':
			errormessage = "First name or Last name not filled in"

		template_values = { 'classkey' : classkey, 'username' : username, 'accounttype': accounttype, 'error':errormessage}
		self.draw(None, template_values)
	def post(self):
		uname = self.request.get('username')
		pword = self.request.get('password')
		pword2 = self.request.get('password2')
		fname = self.request.get('firstname')
		lname = self.request.get('lastname')
		eml = self.request.get('email')
		#key = self.request.get('classkey')
		type = 'instructor'
		
		if(fname == None) or (lname == None) or (pword == None) or (len(pword)) < 8 or pword != pword2:
		#error codes
		#1 pwd not long enough
		#2 pwd no match
		#3 fname,lname not filled out
		#4 invalid email
			if (len(pword)) < 8:
				self.redirect('/registerinstructor?username=' + uname + '&classkey='+key+'&error=1')
			if pword != pword2:
				self.redirect('/registerinstructor?username=' + uname + '&classkey='+key+'&error=2')
			if "@" not in eml:
				self.redirect('/registerinstructor?username=' + uname + '&classkey='+key+'&error=4')
			if "." not in eml:
				self.redirect('/registerinstructor?username=' + uname + '&classkey='+key+'&error=4')
			self.redirect('/register?username=' + uname + '&classkey='+key+'&error=3')
		else:
			newInstructor = User(username = uname,password = pword,lastname = lname,firstname = fname,email = eml,accounttype = type)
			#classy = Key(urlsafe = key).get()
			#newInstructor.classlist.append(classy)
			newInstructor.put()
			time.sleep(2)
			self.success_redirect('DSUBMIT_ACCT_SUCCESS', '/')
			
class AddInstructorToClassHandler(BaseHandler):
	def get(self):
		instructors = User.query(User.accounttype == 'instructor').fetch()
		classes = Class.query().fetch()
		
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/addtoclass.html')
		
		template_values = { 'classes' : classes, 'instructors' : instructors}
		self.response.write(template.render(template_values))
		
	def post(self):
		instructorAssigned = self.request.get("instructorAssigned")
		classAssigned = self.request.get("classAssigned")
		
		instructor = User.query(User.username == instructorAssigned).fetch()[0]
		classy = Class.query(Class.classname == classAssigned).fetch()[0]
		instructor.classlist.append(classy)
		instructor.put()
		self.success_redirect('DSUBMIT_ACCT_SUCCESS', '/')
		
