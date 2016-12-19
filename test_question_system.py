import webapp2
import os
import jinja2
import unittest 
import HTMLTestRunner
import time

import main

#from main import TEST_OUT
from question_system import *
from registration import *
from db_entities import *
from basehandler import BaseHandler
from strings import *
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
from google.appengine.ext.webapp import Response
from StringIO import StringIO
from google.appengine.ext.ndb import Key

from webapp2_extras import sessions
from webapp2_extras.securecookie import SecureCookieSerializer

JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class QuestionTests(unittest.TestCase):
	def setUp(self):
		self.student = User(
			username = 'student_test',
			password = 'student',
			firstname = 'student',
			lastname = 'student',
			email = 'student', 
			accounttype = STUDENT
		)
		self.instructor = User(
			username = 'instructor_test',
			password = 'instructor',
			firstname = 'instructor',
			lastname = 'instructor',
			email = 'instructor',
			accounttype = ADMIN
		)
		self.admin = User(
			username = 'admin_test',
			password = 'admin',
			firstname = 'admin',
			lastname = 'admin',
			email = 'admin',
			accounttype = SADMIN
		)
		#create a test class
		self.classy = Class(classname = 'TESTCLASS_test')
		self.class_key = self.classy.put()
		time.sleep(2)
		
		#add class to classlists
		self.student.add_class(self.classy)
		self.instructor.add_class(self.classy)
		self.admin.add_class(self.classy)
		
		#put the users
		self.student_key = self.student.put()
		self.instructor_key = self.instructor.put()
		self.admin_key = self.admin.put()
		time.sleep(2)
		
		#create the questions
		self.q00 = Question(
			parent = self.student_key,
			classUID = self.class_key,
			message = 'What is the air speed velocity of a swallow?'
		)
		self.q01 = Question(
			parent = self.student_key, 
			classUID = self.class_key, 
			message = 'What is your favorite color?'
		)
		self.q02 = Question(
			parent = self.student_key, 
			classUID = self.class_key, 
			message = 'What is your quest?'
		)
		self.q00_key = self.q00.put()
		self.q01_key = self.q01.put()
		self.q02_key = self.q02.put()
		time.sleep(2)
		
		#create response handler object
		self.respond = ResponseHandler()
		self.ask = QuestionHandler()
	
	def tearDown(self):
		self.student_key.delete()
		self.instructor_key.delete()
		self.admin_key.delete()
		self.class_key.delete()
		self.q00_key.delete()
		self.q01_key.delete()
		self.q02_key.delete()
		time.sleep(2)
		
		del self.admin
		del self.admin_key
		del self.instructor
		del self.instructor_key
		del self.student
		del self.student_key
		
		del self.classy
		del self.class_key
		
		del self.q00
		del self.q00_key
		del self.q01
		del self.q01_key
		del self.q02
		del self.q02_key
		
		del self.respond
		del self.ask
		
	def test_instructor_can_respond(self):
		respond = ResponseHandler()
		session = {
			'account': self.instructor.username,
			'accounttype': ADMIN,
			'class': self.classy.classname,
			'question_key': self.q00_key.urlsafe(),
		}
		
		secure_cookie_serializer = SecureCookieSerializer(SECRET_KEY)
		serialized = secure_cookie_serializer.serialize('session', session)
		headers = {'Cookie':'session=%s' % serialized}
		
		respond.request = Request.blank('/respond?response=test')
		respond.request.method='POST'
		#respond.request.body = 'response=test'
		respond.request.headers=headers
		#print '\n'+respond.request.get('message')+'\n'
		
		self.assertTrue(respond.request.get('response') == 'test')
		
		response = respond.request.get_response(main.app)
		time.sleep(2)
		#message = response.get('message')
		question = self.q00
		self.assertFalse(question == None)
		self.assertFalse(question.respondentUID == None)
		self.assertFalse(question.response == None)
		self.assertFalse(question.response == '')
		self.assertTrue(question.respondentUID == self.instructor.key)
		self.assertTrue(question.response == 'test')

	def test_instructor_can_create_new_category(self):
		
		qkey = self.q00_key
		respond = ResponseHandler()
		session = {
			'account': self.instructor.username,
			'accounttype': ADMIN,
			'class': self.classy.classname,
			'question_key': qkey.urlsafe(),
		}
		secure_cookie_serializer = SecureCookieSerializer(SECRET_KEY)
		serialized = secure_cookie_serializer.serialize('session', session)
		headers = {'Cookie':'session=%s' % serialized}
		respond.request = Request.blank('/respond?add_to_category=1&response=test&cname=Default&new_cname=test_category')
		respond.request.method='POST'
		respond.request.headers=headers
		
		#ensure that the vars were passed to test properly
		self.assertTrue(respond.request.get('response') == 'test')
		self.assertTrue(respond.request.get('new_cname') == 'test_category')
		
		temp = Category.query(Category.name=='test_category').fetch()
		for c in temp:
			c.key.delete()
		del temp
		
		response = respond.request.get_response(main.app)
		
		time.sleep(2)
		category = Category.query(Category.name == 'test_category').fetch()
		
		self.assertTrue(len(category)==1) #was created and is unique, also has the correct name
		category = category[0]
		self.assertTrue(category.key.parent() == self.classy.key)
		category.key.delete()
	
	def test_instructor_can_set_category_to_answer(self):
		qkey = self.q00_key
		respond = ResponseHandler()
		session = {
			'account': self.instructor.username,
			'accounttype': ADMIN,
			'class': self.classy.classname,
			'question_key': qkey.urlsafe(),
		}
		secure_cookie_serializer = SecureCookieSerializer(SECRET_KEY)
		serialized = secure_cookie_serializer.serialize('session', session)
		headers = {'Cookie':'session=%s' % serialized}
		respond.request = Request.blank('/respond?add_to_category=1&response=test&cname=test_category')
		respond.request.method='POST'
		respond.request.headers=headers
		
		#ensure that the vars were passed to test properly
		self.assertTrue(respond.request.get('response') == 'test')
		self.assertTrue(respond.request.get('cname') == 'test_category')
		
		temp = Category.query(Category.name == 'test_category').fetch()
		for c in temp:
			c.key.delete()
		del temp
		
		response = respond.request.get_response(main.app)
		
		time.sleep(2)
		question = qkey.get()
		cate = Category.query(Category.name == 'test_category').fetch()
		self.assertTrue(len(cate)==1) #was created/found and is unique, also has the correct name
		cate = cate[0]
		self.assertTrue(question.category == cate.key)
		question.key.delete()
		cate.key.delete()
	
	def test_instructor_can_respond_with_faq(self):
		
		
		qkey = self.q00_key
		
		respond = ResponseHandler()
		session = {
			'account': self.instructor.username,
			'accounttype': ADMIN,
			'class': self.classy.classname,
			'question_key': qkey.urlsafe(),
		}
		secure_cookie_serializer = SecureCookieSerializer(SECRET_KEY)
		serialized = secure_cookie_serializer.serialize('session', session)
		headers = {'Cookie':'session=%s' % serialized}
		respond.request = Request.blank('/respond?response=test&infaq=infaq')
		respond.request.method='POST'
		respond.request.headers=headers
		
		self.assertTrue(respond.request.get('response') == 'test')
		self.assertTrue(respond.request.get('infaq') == 'infaq')
		response = respond.request.get_response(main.app)
		
		time.sleep(2)
		
		question = qkey.get()
		self.assertTrue(question.response == R_INFAQ)
	
	def test_questions_in_FAQ_have_category(self):
		temp = self.classy.FAQ
		for q in temp:
			q.key.delete()
		del temp
		
		#create a category and put it to the DB
		cate = Category(name="test category 00", parent=self.classy.key)
		
		
		
		
		#update the category of q00
		self.q00.category = cate.put()
		self.q00.put()
		
		time.sleep(2)
		
		
		
		#get all of the questions in the FAQ of classy
		#	ie. all of the questions with a classUID of classy's key
		#	and who have any category
		#	faq is a list
		faq = self.classy.FAQ
		
		self.assertTrue(faq!=None)
		self.assertTrue(len(faq)==1)
		self.assertTrue(faq[0].key == self.q00_key)
		
		cate.key.delete()
	
	def test_questions_not_in_FAQ_have_no_category(self):
		temp = self.classy.FAQ
		for q in temp:
			q.key.delete()
		del temp
		
		#create a category and put it to the DB
		cate = Category(name="test category 01", parent=self.classy.key)
		
		
		#update the category of q00
		self.q00.category = cate.put()
		self.q00.put()
		
		time.sleep(2)
		
		#questions not in the FAQ will NOT have their category field set
		all_questions = Question.query().fetch()
		not_faq = Question.query(Question.category==None).fetch()
		faq = self.classy.FAQ
		
		for q in faq:
			self.assertTrue(q.category!=None)
			self.assertFalse(q in not_faq)
			self.assertTrue(q in all_questions)
		
		for q in not_faq:
			self.assertTrue(q.category==None)
			self.assertFalse(q in faq)
			self.assertTrue(q in all_questions)
		
		cate.key.delete()
	
	def test_unanswered_questions_have_no_category(self):
		
		questions = [None]*100
		for i in range(100):
			questions[i] = Question(parent=self.student.key, classUID = self.classy.key, message = 'This is an unanswered question?').put()
			
		time.sleep(2)
		for q in questions:
			self.assertTrue(q.get().category==None)
			q.delete()
	
	def test_question_submit_wrapper(self):
		self.ask.submit_question_wrapper(self.student.username, self.student.accounttype, self.classy.classname, 'foo is a question?')
		time.sleep(2)
		question = Question.query(Question.message=='foo is a question?').fetch()
		self.assertTrue(len(question)==1)
		question = question[0]
		self.assertTrue(question.key.parent() == self.student_key)
		self.assertTrue(question.message == 'foo is a question?')
		self.assertTrue(question.respondentUID == None)
		self.assertTrue(question.classUID == self.class_key)
		question.key.delete()
	def test_datastore_key(self):
		cate = Category(name='test')
		self.assertTrue(cate.key == None)
		cate_key = cate.put()
		self.assertTrue(cate.key == cate_key)
		self.assertTrue(cate.key != None)
		cate_key.delete()
	def test_datastore_key_2(self):
		thing = self.admin_key.urlsafe()
		radmin = Key(urlsafe=thing).get()
		self.assertFalse(radmin.key==None)
		self.assertTrue(radmin.key == self.admin.key)
		
	def test_bad_address(self):
		self.assertTrue(Register().make_mail_message(subject = 'test', body = 'test', sender ='test', to='test') == None)
	def test_invalid_address1(self):
		self.assertTrue(Register().make_mail_message(subject = 'test', body = 'test', sender ='test', to='test@googles') == None)
	def test_invalid_address2(self):
		self.assertTrue(Register().make_mail_message(subject = 'test', body = 'test', sender ='test', to='test.com') == None)
	def test_valid_address(self):
		self.assertTrue(Register().make_mail_message(subject = 'test', body = 'test', sender ='test', to='test@gmail.com')!= None)
	
"""
	def _test_question_submit_student(self):
		self.assertTrue(False)
	
	def test_student_can_enter_a_code_to_join_class(self):
		self.assertTrue(False)
	
	def test_incorrect_code_gives_error(self):
		self.assertTrue(False)
	
	def test_students_can_edit_account_info(self):
		self.assertTrue(False)
	
	def test_instructor_can_create_student_accounts(self):
		self.assertTrue(False)
	
	def test_instructor_can_edit_FAW(self):
		self.assertTrue(False)
	
	def test_student_can_view_FAQ(self):
		self.assertTrue(False)
	
	def test_else_can_view_FAQ(self):
		self.assertTrue(False)
	
	def test_student_can_view_their_prev_questiosn(self):
		self.assertTrue(False)
	
	def test_instructor_can_view_their_prev_questions(self):
		self.assertTrue(False)
	
	def test_admin_can_create_instructor(self):
		self.assertTrue(False)
	
	def test_admin_can_create_student(self):
		self.assertTrue(False)
	
	def test_instructor_can_batch_create_student_accounts(self):
		self.assertTrue(False)
"""
class FakeFile():
	data = ''
	def write(self, str):
		self.data = self.data+str
	
suite = unittest.TestLoader().loadTestsFromTestCase(QuestionTests)
#outfile = ''#open(os.path.join(os.path.dirname(__file__), 'test_output.html'), 'w')
#unittest.TextTestRunner(verbosity=2).run(suite)
runner = HTMLTestRunner.HTMLTestRunner(
	stream=FakeFile(),
	title='Test Results',
	description='Test output for question_system.'
)
