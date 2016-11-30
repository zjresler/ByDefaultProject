#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
		self.submit_question_wrapper(accountname, accounttype, classname)
			
	def submit_question_wrapper(self, accountname, accounttype, classname):
		if self.validate_user(accountname, accounttype=STUDENT):
			user = User.query(User.username == accountname).fetch()[0]
			#user has correct type
			classes = Class.query(Class.classname==classname).fetch()
			if len(classes) !=1:
				#class was not found or more than one class was found
				super(QuestionHandler, self).error_redirect('CLASS_NOT_FOUND', '/studenthomepage')
			
			question = Question(senderUID = user.key, classUID = classes[0].key, message = self.session.get('message'))
			if question.submit_question() != 0:
				self.session.pop('class')
				self.session.pop('message')
				super(QuestionHandler, self).success_redirect('QSUBMIT_SUCCESS', '/studenthomepage')
			else:
				super(QuestionHandler, self).error_redirect('QSUBMIT_FAIL', '/ask')
		else:
			super(QuestionHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')

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
		#self.response.write(accountname+'<br>'+accounttype+'<br>'+classname+'<br>'+questionkey+'<br>'+Key(urlsafe=questionkey).get().senderUID.urlsafe())
		#tq = Key(urlsafe=questionkey).get()
		#questions = Question.query(Question.key tq.key and Question.senderUID == tq.senderUID and Question.classUID	== tq.classUID).fetch()
		#self.response.write('<br>'+tq.message+'<br>'+str(len(questions)))
		if self.validate_user(accountname, accounttype = ADMIN):
			#user has correct type
			classy = Class.query(Class.classname==classname).fetch()
			#check that the class in the session was found in the database
			#TODO: add a loop to check that the class is in the user's classlist
			if len(classy) == 1:
				classy = classy[0]
				question = None
				try:
					question = Key(urlsafe=questionkey).get()
				except TypeError:
					#corrupt or non existent questionkey
					super(ResponseHandler, self).error_redirect('QKEY_CORRUPT', '/instructorhomepage')
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
				
				if question.respond_question(user.key, response) != 0:
					self.session.pop('class')
					self.session.pop('question')
					super(ResponseHandler, self).success_redirect('RSUBMIT_SUCCESS', '/instructorhomepage')
				else:
					super(ResponseHandler, self).error_redirect('RSUBMIT_FAIL', '/instructorhomepage')
			else:
				super(ResponseHandler, self).error_redirect('CLASS_NOT_FOUND', '/instructorhomepage')

		else:		
			super(ResponseHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
			
	def respond_question_wrapper(self, response, question, accountname, accounttype, classname, categoryname, new_cname):
		#testable version
		return 0