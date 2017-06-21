import requests
import bs4
def get_num(x):
	return float(''.join(ele for ele in x if ele.isdigit() or ele == '.'))
def get_dec(x):
	a = (float(''.join(ele for ele in x if ele.isdigit() or ele == '.')))
	a = float("{0:.2f}".format(a))
	return a
def ReturnItem(page):
	item = str(page.title.string.encode("ascii", "ignore"))
	return str(item)
def Target(SKU, ZIP):
	if '-' not in SKU:
		SKU = ('{}-{}-{}'.format(SKU[0:3], SKU[3:5], SKU[5:9]))
	data = {
		'store_type': '1',
		'sku': SKU,
		'zip': ZIP,
		'sort': 'distance'
		}
	res = requests.post('http://brickseek.com/target-inventory-checker/?sku='.format(str(SKU)), data=data)
	page = bs4.BeautifulSoup(res.text, "lxml")
	Information = {
	'Discounted': str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class="product-stock-status-description">')[0],
	'StockPercent': str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2].partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class=')[0],
	"MSRP": str(str(page.select('.builder-row div div div')).partition('MSRP: <strong>')[2]).partition('</strong></span>')[0],
	"DCPI": str(str(page.select('.builder-row div div div')).partition('DPCI: <strong>')[2]).partition('</strong></span>')[0]
		}
	print(Information)
	Stores = page.select('.bsapi-inventory-checker-stores tr')
	for Result in Stores:
		try:
			Inventory = {
			"Store": str(str(Result).replace('<br/>', " ").partition('class="store-address">')[2]).partition('</address>')[0],
			"OnHand": int(get_num(str(str(Result).replace('<br/>', " ").partition('On Hand Qty: <strong>')[2]).partition('</strong>')[0])),
			"ForSale": int(get_num(str(str(Result).replace('<br/>', " ").partition('Saleable Qty: <strong>')[2]).partition('</strong>')[0])),
			"Price": get_dec((str(str(Result)).partition('$')[2]).partition('</span>')[0])
			}
			print(Inventory)

		except BaseException as exp:
			pass
def Walmart(SKU, ZIP):
	data = {
		'store_type': '3',
		'sku': SKU,
		'zip': ZIP,
		'sort': 'distance'
		}
	res = requests.post('http://brickseek.com/walmart-inventory-checker/?sku={}'.format(str(SKU)), data=data)
	page = bs4.BeautifulSoup(res.text, "lxml")
	Information = {
	'Discounted': str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class="product-stock-status-description">')[0],
	'StockPercent': str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2].partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class=')[0],
	"MSRP": str(str(page.select('.builder-row div div div')).partition('MSRP: <strong>')[2]).partition('</strong></span>')[0],
	"SKU": str(str(page.select('.builder-row div div div')).partition('SKU: <strong>')[2]).partition('</strong></span>')[0],
	"UPC": str(str(page.select('.builder-row div div div')).partition('UPC: <strong>')[2]).partition('</strong>')[0]
		}
	print(Information)
	Stores = page.select('.bsapi-inventory-checker-stores tr')
	for Result in Stores:
		try:
			Inventory = {
			"Store": str(str(Result).replace('<br/>', " ").partition('class="store-address">')[2]).partition('</address>')[0],
			"OnHand": int(get_num(str(str(Result).replace('<br/>', " ").partition('Quantity: <strong>')[2]).partition('</strong>')[0])),
			"ForSale": int(get_num(str(str(Result).replace('<br/>', " ").partition('Quantity: <strong>')[2]).partition('</strong>')[0])),
			"Price": get_dec((str(str(Result)).partition('$')[2]).partition('</span>')[0])
			}
			print(Inventory)
		except BaseException as exp:
			pass
def Staples(SKU, ZIP):
	data = {
		'store_type': '3',
		'sku': SKU,
		'zip': ZIP,
		'sort': 'distance'
		}

	res = requests.post('https://brickseek.com/inventory-check/staples/', data=data)
	page = bs4.BeautifulSoup(res.text, "lxml")
	Table = page.select('tr')[1:]
	for rows in Table:
		if 'Stock' not in str(rows):
			Table.remove(rows)
	for rows in Table:
		try:
			Inventory = {
			'Store': str(rows.select('td')[0]).partition(') <br/>')[2].partition('<br/>(')[0].replace('<br/>', ' '),
			'Quantity': int(get_num(rows.select('td')[1].getText()))
			}
			print(Inventory)
		except:
			pass