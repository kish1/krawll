# krawll
Web crawling made easy. Just supply extractor and terminator functions to this higher-order function and let krawll do the rest.

# How to use krawll

Supply the following to the krawll function:

1. *Extractor* - Parses and extracts the required data from the HTML and returns the data as a dictionary.

2. *Terminator* - The crawler terminates when this function returns True.

_krawll(cookies, homepage, hostname, extractor, terminator)_

# Example

```python
# heading_extractor: String -> Dict
# GIVEN: a html source tree
# RETURNS: a data structure containing newly extracted data
# an empty list otherwise.
def heading_extractor(html):
	import BeautifulSoup
	soup = BeautifulSoup(html)
	h1s = soup.find_all('h1')
	hits = []
	for tag in h1s:
		str_tag = str(tag)
		if str_tag.startswith('<h1 class="headlines" style="color:blue">Breaking News: '):
			hits.append(str(tag.string).split('FLAG: ')[1])
	news = {}
	for hit in hits:
		if not news.has_key(hit):
			news[hit] = 1
	return new


# may_exit: Dict -> Boolean
# GIVEN: a data structure containing the extracted data
# RETURNS: True if the required number of hits have been found, False otherwise.
# This implies that the crawler will terminate when this function returns True.
def may_exit(news):
	return len(news) == 20
	
# never_exit: Dict -> Boolean
# GIVEN: a data structure containing the extracted data
# RETURNS: False. This implies that the crawler will crawl the entire domain.
def never_exit(news):
	False


import krawll
cookies = {}
home_page = 'http://www.xyznews.com'
host = 'www.xyznews.com'
news_dict = krawll.krawll(cookies, home_page, host, heading_extractor, may_exit)
```
