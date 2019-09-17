# Amazon-web-Scraper

Requirements libraries :
Selenium (with chrome driver downloaded and installed to scrape the web)
smtplib  (for sending emails)
math 
time    (for time)
re     (regular expressions)
os     (file extracton)

The input file products.txt contains the product you want to buy and the maximum price you want to pay.
You can run the code by 

python webscrape.py

The code using selenium goes to https://amazon.in and searches for the wish list with in the given prices.
The top 3 search results are taken and sends an email along with links to the given email in send_email() function.
If the search results change or the same product is at low price then an email is sent if this code is hosted
on a server and ran at a certain interval. The results are also stored in best_products.txt
