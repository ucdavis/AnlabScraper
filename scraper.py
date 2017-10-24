import requests
from bs4 import BeautifulSoup
import json
import pyodbc

#https://anlab.azurewebsites.net/AdminAnalysis/Create

page = requests.get("http://anlab.ucdavis.edu/using-the-lab/analysis")
soup = BeautifulSoup(page.content, 'html.parser')
# the DSN value should be the name of the entry in odbc.ini, not freetds.conf
#need conn = pyodbc.connect('DSN=Server;UID=userid;PWD=password;DATABASE=database')
crsr = conn.cursor()


def main():
	listNames = soup.find_all('span', class_='summary')

	for names in listNames:
		category = names.get_text()
		print names.a.get('href')
		listData = getCategory(names.a.get('href'), category)
		for i in range(2, len(listData)):
			req(listData[list(listData)[i]])

	
	close()


def close():
	crsr.close()
	conn.close()




def getCategory(categoryLink, category):
	print "CATEGORY: " + categoryLink
	linkPage = requests.get(categoryLink)
	linkSoup = BeautifulSoup(linkPage.content, 'html.parser')
	listNames = linkSoup.find_all('a', class_="contenttype-document state-published url")

	categoryData = {}
	for names in listNames:
		categoryData[names.get_text()] = getData(names.get_text(), names.get('href'))
		categoryData[names.get_text()]["category"] = category.lstrip().rstrip()
		#rint json.dumps(categoryData, indent=1)

	return categoryData

def getData(number, dataLink):
	linkPage = requests.get(dataLink)
	linkSoup = BeautifulSoup(linkPage.content, 'html.parser')
	data = {}

	data["number"] = number
	data["title"] = linkSoup.find(id='parent-fieldname-description')

	if(data["title"]):
		data["title"] = data["title"].get_text().lstrip().rstrip()

	summary = linkSoup.find_all('p')
	summary = summary[:-1]
	data["summary"] = ""
	for line in summary:
		data["summary"] += line.get_text() + "\n"



	return data

def req(lists):
	print(lists)
	crsr.execute("insert into AnalysisMethods(Id, Category, Content, Title) values (?,?,?,?)", lists["number"], lists["category"], lists["summary"], lists["title"])
	crsr.commit()
	rows = crsr.execute("select * from AnalysisMethods").fetchall()
	print(rows)


if __name__ == '__main__': main()