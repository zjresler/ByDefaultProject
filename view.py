#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import random
import os
import urllib
import jinja2

from db_entities import *
from basehandler import BaseHandler

from google.appengine.ext import ndb
from webapp2_extras import sessions

from strings import *

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)


class ViewQuestionsHandler(BaseHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('./html/Viewquestions.html')
		template_values = {
			'title': 'View Questions'
		}

		self.response.write(template.render(template_values))


class PastQAHandler(BaseHandler):
	template_path_get = './html/PastQA.html'
	template_path_post= ''
	def draw(self, user, template_values={}):
		template_values['banner'] = self.build_banner(user)
		if self.request.method == 'GET':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_get)
			self.response.write(template.render(template_values))
		elif self.request.method == 'POST':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_post)
			self.response.write(template.render(template_values))
		else:
			exit('Write method called with invalid method.')
		
	def get(self):
		username = self.session.get('account')
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		class_get = self.session.get('class')
		
	   
		if self.validate_user(accountname):
			user = User.query(User.username==accountname).fetch()[0]
			if accounttype == '':
				self.session['accounttype'] = user.accounttype
				accounttype = user.accounttype
			user_key = user.key
			classes = Class.query(Class.classname == class_get).fetch()
			#classname = user.classlist
			if accounttype == STUDENT:
				que = user_key.get().questions					
#				if len(classes) == 0:
#
#				else:
#					que = Question.query(Question.classUID == classes[0].key, ancestor=user_key).fetch()
				template_values = {'title': 'Past Questions & Answers','accounttype': accounttype,'accountname' : accountname}
				template_values['questions'] = que
				template = JINJA_ENVIRONMENT.get_template('./html/PastQA.html')
				self.draw(user, template_values)
			elif accounttype == ADMIN:
				que = user_key.get().questions
#				if len(classes) == 0:
#				
#				else:
#					que = Question.query(Question.respondentUID == user_key, Question.classUID == classes[0].key).fetch()	
				template_values = {'title': 'Past Questions & Answers','accounttype': accounttype,'accountname' : accountname}
				template_values['questions'] = que
				template = JINJA_ENVIRONMENT.get_template('./html/PastQA.html')
				self.draw(user, template_values)
			else:
				
				super(PastQAHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
				
			
		else:
			super(PastQAHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
		
class ReviewHandler(BaseHandler):

	template_path_get = ''
	template_path_post= './html/review.html'
	
	def draw(self, user, template_values={}):
		template_values['banner'] = self.build_banner(user)
		if self.request.method == 'GET':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_get)
			self.response.write(template.render(template_values))
		elif self.request.method == 'POST':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_post)
			self.response.write(template.render(template_values))
		else:
			exit('Write method called with invalid method.')
	def post(self):
		username = self.session.get('account')
		accounttype = self.session.get('accounttype')
		classname = self.request.get('class')
		self.session['class'] = classname
		
		template_values = {
			'title': 'Review questions',
			'accounttype': accounttype,
			'accountname': username
			
		}
		classy = Class.query(Class.classname == classname).fetch()[0]
		if username != '':
			user = User.query(User.username == username).fetch()[0]
			
			
			user_key = user.key
			
			if user.accounttype == 'student':
				template_values['questions'] = Question.query(Question.classUID == classy.key, ancestor = user_key).fetch()
				template_values['admin'] = False
				template_values['student'] = True
			elif user.accounttype == 'instructor':
				template_values['questions'] = classy.open_questions
				template_values['instructor'] = True
				template_values['student'] = False
			else:
				super(ReviewHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')
				
			template = JINJA_ENVIRONMENT.get_template('./html/review.html')
			self.draw(user, template_values)
		else:
			super(ReviewHandler, self).error_redirect('INVALID_LOGIN_STATE', '/')

class FAQ(BaseHandler):
	def post(self):
		template = JINJA_ENVIRONMENT.get_template('./html/faq.html')

		faq=['Where is the class?','EMS 190','Is there any extra credit in the class?','No.','Are books required for the class?','Yes.',
			 'Which is better python or java?','Definitely java.',
	 		'Can I make up the test?','Yes, if you have a valid excuse.',
			 'Are the test curved?','Depends on how poorly the class does on the test.',
			 'Is the class curved?','Depends on the situation.']

		template_values = {
			'title': 'FAQ',
			'faq': faq
		}
		self.response.write(template.render(template_values))


class Register(BaseHandler):
	def post(self):
		template = JINJA_ENVIRONMENT.get_template('./html/Student_Registration.html')
		template_values={
			'title': 'Student Registration'
		}
		self.response.write(template.render(template_values))
