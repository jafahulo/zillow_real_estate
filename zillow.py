from lxml import html
import requests
import unicodecsv as csv
import argparse

def parse(zipcode,filter=None):

	if filter=="newest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(zipcode)
	elif filter == "cheapest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(zipcode)
	else:
		url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(zipcode)
	
	for i in range(5):
		# try:
		headers= {
					'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'accept-encoding':'gzip, deflate, sdch, br',
					'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
					'cache-control':'max-age=0',
					'upgrade-insecure-requests':'1',
					'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
		}
		response = requests.get(url,headers=headers)
		print(response.status_code)
		parser = html.fromstring(response.content)
		search_results = parser.xpath("//*[@class='list-card-link list-card-link-top-margin']")
		# print(parser.xpath("//*[@class='list-card-link list-card-link-top-margin']")[0].attrib.get("href"))
		properties_url_list = []
		properties_list = []
		for result in search_results:
			properties_url_list.append(result.get("href"))

		for property_url in properties_url_list:
			current_property = html.fromstring(requests.get(property_url, headers=headers).content)
			raw_address = current_property.xpath("/html/body/div[1]/div[6]/div/div[1]/div/div/div[2]/div[4]/div[6]/div[1]/div[1]/div[2]/div/h1/span[1]//text()")
			raw_address_line_2 = current_property.xpath("/html/body/div[1]/div[6]/div/div[1]/div/div/div[2]/div[4]/div[2]/div/div[2]/div/h1/span[2]/text()[2]")
			raw_price = current_property.xpath("/html/body/div[1]/div[6]/div/div[1]/div/div/div[2]/div[4]/div[2]/div/div[1]/div/div/span/span/span//text()")
			url = property_url

			address = ' '.join(' '.join(raw_address).split()) if raw_address else None
			address_line_2 = ''.join(raw_address_line_2).strip() if raw_address_line_2 else None
			price = ''.join(raw_price).strip() if raw_price else None
			property_url = "https://www.zillow.com"+url[0] if url else None
			is_forsale = property.xpath('.//span[@class="zsg-icon-for-sale"]')
			property = {
							'address':address,
							'address_line_2':address_line_2,
							'price':price,
							'url':property_url,
			}
			properties_list.append(property)
		return properties_list
		# except:
		# 	print ("Failed to process the page",url)

if __name__=="__main__":
	argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	argparser.add_argument('zipcode',help = '')
	sortorder_help = """
    available sort orders are :
    newest : Latest property details,
    cheapest : Properties with cheapest price
    """
	argparser.add_argument('sort',nargs='?',help = sortorder_help,default ='Homes For You')
	args = argparser.parse_args()
	zipcode = args.zipcode
	sort = args.sort
	print ("Fetching data for %s"%(zipcode))
	scraped_data = parse(zipcode,sort)
	print ("Writing data to output file")
	with open("properties-%s.csv"%(zipcode),'wb')as csvfile:
		fieldnames = ['address', 'address_line_2' ,'price','url']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in  scraped_data:
			writer.writerow(row)

