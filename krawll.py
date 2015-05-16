# Python Version: 2.7


import sys
import socket
import urlparse
from bs4 import BeautifulSoup


# GLOBAL CONSTANTS
CRLF = '\r\n'


# HEADER NAMES
HEADER_HOST = 'Host: '
HEADER_LOCATION = 'Location: '
HEADER_SET_COOKIE = 'Set-Cookie: '
HEADER_COOKIE = 'Cookie: '
HEADER_CONTENT_LENGTH = 'Content-Length: '
HEADER_CONNECTION = 'Connection: '
HEADER_KEEP_ALIVE = 'Keep-Alive: '


# __status_code__: String -> String
# GIVEN: a raw string carrying the response to a http request
# RETURNS: the status code of the response as a string
def __status_code__(http_response):
	headers = http_response.split(CRLF + CRLF)[0]
	headers = headers.split(CRLF)
	return headers[0].split(' ')[1]


# __header_value__: String, String -> String
# GIVEN: a raw string carrying the response to a http request and
# a header string
# RETURNS: the value corresponding to the header string if it is
# present, the empty string otherwise
def __header_value__(http_response, header_string):
	headers = http_response.split(CRLF + CRLF)[0]
	headers = headers.split(CRLF)
	for header in headers:
		if header.startswith(header_string):
			return header.partition(header_string)[2]
	return ''


# __header_value_multiple__: String, String -> List<String>
# GIVEN: a raw string carrying the response to a http request and
# a header string
# RETURNS: the list of values corresponding to the header string if it is
# present, the empty list otherwise

def __header_value_multiple__(http_response, header_string):
	headers = http_response.split(CRLF + CRLF)[0]
	headers = headers.split(CRLF)
	values = []
	for header in headers:
		if header.startswith(header_string):
			values.append(header.partition(header_string)[2])
	return values


# __set_cookies__: String -> Dict{cookie_name, value}
# GIVEN: a raw http response string
# RETURNS: a dictionary containing the name, value pairs extracted from
# the header field 'Set-Cookie'
def __set_cookies__(http_response):
	set_cookies =  __header_value_multiple__(http_response, HEADER_SET_COOKIE)
	if set_cookies == []:
		return None
	return set_cookies


# HEADER EXTRACTORS: String -> String
# GIVEN: a http response string
# RETURNS: the value corresponding to the header suggested by the
# function name

def __location__(response_30x):
	return __header_value__(response_30x, HEADER_LOCATION)


def __connection__(http_response):
	return __header_value__(http_response, HEADER_CONNECTION)


def __keep_alive__(http_response):
	return __header_value__(http_response, HEADER_KEEP_ALIVE)


# get_cookies: String -> Dict{cookie_name, value}
# GIVEN: a http response string
# RETURNS: a dictionary representing the cookies extracted from the response
def get_cookies(http_response):
	cookies = __set_cookies__(http_response)
	if cookies == None:
		return None
	return dict(map(lambda x: x.split(';')[0].split('='), cookies))


# merge_cookies: Dict{cookie_name, value}, Dict{cookie_name, value} ->
# Dict{cookie_name, value}
# GIVEN: two dictionaries containing cookies
# RETURNS: a dictionary containing the 
def merge_cookies(current, new):
	if current == None:
		return new
	if new == None:
		return current
	copy_of_current = current.copy()
	copy_of_current.update(new)
	return copy_of_current


# make_cookie_header: Dict{cookie_name, value} -> String
# GIVEN: a dictionary containing cookies
# RETURNS: the given cookies transformed into the 'Cookie' header format
def make_cookie_header(cookies):
	if cookies == None:
		return ''
	header_value = []
	for key, value in cookies.items():
		header_value.append(key + '=' + value)
	header_value = reduce(lambda x,y: x+';'+y, header_value)
	return HEADER_COOKIE + header_value + CRLF


# make_content_length_header: Integer -> String
# GIVEN: a value for content length
# RETURNS: a formatted header for the same
def make_content_length_header(content_length):
	return HEADER_CONTENT_LENGTH + content_length + CRLF


# make_host_header: String -> String
# GIVEN: a URL
# RETURNS: a formatted header for the host address extracted from the
# given URL
def make_host_header(url):
	header_value = parse_port(urlparse.urlparse(url).netloc)[0]
	return HEADER_HOST + header_value + CRLF


# make_connection_header: String -> String
# GIVEN: a value for the connection type
# RETURNS: a formatted header for the same
def make_connection_header(connection_type):
	return HEADER_CONNECTION + connection_type + CRLF


# make_post_headers: String, Dict{cookie_name, value}, String -> String
# GIVEN: a URL, a dictionary containing cookies and a payload string
# RETURNS: a string containing the  headers necessary for a POST request
# using the given data
def make_post_headers(url, cookies, payload):
	headers = []
	headers.append(make_cookie_header(cookies))
	headers.append(make_content_length_header(str(len(payload))))
	headers.append(make_host_header(url))
	return reduce(lambda x,y: x+y, headers) + CRLF


# make_get_headers: String, Dict{cookie_name, value} -> String
# GIVEN: a URL and a dictionary containing cookies
# RETURNS: the headers in format appended with CLRF
def make_get_headers(url, cookies):
	return make_cookie_header(cookies) + make_host_header(url) + CRLF


# url_encode_char: String -> String
# GIVEN: a single-character string
# RETURNS: the url encoding for the given character
def url_encode_char(char):
	if char.isalnum() or char in ['*', '-', '.', '_']:
		return char
	return '%' + hex(ord(char.encode('UTF-8').encode('ASCII')))[2:].upper()


# url_encode: String -> String
# GIVEN: a string
# RETURNS: the given string url encoded(quoted)
def url_encode(string):
#	print('url_encode:' + string)
	return reduce(lambda x,y: x+y, map(lambda x: url_encode_char(x), string))


# url_decode: String -> String
# GIVEN: an encoded URL
# RETURNS: the given URL decoded
def url_decode(encoded_url):
	decoded = ''
	en = encoded_url
	en_len = len(en)
	i = 0
	while i < en_len:
		if en[i] == '%':
			hex_value = '0x' + en[i+1 : i+3]
			decoded += chr(int(hex_value, 16))
			i += 3
		else:
			decoded += en[i]
			i += 1
	return decoded


# hidden_parameters: String -> [String, String]
# GIVEN: a html source tree
# RETURNS: a list containing [name, value] pairs of the <input> tags
# with type="hidden"
def hidden_parameters(html):
	soup = BeautifulSoup(html)
	input_tags = soup.find_all('input', type='hidden')
	return map(lambda x: [x['name'], x['value']], input_tags)


# parameters_encoded: List<[String, String]> -> List<[String, String]>
# GIVEN: encoded parameters
# RETURNS: the given parameters decoded
def parameters_encoded(params):
	return map(lambda x: [x[0], url_encode(x[1])], params)


# make_post_payload: List<[String, String]>
# GIVEN: key,value pairs as parameters to a POST request
# RETURNS: a payload constructed from the given data
def make_post_payload(parameters):
	parameters = map(lambda x: x[0]+'='+x[1], parameters_encoded(parameters))
	return reduce(lambda x,y: x+'&'+y, parameters) + CRLF


# get_path: String -> String
# GIVEN: a URL
# RETURNS: the server path present in the URL
def get_path(url):
	return urlparse.urlparse(url).path


# post_path: String, String -> String
# GIVEN: a string containing html and the base url
# RETURNS: the path for the request line of the POST request.
def post_path(html, base_url):
	soup = BeautifulSoup(html)
	form = soup.find('form', method='post')
	return get_path(urlparse.urljoin(form['action'], base_url))



# tcp_socket: String, String -> socket
# GIVEN: a hostname and a port number
# RETURNS: a tcp socket bound to the given hostname and port
def tcp_socket(hostname, port):
	s = socket.socket()
	try:
		s.connect((socket.gethostbyname(hostname), int(port)))
	except socket.error as se:
	 	print('Exception caught: Socket Error' + str(se))
	 	sys.exit(1)
	return s


# parse_port: String -> (String, String)
# GIVEN: a hostname
# RETURNS: a 2-tuple (host, port). 'host' is the network host address
# of the given hostname. If the port number was appended to the given 
# hostname, then 'port' is extracted from it, else 'port' defaults to '80'.
def parse_port(hostname):
	parsed_hn = hostname.split(':')
	if len(parsed_hn) > 1:
		return tuple(parsed_hn)
	return (hostname, '80')


# internet_address: String -> String
# GIVEN: a URL
# RETURNS: the host address of the given URL
def internet_address(url):
	return (urlparse.urlparse(url).netloc, '80')


# get: String -> String
# GIVEN: a URL
# RETURNS: the raw http response to a GET request sent to the given URL
def get(url, cookies):
	host, port = internet_address(url)

	request_line = 'GET ' + url + ' HTTP/1.0' + CRLF
	headers = make_get_headers(url, cookies)
	request = request_line + headers + CRLF

	sock = tcp_socket(host, port)
	sock.send(request)

	message = ''
	response = None
	buffer_length = 2048

	while response != '':
		response = sock.recv(buffer_length)
		message = message + response

	status_code = __status_code__(message)

	if status_code == '200':
		return message
	elif status_code in ['301', '302', '303']:
		new_url = get_location(message)
		return get(new_url, merge_cookies(cookies, get_cookies(message)))
	elif status_code in ['401', '403', '404']:
		return ' abandon'
	elif status_code == '400':
		return ' badrequest'
	elif status_code == '500':
#		print('Internal Server Error')
		return get(url, cookies)
		
	return ''


# get_location: String -> String
# GIVEN: a http response
# RETURNS: the location specified in its headers
def get_location(http_response):
	return url_decode(__location__(http_response)).split(CRLF)[0]


# post: String, String, Dict{cookie_name, value}, String -> String
# GIVEN: a URL, the path for the request line, a dictionary containing cookies
# and a payload string
# RETURNS: a raw string containing the http response to a POST request constructed
# from the given data
def post(url, path, cookies, payload):
	request_line = 'POST ' + path + ' HTTP/1.0' + CRLF
	headers_line = make_post_headers(url, cookies, payload)
	request = request_line + headers_line + payload

	host, port = internet_address(url)
	s = tcp_socket(host, port)
	s.send(request)

	message = ''
	buffer = None
	while buffer != '':
		buffer = s.recv(4096)
		message += buffer

	status_code = __status_code__(message)

	if status_code in ['301', '302', '303']:
		new_path = get_location(message)
		return get(new_path, merge_cookies(cookies, get_cookies(message)))
	elif status_code in ['401', '403', '404']:
		return 'abandon post: ' + status_code
	elif status_code == '400':
		return 'bad request'
	elif status_code == '500':
		pass
#		print('Internal Server Error')
	elif status_code == '200':
		print('Login unsuccessful')
		exit(0)
		return post(url, path, merge_cookies(cookies, get_cookies(message)), payload)

	return ''


# link_within_domain: String, String -> Boolean
# GIVEN: a host address and a URL
# RETURNS: True if and only if the given URL is within the given domain
def link_within_domain(host, link):
	return urlparse.urlparse(link).netloc == host


# get_abs_url: String, String -> String
# GIVEN: a host address and a relative URL
# RETURNS: a canonical URL constructed from the given data
def get_abs_url(host, rel_link):
	return urlparse.urlunparse(('http', host, rel_link, '', '', ''))


# scrape_all_links: String -> List<String>
# GIVEN: a string containing html
# RETURNS: a list of all hyperlinks present in the given html string
def scrape_all_links(html):
	return filter(lambda x: x.startswith('/'), map(lambda x: x['href'], BeautifulSoup(html).find_all('a')))


# krawll: Dict{cookie_name, value}, String, String, Function, Function -> Dict
# GIVEN: a dictionary containing cookies, the home page of the website, a function to extract
# the required data and a function that returns whether or not the crawler needs to stop at 
# that point in time
# extractor: String -> Dict
# terminator: Dict -> Boolean
# RETURNS: the data collected by the extractor function
def krawll(cookies, home_page, host, extractor, terminator):
# Traversal algorithm: BFS
	
	queue = []
	visited = set()
	data_extracted = {}
	
	current_page = home_page
	current_link = 'no idea'
	abandon = False
	while True:
		visited.add(current_link)
		if not abandon:
			data_extracted.update(extractor(current_page))
			if terminator(data_extracted):
				break
			links = map(lambda x: get_abs_url(host, x), scrape_all_links(current_page))
			
			for link in links:
				if link_within_domain(host, link) and (link not in visited) and (link not in queue):
					queue.append(link)
		abandon = False
		if len(queue) == 0:
			return data_extracted

		current_link = queue.pop(0)

		current_page = get(current_link, cookies)
		status = __status_code__(current_page)
		if status == 'abandon':
			abandon = True
		elif status == 'badrequest':
			print(status)
		   	return None
		elif status == '200':
			continue
		else:
			return None
			
	return data_extracted

