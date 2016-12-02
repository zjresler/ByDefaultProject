STRINGS = {
	'INVALID_LOGIN_STATE': 'You are not logged in or your login session is invalid.',	#invalid login message
	'CLASS_NOT_FOUND': 'The class selected was not found. Please contact your instructor or a system administrator if this issue persists.', #invalid classname message
	'QSUBMIT_FAIL': 'There was an error submitting you question.', #ambiguous question submit error message
	'QSUBMIT_SUCCESS': 'Question Submitted Successfully!',	#question submit successful message
	'QKEY_CORRUPT':	'The question key is corrupt.', #bad question key message
	'RSUBMIT_FAIL': 'There was an unexpected error submitting the response.', #response submit failure message
	'RSUBMIT_SUCCESS': 'Response submitted successfully!', #response submit success message
}
#account types
ADMIN	= 'instructor'	#instructor accounttype string
STUDENT = 'student'		#student accounttype string
SADMIN	= 'admin'		#super admin accounttype string	

#session indicies		really wish python had a const modifier...
ACCT_T	= 'accounttype' #string that is used in the session dictionsry to retrieve the accounttype
ACCT_N	= 'account'		#string that is used in the session dictionary to retrieve the username
CLAS_N = 'class'		#string that is used in the session dictionary to retrieve the classname
QUES_K = 'question_key'	#string that is used in the session dictionary to retrieve the question key (urlsafe)
MESSAGE = 'message'

#other
SECRET_KEY = 'my-super-secret-key'	#string used to serialize teh session data or something
R_INFAQ = 'This question is already answered in the FAQ. Please look in the FAQ for the answer to your question. Always check the FAQ before asking a question to save yourself the time of waiting for a response.' #default "ITS IN THE FAQ!" response
F_TEST_OUT = './html/test_output.html' #this isnt used because gae is poo

#banner parts
BANNER_DEFAULT_0 = """
	<h1 id="SysName">By Default</h1>
	<div class=\"bannerArea\">
""" #add greeting with accountname after this string
BANNER_LOGOUT = """
	<form action="/logout" method="GET"><input type="submit" value="Logout"></form>
"""
BANNER_VIEW_FAQ = """
	<form action="/faq" method="GET"><input class="bannerButton" type="submit"  value="View FAQ"></form>
"""
BANNER_PASTQA ="""
	<form action="/PastQA" method="GET"><input class="bannerButton" type="submit" value="View Questions"></form>
"""
BANNER_STHOME ="""
	<form action="/studenthomepage" method="GET"><input type="submit" value="Home"></form>
"""
BANNER_INHOME = """
	<form action="/instructorhomepage" method="GET"><input type="submit" value="Home"></form>
"""
BANNER_END = """</div>
"""