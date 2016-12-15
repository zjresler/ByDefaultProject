import webapp2
import os
import jinja2
import time

from db_entities import *
from basehandler import BaseHandler

from google.appengine.ext import ndb
from google.appengine.ext.ndb import Key
from webapp2_extras import sessions

from strings import *
JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)


class FAQHandler(BaseHandler):
	
	template_path_get = './html/view.html'
	template_path_post = './html/FAQ.html'
	
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
		classes = Class.query().fetch()
		username = ''
		accounttype = ''
		user = None
		if 'account' in self.session and self.session['account']!='':
			username = self.session.get('account')
			user = User.query(User.username == username).fetch()
			if len(user) == 1:
				accounttype = user[0].accounttype
				user=user[0]
			else:
				user=None
		template_values = {'class': classes, 'accountname': username}
		self.draw(user, template_values)

		
		
	def post(self):
		class_get = self.request.get_all('Class')
		classname = class_get[0]
		
		username = ''
		accounttype = ''
		user = None
		if 'account' in self.session and self.session['account']!='':
			username = self.session.get('account')
			user = User.query(User.username == username).fetch()
			if len(user) == 1:
				accounttype = user[0].accounttype
				user = user[0]
			else:
				user = None
		class_get = Class.query(Class.classname
								== class_get[0]).fetch()[0]
		theclass = class_get.FAQ

		template_values = {'class': theclass,'classname': classname}
		self.draw(user, template_values)



			

