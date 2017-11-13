import requests
import bs4
from enum import Enum
import traceback

class Retailer(Enum):
	WALMART = 0
	TARGET = 1
	STAPLES = 2

class Store(object):
	def __init__(self, address):
		self.address = address

class Item(object):
	def __init__(self, api, retailer, sku):
		self.api = api
		self.retailer = retailer
		self.sku = sku

		self.name = ""
		self.discounted = 0.0
		self.stockingPercent = 1.0
		self.msrp = 0.0
		self.dcpi = 0.0

		self.inventory = []

	def fetchLocalInventory(self, zip):
		if self.retailer == Retailer.WALMART:
			self.inventory = self.api.lookupWalmart(self, zip)
		elif self.retailer == Retailer.TARGET:
			self.inventory = self.api.lookupTarget(self, zip)
		elif self.retailer == Retailer.STAPLES:
			self.inventory = self.api.lookupStaples(self, zip)
		else:
			print("Unknown retailer")
			return

		return self.inventory

	def updateStats(self, name, discounted, stockingPercent, msrp, dcpi):
		self.name = name
		self.discounted = discounted
		self.stockingPercent = stockingPercent
		self.msrp = msrp
		self.dcpi = dcpi

	def getURL(self):
		if self.retailer == Retailer.WALMART:
			return "http://brickseek.com/walmart-inventory-checker/?sku={}".format(str(self.sku))
		elif self.retailer == Retailer.TARGET:
			return "http://brickseek.com/target-inventory-checker/?sku=".format(str(self.sku))
		elif self.retailer == Retailer.STAPLES:
			print("Staples URL not supported")
			return
		else:
			print("Unknown retailer")
			return

class Inventory(object):
	def __init__(self, store, forSale, onHand, price):
		self.store = store
		self.forSale = forSale
		self.onHand = onHand
		self.price = price

class Brickseek(object):
	def __init__(self):
		self.api = Api(self)
		self.knownStores = {}

	def createWalmartItem(self, sku):
		return Item(self.api, Retailer.WALMART, sku)

	def createTargetItem(self, sku):
		return Item(self.api, Retailer.TARGET, sku)

	def createStaplesItem(self, sku):
		return Item(self.api, Retailer.STAPLES, sku)

	def createItem(self, retailer, sku):
		return Item(self.api, retailer, sku)

	def lookupStore(self, address):
		address = address.strip()

		store = None

		if address not in self.knownStores:
			store = Store(address)
			self.knownStores[address] = store
		else:
			store = self.knownStores[address]

		return store

	def updateUserAgent(self, userAgent):
		self.api.userAgent = userAgent

	def updateCookies(self, cf_clearance, cfduid):
		self.api.cf_clearance = cf_clearance
		self.api.cfduid = cfduid

class Api(object):
	def __init__(self, brickseek):
		self.brickseek = brickseek
		self.cf_clearance = None
		self.cfduid = None
		self.userAgent = None

	def get_num(self, x):
		return float(''.join(ele for ele in x if ele.isdigit() or ele == '.'))

	def get_dec(self, x):
		a = (float(''.join(ele for ele in x if ele.isdigit() or ele == '.')))
		a = float("{0:.2f}".format(a))
		return a

	def returnItem(self, page):
		item = str(page.title.string.encode("ascii", "ignore"))
		return str(item)

	def lookupTarget(self, item, zip):
		inventory = []
		sku = item.sku
		if '-' not in sku:
			sku = ('{}-{}-{}'.format(sku[0:3], sku[3:5], sku[5:9]))

		data = {
			'store_type': '1',
			'sku': sku,
			'zip': zip,
			'sort': 'distance'
			}
		res = requests.post('http://brickseek.com/target-inventory-checker/?sku='.format(str(sku)), data=data)
		page = bs4.BeautifulSoup(res.text, "lxml")

		name = str(str(page.select('.builder-row div div div')).partition('<img alt="')[2]).partition('" src=')[0]
		discounted = str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class="product-stock-status-description">')[0]
		stockingPercent = str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2].partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class=')[0]
		msrp = self.get_dec(str((str(page.select('.builder-row div div div')).partition('MSRP: <strong>')[2]).partition('</strong></span>')[0].replace('$', "")))
		dcpi = str(str(page.select('.builder-row div div div')).partition('DPCI: <strong>')[2]).partition('</strong></span>')[0]

		item.updateStats(name, discounted, stockingPercent, msrp, dcpi)

		stores = page.select('.bsapi-inventory-checker-stores tr')
		for result in stores:
			try:
				address = str(str(result).replace('<br/>', " ").partition('class="store-address">')[2]).partition('</address>')[0]

				onHand = 0
				try:
					onHand = int(self.get_num(str(str(result).replace('<br/>', " ").partition('On Hand Qty: <strong>')[2]).partition('</strong>')[0]))
				except:
					pass

				forSale = 0
				try:
					forSale = int(self.get_num(str(str(result).replace('<br/>', " ").partition('Saleable Qty: <strong>')[2]).partition('</strong>')[0]))
				except:
					pass

				price = self.get_dec((str(str(result)).partition('$')[2]).partition('</span>')[0])

				item = Inventory(self.brickseek.lookupStore(address), forSale, onHand, price)
				inventory.append(item)
				
			except BaseException as exp:
				pass

		return inventory

	def lookupWalmart(self, item, zip):
		inventory = []
		sku = item.sku
		data = {
			'store_type': '3',
			'sku': sku,
			'zip': zip,
			'sort': 'distance'
			}

		cookies = {}
		headers = {}

		if self.cf_clearance and self.cfduid:
			cookies = {'cf_clearance': self.cf_clearance, '__cfduid': self.cfduid}

		if self.userAgent:
			headers = {'user-agent': self.userAgent}

		res = requests.post('https://brickseek.com/walmart-inventory-checker/?sku={}'.format(str(sku)), data=data, headers=headers, cookies=cookies, timeout=10)

		if res.status_code != 200:
			return res.status_code

		page = bs4.BeautifulSoup(res.text, "lxml")

		name = str(str(page.select('.builder-row div div div')).partition('<img alt="')[2]).partition('" src=')[0]
		
		discounted = None
		try:
			discounted = str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class="product-stock-status-description">')[0]
		except:
			pass
		
		stockingPercent = None
		try:
			stockingPercent = str(str(page.select('.builder-row div div div div')).partition('"product-stock-status-percent">')[2].partition('"product-stock-status-percent">')[2]).partition('</span>\n<span class=')[0]
		except:
			pass
		
		msrp = None
		try:
			msrp = self.get_dec(str((str(page.select('.builder-row div div div')).partition('MSRP: <strong>')[2]).partition('</strong></span>')[0].replace('$', "")))
		except:
			# MSRP is not a number (likely N.A.)
			pass

		upc = None
		try:
			upc = str(str(page.select('.builder-row div div div')).partition('SKU: <strong>')[2]).partition('</strong></span>')[0]
		except:
			pass

		item.updateStats(name, discounted, stockingPercent, msrp, upc)

		stores = page.select('.bsapi-inventory-checker-stores tr')
		for result in stores:
			try:
				address = str(str(result).replace('<br/>', " ").partition('class="store-address">')[2]).partition('</address>')[0]

				forSale = 0
				try:
					forSale = int(self.get_num(str(str(result).replace('<br/>', " ").partition('Quantity: <strong>')[2]).partition('</strong>')[0]))
				except:
					pass

				price = self.get_dec((str(str(result)).partition('$')[2]).partition('</span>')[0])

				item = Inventory(self.brickseek.lookupStore(address), forSale, forSale, price)
				inventory.append(item)

			except BaseException as exp:
				pass

		return inventory

	def lookupStaples(self, item, zip):
		inventory = []
		sku = item.sku
		data = {
			'store_type': '3',
			'sku': sku,
			'zip': zip,
			'sort': 'distance'
			}

		res = requests.post('https://brickseek.com/inventory-check/staples/', data=data)
		page = bs4.BeautifulSoup(res.text, "lxml")
		table = page.select('tr')[1:]
		for rows in table:
			if 'Stock' not in str(rows):
				table.remove(rows)
		for rows in table:
			try:
				store = str(rows.select('td')[0]).partition(') <br/>')[2].partition('<br/>(')[0].replace('<br/>', ' ')
				quantity = int(self.get_num(rows.select('td')[1].getText()))

				inventory.append(Inventory(self.brickseek.lookupStore(address), quantity, quantity, None))
			except:
				pass

		return inventory