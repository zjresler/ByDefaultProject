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
	def get(self):
		username = self.session.get('account')
		accountname = self.session.get('account')
		accounttype = self.session.get('accounttype')
		class_get = self.session.get('class')
	
	   
		if username != '':
			user = User.query(User.username == username).fetch()[0]
			user_key = user.key
			classes = Class.query(Class.classname == class_get).fetch()
			#classname = user.classlist
			que = Question.query(Question.senderUID == user_key and Question.classUID == classes[0].key).fetch()		
			if user.accounttype == 'student':
				template_values = {'title': 'Past Questions & Answers','accounttype': accounttype,'accountname' : accountname}
				template_values['questions'] = que
				template = JINJA_ENVIRONMENT.get_template('./html/PastQA.html')
			else:
				self.response.write('You are not logged in.')
				#time.sleep(2)
				self.redirect('/')
				
			template = JINJA_ENVIRONMENT.get_template('./html/PastQA.html')
			self.response.write(template.render(template_values))
		else:
			self.response.write('You are not logged in.')
			#time.sleep(2)
			self.redirect('/')
		#self.response.write(template.render(template_values))
class ReviewHandler(BaseHandler):
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
				template_values['questions'] = Question.query(Question.senderUID == user_key and Question.classUID == classy.key).fetch()
				template_values['admin'] = False
				template_values['student'] = True
			elif user.accounttype == 'instructor':
				template_values['questions'] = Question.query(Question.respondentUID == None and Question.classUID == classy.key).fetch()
				template_values['instructor'] = True
				template_values['student'] = False
			else:
				self.error_redirect('INVALID_LOGIN_STATE', '/')
				
			template = JINJA_ENVIRONMENT.get_template('./html/review.html')
			self.response.write(template.render(template_values))
		else:
			self.error_redirect('INVALID_LOGIN_STATE', '/')

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
