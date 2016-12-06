#	
#	Question Submission and Response Handlers for By Default QA System
#	Copyright (C) 2016  Damian Kendzior, By Default 
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import webapp2
import os
import jinja2
import time

from db_entities import *
from basehandler import BaseHandler
from strings import *

from google.appengine.ext import ndb
from google.appengine.ext.ndb import Key
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)


class QuestionHandler(BaseHandler):
	def get(self): #where question is composed by the user
		#gets the accountname, accounttype, and classname
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		classname = self.request.get('class')
		#add the classname to the session
		self.session['class'] = classname
		if self.validate_user(accountname, accounttype=STUDENT):
			classes = Class.query(Class.classname==classname).fetch()
			
			#check that the class in the session was found in the database
			#TODO: add a loop to check that the class is in the user's classlist
			if len(classes) == 1:
				#class was found
				template = JINJA_ENVIRONMENT.get_template('./html/ask.html')
				self.response.write(template.render())
			else:
				#class was not found or more than one class was found
				#redirect to your homepage
				super(QuestionHandler, self).error_redirect('CLASS_NOT_FOUND', '/studenthomepage')
		else:		
			super(QuestionHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
			
	def post(self):
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		classname = self.session.get('class')
		self.session['message'] = self.request.get('message')
		ret = self.submit_question_wrapper(accountname, accounttype, classname, self.request.get('message'))
		if ret == 1:
			self.session.pop('class')
			self.session.pop('message')
			super(QuestionHandler, self).success_redirect('QSUBMIT_SUCCESS', '/studenthomepage')
		elif ret == -1:
			super(QuestionHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
		elif ret == -2:
			super(QuestionHandler, self).error_redirect('QSUBMIT_FAIL', '/ask')
		elif ret == -3:
			super(QuestionHandler, self).error_redirect('CLASS_NOT_FOUND', '/studenthomepage')
			
	def submit_question_wrapper(self, accountname, accounttype, classname, message):
		if self.validate_user(accountname, accounttype=STUDENT):
			user = User.query(User.username == accountname).fetch()[0]
			#user has correct type
			classes = Class.query(Class.classname==classname).fetch()
			if len(classes) !=1:
				#class was not found or more than one class was found
				return -3
			question = Question(parent=user.key, classUID = classes[0].key, message = message)
			if question.submit_question() != 0:
				return 1
			else:	
				return -2
		else:
			return -1

class ResponseHandler(BaseHandler):

	def get(self):
		#display all of the questions and post when one is selected
		#	class_name = self.request.get('class_name')
		#	questions = Question.query(Question.classUID.get().name == class_name && Question.respondentUID == None).fetch()
		#assuming we were redirected here from a question slect and the question id/UID was sent via get
		
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		classname = self.session.get('class')
		questionkey = self.request.get('questionkey')
		
		if self.validate_user(accountname, accounttype = ADMIN):
			#user has correct type
			classy = Class.query(Class.classname==classname).fetch()
			#check that the class in the session was found in the database
			#TODO: add a loop to check that the class is in the user's classlist
			if len(classy) == 1:
				classy = classy[0]
				#question = None
				#try:
				question = Key(urlsafe=questionkey).get()
				#except TypeError:
					#corrupt or non existent questionkey
					#super(ResponseHandler, self).error_redirect('QKEY_CORRUPT', '/instructorhomepage')
				#question retrieved successfully
				self.session['question_key'] = questionkey
				data = {
					'question': question,
					'accountname': accountname,
					'categories': classy.categories,
				}
				template = JINJA_ENVIRONMENT.get_template('./html/respond.html')
				self.response.write(template.render(data))
			else:
				#class was not found or more than one class was found
				#redirect to your homepage
				super(ResponseHandler, self).error_redirect('CLASS_NOT_FOUND', '/instructorhomepage')
		else:		
			super(ResponseHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
	
	def post(self):
		
		response = self.request.get('response')
		question = Key(urlsafe = self.session.get('question_key')).get()
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		classname = self.session.get('class')
		categoryname = self.request.get('cname')
		new_cname = self.request.get('new_cname')
		if self.validate_user(accountname, accounttype = ADMIN):
			#user is logged in as accountname qand accounttype is ADMIN
			user = User.query(User.username == accountname).fetch()[0]
			classes = Class.query(Class.classname == classname).fetch()
			if len(classes) == 1:
				classy = classes[0]
				
				if categoryname != 'none' and categoryname != '':
				
					if categoryname == 'newCategory' and new_cname != '':
						categoryname = new_cname
						
					category = Category.query(Category.name == categoryname, ancestor=classy.key).fetch()
					if len(category) == 1:
						category = category[0]
					elif len(category) == 0:
						category = Category(name=categoryname, parent=classy.key)
						category.put()
					else:
						category = None
					if category != None:
						question.category = category.key
				if question.respond_question(user.key, response)==1:
					self.session.pop('class')
					self.session.pop('question_key')
					super(ResponseHandler, self).success_redirect('RSUBMIT_SUCCESS', '/instructorhomepage')
				else:
					super(ResponseHandler, self).error_redirect('RSUBMIT_FAIL', '/instructorhomepage')
			else:
				super(ResponseHandler, self).error_redirect('CLASS_NOT_FOUND', '/instructorhomepage')
		else:		
			super(ResponseHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
			
#	def respond_question_wrapper(self, response, question, accountname, accounttype, classname, categoryname, new_cname):
#		return 0