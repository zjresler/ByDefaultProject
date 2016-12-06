import webapp2
import os
import jinja2

from strings import *
from db_entities import *

from google.appengine.ext import ndb
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class BaseHandler(webapp2.RequestHandler):
	def error_redirect(self, message_key, path, delay=2):
		template = JINJA_ENVIRONMENT.get_template('./html/error_redirect.html')
		self.response.write(template.render({
			'message':STRINGS[message_key],
			'delay': str(delay),
			'path': path
		}))
		
	def success_redirect(self, message_key, path, delay=2):
		template = JINJA_ENVIRONMENT.get_template('./html/success_redirect.html')
		self.response.write(template.render({
			'message':STRINGS[message_key],
			'delay': str(delay),
			'path': path
		}))
	def validate_user(self, accountname, accounttype=''):
		if accountname != '':
			user = User.query(User.username == accountname).fetch()
			if len(user) == 1:
				user=user[0]
				if accounttype !='': #check accounttype needs to be checked aswell
					if user.accounttype != accounttype: #check that the accounttype is correct
						return False #accounttype was not correct
				return True
				
		return False
		
	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()