## Thoughts on reference research
- Automation suggestion - reference crawling
	- Parse the references part of a paper
	- Send each reference text as a query to sgoogle
	- Go to the first result
	- run the Zotero extension on that page to catalogue the article

- Automation suggestion - citation crawling
	- lookup the paper on sgoogle
	- follow the "cited by" link
	- follow each link and run the Zotero extension on the page


- Research strategies
	- Take several articles from the same epoch (a 2-year window) and cluster them by the number of cross references
	- automated keyword extraction by finding words that are found in few other articles
	- find key articles by looking for articles that are referenced directly by their 2nd, 3rd and 4th generation of citations (i.e. even those the article was analyzed later, it was accessed directly)
	- Cluster by minimizing total arc length then performing k-means or dbscan. number of dimensions is a parameter


- Retrieval strategies
	- locate important old articles by the number of their recent citations. then take all the references of these articles several generations forward
	- name a few important current articles and 



