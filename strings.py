STRINGS = {
	'INVALID_LOGIN_STATE': 'You are not logged in or your login session is invalid.',	#invalid login message
	'CLASS_NOT_FOUND': 'The class selected was not found. Please contact your instructor or a system administrator if this issue persists.', #invalid classname message
	'QSUBMIT_FAIL': 'There was an error submitting you question.', #ambiguous question submit error message
	'QSUBMIT_SUCCESS': 'Question Submitted Successfully!',	#question submit successful message
	'QKEY_CORRUPT':	'The question key is corrupt.', #bad question key message
	'RSUBMIT_FAIL': 'There was an unexpected error submitting the response.', #response submit failure message
	'RSUBMIT_SUCCESS': 'Response submitted successfully!', #response submit success message
	'DSUBMIT_SUCCESS': 'Data was submitted successfully!',
	'DSUBMIT_NO_SELECTION': 'You did not select a user to edit.',
	'DSUBMIT_NO_CLASS_SELECTED': 'No class was selected.',
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
	<img id="bannerimg" src="/texture/banner.png" alt="banner image">
	<h1 id="SysName">By Default</h1>
	<div class=\"bannerArea\">
	
	
	<table id = "bannerTable" ><tr>
""" #add greeting with accountname after this string
BANNER_LOGOUT = """
	<td><form action="/logout" method="GET"><input type="submit" value="Logout"></form></td>
"""
BANNER_LOGIN = """
	<td><form action="/" method="GET"><input type="submit" value="Login"></form></td>
"""
BANNER_VIEW_FAQ = """
	<td><form action="/faq" method="GET"><input class="bannerButton" type="submit"  value="View FAQ"></form></td>
"""
BANNER_PASTQA ="""
	<td><form action="/PastQA" method="GET"><input class="bannerButton" type="submit" value="View Questions"></form></td>
"""
BANNER_STHOME ="""
	<td><form action="/studenthomepage" method="GET"><input type="submit" value="Home"></form></td>
"""
BANNER_INHOME = """
	<td><form action="/instructorhomepage" method="GET"><input type="submit" value="Home"></form></td>
"""
BANNER_AHOME = """
	<td><form action="/registrationhomepage" method="GET"><input type="submit" value="Home"></form></td>
"""
BANNER_END = """</tr></table></div>
"""