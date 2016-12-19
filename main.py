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
import jinja2
import os
import time
import test_question_system

from db_entities import *
from strings import *

from basehandler import *
from login import *
from question_system import *
from view import *
#from test_question_system import ValidateUserTestHandler
from registration import *
from faq import *

from google.appengine.ext import ndb
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class DumpDBHandler(BaseHandler):
	def get(self):
		# I got sick of doing it manually
		for q in Question.query().fetch():
			q.key.delete()
		for u in User.query().fetch():
			u.key.delete()
		for c in Class.query().fetch():
			c.key.delete()
		for t in Category.query().fetch():
			t.key.delete()
		time.sleep(2)
		self.redirect('/ctu')
		
class TestOutputHandler(BaseHandler):
	def get(self):
		classes_to_dump = Class.query(Class.classname == 'TESTCLASS_test').fetch()
		for c in classes_to_dump:
			if c.key != None:
				self.response.write('Dumping Class: '+c.classname+'<br>')
				c.key.delete()
		time.sleep(2)
		self.response.write('Starting tests, this may take a few minutes...')
		test_question_system.runner.stream.data = ''
		test_question_system.runner.run(test_question_system.suite)
		self.response.write(test_question_system.runner.stream.data)

class LoginHandler(BaseHandler):
    def get(self):
		template = JINJA_ENVIRONMENT.get_template('./html/login.html')
		self.response.write(template.render({'banner': BANNER_DEFAULT_0 + BANNER_END}))
class createresettestusers(BaseHandler):
	def get(self):
		if len(User.query(User.username == 'admin').fetch()) == 0:
			u = User(
				username = 'admin',
				password = 'admin',
				firstname = 'test',
				lastname = 'test',
				email = 'test',
				accounttype ='admin'
			)
			u_key = u.unique_put()
		else:
			u = User.query(User.username == 'admin').fetch()[0]
			u_key = u.key
			
		if len(User.query(User.username == 'student').fetch()) == 0:
			s = User(
				username = 'student',
				password = 'student',
				firstname = 'student',
				lastname = 'student',
				email = 'student',
				accounttype ='student'
			)
			s_key = s.unique_put()
		else:
			s = User.query(User.username == 'student').fetch()[0]
			s_key = s.key
			
		if len(User.query(User.username == 'instructor').fetch()) == 0:
			i = User(
				username = 'instructor',
				password = 'instructor',
				firstname = 'instructor',
				lastname = 'instructor',
				email = 'instructor',
				accounttype ='instructor'
			)
			i_key = i.unique_put()
		else:
			i = User.query(User.username == 'instructor').fetch()[0]
			i_key = i.key
		time.sleep(2)
		c = Class(classname = 'TESTCLASS')
		d = Class(classname = 'test2')
		c.unique_put()
		d.unique_put()
		time.sleep(2)
		s = s_key.get()
		u = u_key.get()
		i = i_key.get()
		s.reset_classlist()
		u.reset_classlist()
		i.reset_classlist()
		u.add_class(c)
		u.add_class(d)
		s.add_class(c)
		s.add_class(d)
		i.add_class(c)
		i.add_class(d)
		i.put()
		u.put()
		s.put()
		time.sleep(2)
		self.redirect('/')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': SECRET_KEY,
}		

app = webapp2.WSGIApplication([
    ('/', LoginHandler),
	('/ask', QuestionHandler),
	('/respond', ResponseHandler),
	('/review',ReviewHandler),
	('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/homepage', HomeHandler),
    ('/admin', AdminHandler),
    ('/studenthomepage', StudentHomeHandler),
    ('/instructorhomepage', InstructorHomeHandler),
#	('/t', ValidateUserTestHandler),
	('/tests', TestOutputHandler),
	('/ddb', DumpDBHandler),
    ('/registrationhomepage', RegistrationMainHandler),
    ('/addinstructor', AddInstructorHandler),
    ('/addstudent', AddStudentHandler),
	('/PastQA', PastQAHandler),
	('/faq', FAQHandler),
	('/register', RegisterHandler),
	('/editreviewstudents', EditReviewStudentsHandler),
#	('/enroll', AddUserToClass),
	('/displaystudents', DisplayStudentsHandler),
	('/savedata', SaveDataHandler),
	('/ctu', createresettestusers),
	('/registerinstructor', RegisterInstructorHandler),
	('/addtoclass', AddInstructorToClassHandler)
], config=config, debug=True)
