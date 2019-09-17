# from bs4 import BeautifulSoup

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver import DesiredCapabilities

import smtplib
import math
import time
import sys
import os
import re 

class AmazonBot(object) :
	def __init__(self , wishlist) :
		self.amazon_url = 'https://www.amazon.in/'
		self.wishlist = wishlist

		self.profile = webdriver.FirefoxProfile()

		self.options = Options()
		self.driver = webdriver.Chrome("C:\\Users\\Ganesh\\Downloads\\chromedriver" , 
										chrome_options=self.options)
		self.driver.get(self.amazon_url)

	def search_items(self) : 
		product_details = {}
		for item in self.wishlist : 
			print("item : {}".format(item[0]))
			self.driver.get(self.amazon_url)
			
			search_input = self.driver.find_element_by_id("twotabsearchtextbox")
			search_input.send_keys(item[0])
			
			time.sleep(2)

			search_button = self.driver.find_element_by_xpath('//*[@id="nav-search"]/form/div[2]/div/input')
			search_button.click()

			time.sleep(2)
			i = 0
			count = 0
			while i < 3 and count < 20 :
				result = self.driver.find_element_by_xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[{}]'.format(count+1))
				asin = result.get_attribute("data-asin")
				if asin == '' :
					count += 1
					continue
				url = self.amazon_url + "dp/" + asin
				price = self.get_product_price(url)
				name = self.get_product_name(url)
				print(name , price,'--')
				if price != 'Not available' and price != '' and float(price) < item[1] :
					if name not in product_details :
						product_details[name] = [price , url]
					else :
						if name != 'Not available' and price != 'Not available' and  float(product_details[name][0]) >= float(price) :
							product_details[name] = [price , url]
					i += 1
				count += 1

				self.driver.back()
				time.sleep(2)
		return product_details
		

	def get_product_name(self , url) : 
		self.driver.get(url)
		product_name = None
		try : 
			product_name = self.driver.find_element_by_id("productTitle").text
		except :
			print("Name not found" , url)

		if product_name is None : 
			product_name = 'Not available'

		return product_name


	def get_product_price(self , url) :
		self.driver.get(url)
		price = None
		try : 
			price = self.driver.find_element_by_id("priceblock_ourprice").text
		except :
			pass

		try : 
			price = self.driver.find_element_by_id("priceblock_dealprice").text
		except :
			pass

		if price is None : 
			price = 'Not available'
		else :
			# non_decimal = re.compile(r'[^\d.,]+ ')
			# price = non_decimal.sub('' ,price)
			temp = re.findall(r'[^\d.,]+' , price)
			print(temp)
			if len(temp) == 1 :
				price = price.split(temp[0])[1]
			if len(temp) == 2 :
				price = price.split(temp[0] , 1)[1]
				price = price.split(temp[1])[0]
			if ',' in price :
				price = price.replace(',' ,'')
			print('pr' , price)

		return price


def send_email(product_details , wishlist) :
	with smtplib.SMTP('smtp.gmail.com' , 587) as smtp :
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()

		email_address = 'ganeshgood130y@gmail.com'

		smtp.login( email_address, '')

		subject = 'Amazon Price Report on current WishList'
		body = "The new Offers on \n"
		for product in wishlist :
			body += product[0]+'\n'
		for name in product_details :
			body += name + '\nPrice : ' + product_details[name][0] + '\t\t' + product_details[name][1] + '\n'

		msg = f'Subject : {subject}\n\n{body}'

		smtp.sendmail(email_address , 'yvm10@iitbbs.ac.in' , msg)


if __name__ == '__main__' :
	
	wishlist = []
	
	if os.path.exists('./products.txt') :
		f = open('./products.txt' , 'r')
		products = f.read().split('\n')
		f.close()
	else : 
		print("No WishList")
		exit()
	print(products)
	for product in products :
		temp = product.split('->')
		temp[0] = temp[0].strip()
		if len(temp) == 1 :
			wishlist = [temp[0] , math.inf]
		else :
			temp[1] = int(temp[1].replace(' ' ,''))
			wishlist.append(temp)

	bot = AmazonBot(wishlist)
	product_details = bot.search_items()

	if os.path.exists('./best_products.txt') :
		f = open('./best_products.txt' , 'r') 
		best_prod = f.read().split('\n')
		f.close()
		
		prev_prod_info = {}
		for details in best_prod :
			temp = details.split('----')
			if temp[0] != '' :
				prev_prod_info[temp[0]] = [temp[1] , temp[2]]

		new_best_prod = {}
		for name in product_details :
			if name not in prev_prod_info or (name in prev_prod_info and prev_prod_info[name][0] > product_details[name][0]) :
				new_best_prod[name] = product_details[name]
				prev_prod_info[name] = product_details[name]
			# else :
			# 	new_best_prod[name] = product_details[name]
			# 	prev_prod_info[name] = product_details[name]

		f = open('./best_products.txt', 'w')

		for name in prev_prod_info :
			f.write(name + '----' + prev_prod_info[name][0] + '----' + prev_prod_info[name][1] + '\n')
		f.close()

		send_email(new_best_prod , wishlist)

	else :

		f = open('./best_products.txt', 'w')
		for name in product_details :
			f.write(name + '----' + product_details[name][0] + '----' + product_details[name][1] + '\n')
		f.close()
		
		send_email(product_details, wishlist)