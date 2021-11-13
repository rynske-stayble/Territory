# coding: UTF-8

import os
import shutil
import math
import re
from urllib.parse import urljoin
from urllib import request
from bs4 import BeautifulSoup


# HottoMotto
response_hottomotto = request.urlopen('https://www.hottomotto.com/menu_list/index/13')
soup_hottomotto = BeautifulSoup(response_hottomotto, 'html.parser')
response_hottomotto.close()

jstab_wrap = soup_hottomotto.find('div', class_='js-tab__wrap')

cmenu__picts = jstab_wrap.find_all('img', class_="c-menu__pict")
cmenu__titles = jstab_wrap.find_all('p', class_="c-menu__title")

for j in range(len(cmenu__titles)):
	cmenu__titles[j] = cmenu__titles[j].text.rstrip('\n')

cmenu__prices = jstab_wrap.find_all('span', class_="c-menu__price")

products = []

for i in range(len(cmenu__titles)):
	products.append({"JAN": "-", "Name": cmenu__titles[i], "Image": "https://www.hottomotto.com" + cmenu__picts[i].get("src"), "Prices": [int((cmenu__prices[i].text).replace(',', ''))], "Places": ["ほっともっと"]})


#Daiso
baseLink = 'https://jp.daisonet.com/collections'
response = request.urlopen(baseLink)
soup = BeautifulSoup(response, 'html.parser')
response.close()

categoryMenu = soup.find('div', class_='mobile-menu__inner')

categoryLinkLines = categoryMenu.find_all('a', class_='mobile-menu__nav-link text--strong')

categoryLinks = []

for category in range(24):
	categoryLinks.append(urljoin(baseLink, categoryLinkLines[category].get("href")))


for categorylink in categoryLinks:
	response = request.urlopen(categorylink)
	soup = BeautifulSoup(response, 'html.parser')
	response.close()

	if soup.find('span', class_='pagination__page-count') is None:
		continue

	pageCount = int(re.findall('(.*)ページ中.ページ目', soup.find('span', class_='pagination__page-count').text)[0])

	for page in range(1, pageCount+1):
		if page == 1 :
			pageLink = categorylink
		else: 
			pageLink = categorylink + '?page=' + str(page)	

		response = request.urlopen(pageLink)
		soup = BeautifulSoup(response, 'html.parser')
		response.close()
	
		productCollection = soup.find('div', class_='product-list product-list--collection product-list--with-sidebar')
		productFrames = productCollection.find_all('div', class_='product-item product-item--vertical 1/3--tablet-and-up 1/4--desk')


		for product in range(len(productFrames)):
			name = (productFrames[product].find('a', class_='product-item__title text--strong link')).text
			if name in [d["Name"] for d in products]:
				continue

			untrimedPrice = productFrames[product].find('div', class_='product-item__price-list price-list').find_all('span', class_='tax')[1].text
			price = int(re.findall('\(税込(.*)円\)', untrimedPrice)[0].replace(',', ''))
	
			untrimedImage = productFrames[product].find('img', class_='product-item__primary-image lazyload image--fade-in')	
			if (untrimedImage != None):
				image = 'https:' + untrimedImage.get("data-src").replace('{width}', '600')
			else:
				image = '-'

			products.append({"JAN": "-", "Name": name, "Image": image, "Prices": [price], "Places": ['ダイソー']})



#htmlファイル群の作成

os.mkdir('html_files')
htmlDir = 'html_files'
shutil.rmtree(htmlDir)
os.makedirs(htmlDir, exist_ok = True)

pageSize = 480
numberOfPages = math.ceil(len(products)/pageSize)

for page in range(numberOfPages):
	pageURL = 'https://jp.territory.com?page=' + str(page+1)
	htmlFile = htmlDir+'seikatsuken_page'+ str(page+1) + '.html'
	
	f = open(htmlFile, mode='w')
	f.write(
		'<!DOCTYPE html>\n'\
		'<html>\n'\
		'<head>\n'\
		'	<meta charset="utf-8">\n'\
		'	<title>Seikatsuken.com</title>\n'\
		'	<link rel="stylesheet" href="../stylesheet_Seikatsuken.css">\n'\
		'	<link rel="canonical" href="' + pageURL + '">\n'\
		'</head>\n'\
		'<header>\n'\
		'	<div class="header-list">\n'\
		'		<ul>\n'\
		'		        <li>閲覧履歴</li>\n'\
		'			<li>ログイン</li>\n'\
		'		</ul>\n'\
		'	</div>\n'\
		'</header>\n'\
		'<div class="top-wrapper">\n'\
		'	<h1 class="title">東大生のための生活圏<span>.</span>com</h1>\n'\
		'	<p class="discription">身の回りで売られている商品とその価格が一瞬で把握できます。</p>\n'\
		'	<p>検索エリア（駅名）</p>\n'\
		'	<input class=\'searching-area\'>\n'\
		'	<input class=\'search-button\' type=\'submit\' value=\'search\'>\n'\
		'</div>\n'\
		'<script>\n'\
		'\n'\
		'	let jan;\n'\
		'	let names;\n'\
		'	let prices;\n'\
		'	let images;\n'\
		'\n'\
		'	const searchingArea = document.querySelector(\'.searching-area\');\n'\
		'	const searchButton = document.querySelector(\'.search-button\');\n'\
		'\n'\
		'	searchingArea.focus()\n'\
		'\n'\
		'	function checkLocation() {\n'\
		'		let inputLocation = String(searchingArea.value);\n'\
		'\n'\
		'		alert(\'位置情報の使用を許可しますか？\');\n'\
		'\n'\
		'	}\n'\
		'\n'\
		'	searchButton.addEventListener(\'click\', checkLocation);\n'\
		'\n'\
		'</script>\n'\
		'<div class="contents">\n'\
		'	<h3 class="product-list">商品一覧</h3>\n'\
	)

	if page == numberOfPages-1:
		for product in range(page*pageSize, len(products)):
			f.write('		<div class="contents-item">\n'\
			'			<img src="' + products[product]["Image"] + '" width="auto" height="200px">\n'\
			'			<p class="product-name">' + products[product]["Name"] + '</p>\n'\
			'			<p class="place-price">' + products[product]["Places"][0] + ':  ' + str(products[product]["Prices"][0]) + '円(税込)</p>\n'\
			'		</div>\n')	

	else:
		for product in range(page*pageSize, (page+1)*pageSize):
			f.write('		<div class="contents-item">\n'\
			'			<img src="' + products[product]["Image"] + '" width="auto" height="200px">\n'\
			'			<p class="product-name">' + products[product]["Name"] + '</p>\n'\
			'			<p class="place-price">' + products[product]["Places"][0] + ':  ' + str(products[product]["Prices"][0]) + '円(税込)</p>\n'\
			'		</div>\n')
		
	f.close()
