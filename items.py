class Retailer(Enum):
	WALMART = 0
	TARGET = 1
	STAPLES = 2

class Store(object):
	def __init__(self, address):
		self.address = address

class Item(object):
	def __init__(self, retailer, sku):
		self.retailer = retailer
		self.sku = sku

	def getLocalStores(self, zip):
		if self.retailer == WALMART:
			Walmart(self.sku, zip)

class Inventory(object):
	def __init__(self, store, forSale, onHand, price):
		self.store = store
		self.forSale = forSale
		self.onHand = onHand
		self.price = price