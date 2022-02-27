# CODEXBASE
## Crawling

### Technology
- Python 3.9

### Plan

- Learning Technology

The members of the crawling section should know at least the basis of **python programming** and the using of standard libraries like **urllib3** for HTTP requests and **re** for text manipulating. Total mastery of these technologies are not actually required but members should be able to work in using it.
The members should also do personal researches and improve their skills during this period.

- Writing/Building of a prototype (web crawler)

- Test of the prototype on a local website

- Improvement of the prototype and test on a website

- Test of the prototype on Internet

- Writing/Building of the solution

- Test of the solution on Internet

- Maintenance
	NB: After each test, we will proceed to the next step if and only if no occurred errors

### Process

To crawl a website, we will verify if contains a **robots.txt**. After we will connect on it in respecting this **robots.txt**, we will download the HTML contains of each webpage and we will get the URL inside to explore the others webpages of the same website. To evict to make a loop or go out of the website, we will verify before open a link if it has been opened or not and if it is belong the website to crawl. To evit to be detected as a crawler, we will use a delay between each request with a variable value (0.5s-1s) to simulate a human activity.
	NB: The file **robots.txt** is a method used in a website to say to a crawler how to crawl in this website.

### Summary

- Getting links present in a webpage.
 
We can use the regular expression with the module **re**.

- Getting webpages of a website.
 
We can use the HTTP request with the module **urllib3**.

- Using of the file robots.txt while the crawling.

### Notes

- This is an overview plan. We cannot provide a full documentary about something we haven't started because it will have to change depending on the difficulties met when implementing the project itself.

- The full documentary of the process will be written after the project has been implemented.

- Notes will be taken after each step in the plan like problems faced, solutions, etc...

### Notes for indexing team

	While the test of the crawling we have meet

- a problem of duplicate data with different url

	https://example.com/mobile/87356/11:1/ and https://example.com/87356/11:1/
	https://example.com/articles and https://example.com/articles?page=1
	https://example.com/news/ and https://example.com/news

- some empty data

- some html (HTML 5 named and numerica character references e.g. \&gt;, \&#62;, \&x3e;)

	To preserve the speed of the crawling, we will not manage it.



### Developers

- Fody @pythonbrad
- Eddy

### References
https://www.mschweighauser.com/fast-url-parsing-with-python/
https://moz.com/blog/interactive-guide-to-robots-txt
https://docs.python.org/3/library/urllib.robotparser.html