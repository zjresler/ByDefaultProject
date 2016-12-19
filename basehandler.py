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

#interface-esque class?
class BannerStandard():
	def build_banner(self, user):
		#returns string to be passed to jinja2 template
		exit("Instance Method \"create_banner\" undefined!")
	def draw(self, user):
		#outputs html to browser window
		exit("Instance Method \"draw\" undefined!")
class BaseHandler(BannerStandard, webapp2.RequestHandler):
	def error_redirect(self, message_key, path, delay=5):
		template = JINJA_ENVIRONMENT.get_template('./html/error_redirect.html')
		self.response.write(template.render({
			'message':STRINGS[message_key],
			'delay': str(delay),
			'path': path,
			'banner': BANNER_DEFAULT_0 + BANNER_END
		}))
	def success_redirect(self, message_key, path, delay=5):
		template = JINJA_ENVIRONMENT.get_template('./html/success_redirect.html')
		self.response.write(template.render({
			'message':STRINGS[message_key],
			'delay': str(delay),
			'path': path,
			'banner': BANNER_DEFAULT_0 + BANNER_END
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
		
	def build_banner(self, user):
		html_out = BANNER_DEFAULT_0 
		if user != None:
			#html_out = html_out + "Hello, "+user.username+"..."			
			if user.accounttype == ADMIN:
				html_out = html_out + BANNER_INHOME + BANNER_PASTQA
			elif user.accounttype == STUDENT:
				html_out = html_out + BANNER_STHOME + BANNER_PASTQA
			elif user.accounttype == SADMIN:
				html_out = html_out + BANNER_AHOME
			html_out = html_out  + BANNER_VIEW_FAQ + BANNER_LOGOUT
		else:
			html_out = html_out + BANNER_VIEW_FAQ + BANNER_LOGIN
			
		return ( html_out+BANNER_END )
	
class DefaultDraw(BaseHandler):
	template_path_get = ''
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
