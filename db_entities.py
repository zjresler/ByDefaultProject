import webapp2
import os
from google.appengine.ext import ndb
from google.appengine.ext.ndb import Key
from strings import *
class Category(ndb.Model):
	name = ndb.StringProperty(required=True)
	def unique_put(self, classUID):
		categories = Category.query(Category.name==self.name, ancestor=classUID).fetch()
		if len(categories) == 0:
			return self.put()
		elif len(categories) == 1:
			return categories[0].key
		return 0
class Class(ndb.Model):
	classname = ndb.StringProperty()

	def unique_put(self):
		classes = Class.query(Class.classname == self.classname).fetch()
		if len(classes) == 0:
			return self.put()
		elif len(classes) == 1:
			return classes[0].key
		return 0
		
	@property
	def FAQ(self):
		#return list of questions that are children of this class AND have a category
		return Question.query(Question.category!=None, Question.classUID==self.key).fetch()
		
	@property
	def questions(self):
		return Question.query(Question.classUID==self.key).fetch()
		
	@property
	def categories(self):
		return Category.query(ancestor=self.key).fetch()
		
	@property
	def open_questions(self):
		return Question.query(Question.classUID==self.key, Question.response == None, Question.respondentUID == None).fetch()
class User(ndb.Model):
	username 	= ndb.StringProperty(required=True)
	password	= ndb.StringProperty(required=True)
	lastname	= ndb.StringProperty(required=True)
	firstname	= ndb.StringProperty(required=True)
	email		= ndb.StringProperty(required=True)
	classlist	= ndb.StructuredProperty(Class, repeated=True)
	accounttype	= ndb.StringProperty(required=True)
	
	def unique_put(self):
		users = User.query(User.username == self.username).fetch()
		if len(users) == 0:
			return self.put()
		elif len(users) == 1:
			return users[0].key
		return 0
	def add_class(self, class_):
		classquery = Class.query(Class.classname == class_.classname).fetch()
		if len(classquery) == 1:
			classy = classquery[0]
			self.classlist.append(classy)
			return 1
		return 0
	def reset_classlist(self):
		self.classlist = []
		
	@property
	def questions(self):
		if self.accounttype == ADMIN:
			return Question.query(Question.respondentUID == self.key).fetch()
		elif self.accounttype == STUDENT:
			return Question.query(ancestor=self.key).fetch()
		return []
	
	def questions_of_class(self, classUID):
		if self.accounttype == ADMIN:
			return Question.query(Question.respondentUID == self.key, Question.classUID == classUID).fetch()
		elif self.accounttype == STUDENT:
			return Question.query(Question.classUID == classUID, ancestor=self.key).fetch()
		return []
	@property
	def instructors(self):
		return User.query(User.accounttype == ADMIN).fetch()
		
class Question(ndb.Model):
	respondentUID		= ndb.KeyProperty(User)
#	senderUID			= ndb.KeyProperty(User, required = True)
#	Use parent = senderUID for this field
	classUID			= ndb.KeyProperty(Class, required = True)
	message 			= ndb.StringProperty(required=True)
	response 			= ndb.StringProperty()
	category			= ndb.KeyProperty(Category)
	
	def unique_put(self):
		#keeping so nothing breaks
		return self.put()
		
	def submit_question(self, strict=False):
		#return key on success / 0 on failure
		#ensure the UIDs are actually keys, this may be redundant with ndb
		if self.classUID != None:
			sender = self.key.parent().get()
			class_ = self.classUID.get()
			#ensure the sender is a student
			if sender.accounttype == 'student':
				#calls put, 'submit' the question
				return self.put()
		return 0
	def respond_question(self, user_key, response):
		#return: 1/0
		if self.key != None:
			self.respondentUID = user_key
			self.response = response
			self.put()
			return 1
		else:
			return 0
def FAQ_dict(self):
		#unfinished
		# will organize FAQ entries into dictionary indexed by category
		categories = Category.query(ancestor=classUID).fetch()
		FAQ_by_category = {}
		if categories:
			for category in categories:
				FAQ_by_category[category] = Question.query(Question.category==category.key).fetch()
		return FAQ_by_category
	
		