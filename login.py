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

from db_entities import *
from basehandler import BaseHandler

from google.appengine.ext import ndb
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

from webapp2_extras import sessions

class LogoutHandler(BaseHandler):
	def get(self):
		self.session['account'] = ''
		self.session['accounttype'] = ''
		template = JINJA_ENVIRONMENT.get_template('./html/login.html')
		self.response.write(template.render({'banner': BANNER_DEFAULT_0 + BANNER_END}))


class HomeHandler(BaseHandler):
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		user = User.query(User.username == username).fetch()
		if len(user) != 0:
			
			if user[0].password == password:
				self.session['account'] = username
				self.session['accounttype'] = user[0].accounttype
				if(user[0].accounttype == 'student'):
					self.redirect('/studenthomepage')
				elif(user[0].accounttype == 'admin'):
					self.redirect('/registrationhomepage')
				elif(user[0].accounttype == 'instructor'):
					self.redirect('/instructorhomepage')
				#else:
					#self.redirect('/admin')
			else:
				self.redirect('/login')
		else:
			self.redirect('/login')
class StudentHomeHandler(BaseHandler):
	template_path_get = './html/studenthomepage.html'
	
	def draw(self, user, template_values={}):
		template_values['banner'] = self.build_banner(user)
		if self.request.method == 'GET':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_get)
			self.response.write(template.render(template_values))
		else:
			exit('Write method called with invalid method.')
	def get(self):
		accountname = self.session.get('account')
		
		self.session['class'] = ''
		html_debug = """
		
			<div class=\"console\">
				<table class="consoleTable">
				<tr><th>Variable Name</th><th>Value as string</th></tr>
				"""
			
		if accountname != '':
			user = User.query(User.username == accountname).fetch()[0]
			html_debug = html_debug + """
				<tr><td>user</td><td>"""+str(user)+"""</td></tr>
				</table>
			</div>
			
			"""
			if user.accounttype == 'student':
				self.draw(user, {
					'accountname': accountname,
					'accounttype': user.accounttype,
					'classlist': user.classlist,
					'path': '/ask',
					'method': 'get'
				})
			else:
				self.redirect('/')
		else:
			self.redirect('/')
		self.response.write(html_debug)
		
class InstructorHomeHandler(BaseHandler):
	template_path_get = './html/studenthomepage.html'
	def draw(self, user, template_values={}):
		template_values['banner'] = self.build_banner(user)
		if self.request.method == 'GET':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_get)
			self.response.write(template.render(template_values))
		else:
			exit('Write method called with invalid method.')
	def get(self):
		accountname = self.session.get('account')
		self.session['class'] = ''
			
		if accountname != '':
			user = User.query(User.username == accountname).fetch()[0]
			if user.accounttype == 'instructor':
				template = JINJA_ENVIRONMENT.get_template('./html/studenthomepage.html')
				self.draw(user, {
					'accountname': accountname,
					'accounttype': user.accounttype,
					'classlist': user.classlist,
					'path': '/review',
					'method': 'post'
				})
			else:
				self.redirect('/')
		else:
			self.redirect('/')

class AdminHandler(BaseHandler):
	template_path_get = './html/studenthomepage.html'
	def draw(self, user, template_values={}):
		template_values['banner'] = self.build_banner(user)
		if self.request.method == 'GET':
			template = JINJA_ENVIRONMENT.get_template(self.template_path_get)
			self.response.write(template.render(template_values))
		else:
			exit('Write method called with invalid method.')
	def get(self):
		accountname = self.session.get('account')
		if accountname != '':
			user = User.query(User.username == accountname).fetch()[0]
			if user.accounttype == 'admin':
				template = JINJA_ENVIRONMENT.get_template('./html/admin.html')
				self.response.write(template.render())
			else:
				self.redirect('/')
		else:
			self.redirect('/')
	def post(self):
		username_from_form = self.request.get('username')
		password_from_form = self.request.get('password')
		accountype_from_form = self.request.get('accounttype')
		fname = self.request.get('firstname')
		lname = self.request.get('lastname')
		email = self.request.get('email')
		newuser = User(
			username=username_from_form,
			password=password_from_form,
			accounttype=accountype_from_form,
			firstname = fname,
			lastname = lname,
			email = email 
		)
		newuser.unique_put()
		self.redirect('/admin')
