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

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('./html/view.html')
		classes = Class.query().fetch()
		username = ''
		accounttype = ''
		if 'account' in self.session and self.session['account']!='':
			username = self.session.get('account')
			user = User.query(User.username == username).fetch()
			if len(user) == 1:
				accounttype = user[0].accounttype
				
		#added to fix redirect to login when instructor pressed the home button from the faq selection page
		homepath=''
		if accounttype == ADMIN:
			homepath = 'action="/instructorhomepage"'
		elif accounttype == STUDENT:
			homepath = 'action="/studenthomepage"'
		else:
			homepath = 'style="visibility:hidden;"'
			
		template_values = {'class': classes, 'accountname': username, 'homeargs': homepath}
		self.response.write(template.render(template_values))

	def post(self):
		template = JINJA_ENVIRONMENT.get_template('./html/FAQ.html')
		class_get = self.request.get_all('Class')
		classname = class_get[0]
		
		username = ''
		accounttype = ''
		if 'account' in self.session and self.session['account']!='':
			username = self.session.get('account')
			user = User.query(User.username == username).fetch()
			if len(user) == 1:
				accounttype = user[0].accounttype
				
		class_get = Class.query(Class.classname
								== class_get[0]).fetch()[0]
		theclass = class_get.FAQ
#		theclass = Question.query(Question.classUID
#								  == class_get.key).fetch()
		homepath = ''
		if accounttype == 'instructor':
			homepath = 'action="/instructorhomepage" style="visibility:visible;"'
		elif accounttype == 'student':
			homepath = 'action="/studenthomepage" style="visibility:visible;"'
		else:
			homepath = 'style="visibility:hidden;"'
		template_values = {'class': theclass, 'classname': classname, 'homeargs': homepath}
		self.response.write(template.render(template_values))



			

