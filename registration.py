<<<<<<< HEAD
import webapp2
import smtplib
import random
import os
import urllib
import jinja2
import re

from db_entities import *
from basehandler import BaseHandler
from basehandler import *
from login import *
from smtplib import SMTPException
from google.appengine.ext import ndb
from webapp2_extras import sessions
from google.appengine.api.mail import EmailMessage
from google.appengine.api import app_identity
from google.appengine.ext import ndb



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
	
	
class RegistrationMainHandler(BaseHandler):
	def get(self): 
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/MainPage_AccountAdministration.html')
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		
		template_values = {
			'user': user
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
			if firstNameFromForm == '': 
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
		classFromForm = None
		if len(Class.query(Class.classname == self.request.get('class')).fetch()) == 0:
			classFromForm = Class(classname=self.request.get('class'))
			classFromForm.put()
		else:
			classFromForm = Class.query(Class.classname == self.request.get('class')).fetch()[0]
		textFromForm = self.request.get('textArea').strip()
		
		accountname = self.session.get('account')
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
			students = User.query(User.username == address).fetch()
			if len(students) == 0:
				sender = 'Question App Support <admin@{}.appspotmail.com>'.format(app_identity.get_application_id())
				to = address
				subject = 'Activation Your Account'
				body = 'Please click the following link to create your account<br>  {}.appspot.com/register?username={}&classkey={}'.format(app_identity.get_application_id(),address.split('@')[0],classFromForm.key.urlsafe())
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
					
		self.redirect('/registerhomepage')
					
"""		
		# IF USER IS AN ADMIN, GET THE INSTRUCTOR FOR THE NEW CLASS
		if(accounttype == 'admin'): 
			self.request.get('instructorAssigned')
		else:
			# IF USER IS AN INSTRUCTOR, ADD THE INSTRUCTOR TO THE CLASS IF NOT ALREADY ASSIGNED
			userClassList = user.classlist
	#		self.response.write("classFromForm:")
	#		self.response.write(classFromForm)
	#		self.response.write("userClassList:")
	#		self.response.write(userClassList)
			if not(classFromForm in userClassList): #not (classnameFromForm in user.classlist):
				user.classlist.append(classFromForm)
				user.put()


		#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewStudents.html')
		#self.response.out.write(" class = " + currentClass + ", addresses = " + text)
		#self.response.write(template.render())
		
		# Parse each email address from between commas
		addressList = []
		newAddress =''
		BlankAddy = False
		for character in textFromForm:
			if character != ',' and character !='*':
				newAddress += character
			elif len(newAddress) > 0:
					addressList.append(newAddress)
					newAddress=''
			else:
				BlankAddy = True
		if len(addressList) == 0: 
			BlankAddy = True
		
		if not BlankAddy and len(classFromForm.classname) != 0:
			# Add the addresses to the datastore if not already existing there.
			# Otherwise, see if the account is already a member in the class.
			# If not a member, add to the classlist.

			passwordLog = []
			for studentToAdd in addressList:
				# IF 'student[0]' DOES NOT EXIST, THEN ADD AS NEW USER
				students = User.query(User.username == studentToAdd).fetch()
				Unique = True
				for student in students:
					if student.username == studentToAdd:
						Unique = False
				if Unique:
					passWord = str(random.randrange(100000,1000000))
					passwordLog.append([studentToAdd, passWord])
					newStudent = User(
						username=studentToAdd,
						password=passWord,
						lastname='temp',
						firstname='temp',
						email=studentToAdd,
						accounttype='student'
						)
					newStudent.classlist.append(classFromForm)
					newStudent.put()
				# SINCE STUDENT ALREADY EXISTS, IS THE STUDENT ALREADY A MEMBER OF THE CLASS?
				else:
					textmsg = ''
					student = User.query(User.username == studentToAdd).fetch()[0]
					self.response.write('student: ' + student.username)
					classList = student.classlist
					self.response.write(classList)
					self.response.write('\n')
					self.response.write(classFromForm in classList)
					if (classFromForm in classList):
						textmsg = ', already in class'
					else:
						student.classlist.append(classFromForm)
						student.put()
						textmsg = ', added to ' + classFromForm.classname
							
					passwordLog.append([studentToAdd, 'existing user' + textmsg])

		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/DisplayNewStudents.html')
		template_values = { "log": passwordLog, "class": classFromForm.classname }
		self.response.write(template.render(template_values))
		"""

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

class EditReviewStudentsHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		accountname = self.session.get('account')
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
		self.response.write(template.render(template_values))

	def post(self):
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		class_selection = self.request.get('selection')
		#class_selection = Class(classname = class_selection.classname)
		#self.response.out.write('class_selection:')
		#self.response.out.write(class_selection)

		#students = User.query(User.accounttype == 'student').fetch()
		#self.response.out.write('students:')
		#self.response.out.write(students)

		#stdnts = User.query(User.classlist.classname == class_selection.classname)
		
		class_select = Class(classname = class_selection)
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

		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render(template_values))

class DisplayStudentsHandler(BaseHandler):
	def post(self):
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		userSelection = self.request.get('userSelection')
		userChosen = User.query(User.username == userSelection).fetch()[0]
		#self.response.out.write(students)
		
		self.response.write("userChosen: " + userChosen.username)

		template_values = {
			'user': user,
			'userChosen': userChosen,
			'nextAction': 'show student data'
		}
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render(template_values))

class SaveDataHandler(BaseHandler):
	def post(self):
		userFirstName = self.request.get('firstName')
		userLastName = self.request.get('lastName')
		userPassword = self.request.get('passWord')
		user = User.query(  User.firstname == userFirstName and
							User.lastname == userLastName and 
							User.password == userPassword).fetch()
		self.response.write(user)
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render())
class RegisterHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/register.html')

		username = self.request.get('username')
		classkey = self.request.get('classkey')
		accounttype = 'student'

		template_values = { 'classkey' : classkey, 'username' : username, 'accounttype': accounttype}
		self.response.write(template.render(template_values))
	def post(self):
		uname = self.request.get('username')
		pword = self.request.get('password')
		fname = self.request.get('firstname')
		lname = self.request.get('lastname')
		eml = uname
		key = self.request.get('classkey')
		type = 'student'
		
		if(fname == None) or (lname == None) or (pword == None) or (len(pword) < 8):
			self.redirect('/register?username=' + uname + '&classkey='+key)
		else:
			newStudent = User(username = uname,password = pword,lastname = lname,firstname = fname,email = eml,accounttype = type)
			classy = Key(urlsafe = key).get()
			newStudent.classlist.append(classy)
			newStudent.put()
			self.redirect('/')
		

=======
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
		
		template_values = {
			'user': user
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
			if firstNameFromForm == '': 
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
		classFromForm = Class(classname=self.request.get('class'))
		textFromForm = self.request.get('textArea').strip() + '*'

		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype

		instructorAssigned = ""
		# IF USER IS AN ADMIN, GET THE INSTRUCTOR FOR THE NEW CLASS
		if(accounttype == 'admin'): 
			self.request.get('instructorAssigned')
		else:
			# IF USER IS AN INSTRUCTOR, ADD THE INSTRUCTOR TO THE CLASS IF NOT ALREADY ASSIGNED
			userClassList = user.classlist
			self.response.write("classFromForm:")
			self.response.write(classFromForm)
			self.response.write("userClassList:")
			self.response.write(userClassList)
			if not(classFromForm in userClassList): #not (classnameFromForm in user.classlist):
				user.classlist.append(classFromForm)
				user.put()


		#template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/AddNewStudents.html')
		#self.response.out.write(" class = " + currentClass + ", addresses = " + text)
		#self.response.write(template.render())
		
		# Parse each email address from between commas
		addressList = []
		newAddress =''
		BlankAddy = False
		for character in textFromForm:
			if character != ',' and character !='*':
				newAddress += character
			elif len(newAddress) > 0:
					addressList.append(newAddress)
					newAddress=''
			else:
				BlankAddy = True
		if len(addressList) == 0: 
			BlankAddy = True
		
		if not BlankAddy and len(classFromForm.classname) != 0:
			# Add the addresses to the datastore if not already existing there.
			# Otherwise, see if the account is already a member in the class.
			# If not a member, add to the classlist.

			passwordLog = []
			for studentToAdd in addressList:
				# IF 'student[0]' DOES NOT EXIST, THEN ADD AS NEW USER
				students = User.query(User.username == studentToAdd).fetch()
				Unique = True
				for student in students:
					if student.username == studentToAdd:
						Unique = False
				if Unique:
					passWord = str(random.randrange(100000,1000000))
					passwordLog.append([studentToAdd, passWord])
					newStudent = User(
						username=studentToAdd,
						password=passWord,
						lastname='temp',
						firstname='temp',
						email=studentToAdd,
						accounttype='student'
						)
					newStudent.classlist.append(classFromForm)
					newStudent.put()
				# SINCE STUDENT ALREADY EXISTS, IS THE STUDENT ALREADY A MEMBER OF THE CLASS?
				else:
					textmsg = ''
					student = User.query(User.username == studentToAdd).fetch()[0]
					self.response.write('student: ' + student.username)
					classList = student.classlist
					self.response.write(classList)
					self.response.write('\n')
					self.response.write(classFromForm in classList)
					if (classFromForm in classList):
						textmsg = ', already in class'
					else:
						student.classlist.append(classFromForm)
						student.put()
						textmsg = ', added to ' + classFromForm.classname
							
					passwordLog.append([studentToAdd, 'existing user' + textmsg])

		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/DisplayNewStudents.html')
		template_values = { "log": passwordLog, "class": classFromForm.classname }
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

class EditReviewStudentsHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		accountname = self.session.get('account')
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
		self.response.write(template.render(template_values))

	def post(self):
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		class_selection = self.request.get('selection')
		#class_selection = Class(classname = class_selection.classname)
		#self.response.out.write('class_selection:')
		#self.response.out.write(class_selection)

		#students = User.query(User.accounttype == 'student').fetch()
		#self.response.out.write('students:')
		#self.response.out.write(students)

		#stdnts = User.query(User.classlist.classname == class_selection.classname)
		
		class_select = Class(classname = class_selection)
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

		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render(template_values))

class DisplayStudentsHandler(BaseHandler):
	def post(self):
		accountname = self.session.get('account')
		user = User.query(User.username == accountname).fetch()[0]
		accounttype = user.accounttype
		userSelection = self.request.get('userSelection')
		userChosen = User.query(User.username == userSelection).fetch()[0]
		#self.response.out.write(students)
		
		self.response.write("userChosen: " + userChosen.username)

		template_values = {
			'user': user,
			'userChosen': userChosen,
			'nextAction': 'show student data'
		}
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render(template_values))

class SaveDataHandler(BaseHandler):
	def post(self):
		userFirstName = self.request.get('firstName')
		userLastName = self.request.get('lastName')
		userPassword = self.request.get('passWord')
		user = User.query(  User.firstname == userFirstName and
							User.lastname == userLastName and 
							User.password == userPassword).fetch()
		self.response.write(user)
		template = JINJA_ENVIRONMENT.get_template('/html/reg_templates/EditReviewStudents.html')
		self.response.write(template.render())




>>>>>>> origin/master
