"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import logging
import time
import logging.handlers
import unittest
from threading import currentThread
import threading
from tema.product import Tea

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.id_producer = 0
        self.size = {}

        self.product_list = list()
        self.producer_list = {}

        self.cart_list = {}
        self.id_carts = 0

        self.mutex_qsize = threading.Lock()
        self.mutex_addcart = threading.Lock()
        self.mutex_cart = threading.Lock()
        self.mutex_printing = threading.Lock()

        logging.Formatter.converter = time.gmtime
        formatter = logging.Formatter('%(asctime)s %(levelname)8s: %(message)s')
        self.log = logging.basicConfig(filename='marketplace.log', level=logging.INFO)
        self.log = logging.getLogger('marketplace.log')
        my_handler = logging.handlers.RotatingFileHandler('marketplace.log', maxBytes=50000, backupCount=10)
        my_handler.setFormatter(formatter)
        self.log.addHandler(my_handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.log.info("Register new producer loading.")
        self.id_producer = self.id_producer + 1
        self.size[self.id_producer - 1] = 0  #queue size for producs
        self.log.info("Registered new producer with id %d", self.id_producer - 1)
        return self.id_producer - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

		# check if there is room for a new product and then adds it to the list
        self.log.info("Publish new product %s loading.", str(product))

        if self.size[int(producer_id)] is not self.queue_size_per_producer:
            self.size[int(producer_id)] += 1
            self.product_list.append(product)
            self.producer_list[product] = int(producer_id)
            self.log.info("Product %s was not published.", str(product))
            return True

        self.log.info("Product %s was not published.", str(product))
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.log.info("Add new cart loading.")

        self.mutex_cart.acquire()
        self.id_carts = self.id_carts + 1
        self.mutex_cart.release()

        self.cart_list[self.id_carts] = list()  # queue for products from the cart
        self.log.info("Added new cart with id %s.", self.id_carts)

        return self.id_carts

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.log.info("Add to cart with id %d product %s.", cart_id, str(product))

        with self.mutex_addcart:
            if product in self.product_list:  # check if the product is valid
                self.cart_list[cart_id].append(product)
                self.product_list.remove(product)  # remove it from the product lists
                producer = self.producer_list[product]
                self.size[producer] = self.size[producer] - 1
                self.log.info("Succeded to add to cart with id %d product %s.",
				cart_id, str(product))
                return True

        self.log.info("Failed to add to cart with id %d product %s.", cart_id, str(product))
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.log.info("Remove from cart with id %d product %s.", cart_id, str(product))

        if self.cart_list[cart_id] is not None:  # check if the cart is valid
            if product in self.cart_list[cart_id]:  # check if the product is in the cart
                self.cart_list[cart_id].remove(product)  # remove it from the cart

                self.mutex_qsize.acquire()  # and add it back tp the products list
                producer = self.producer_list[product]
                self.size[producer] = self.size[producer] + 1
                self.product_list.append(product)
                self.mutex_qsize.release()
        self.log.info("Removed from cart with id %d product %s.", cart_id, str(product))

        return True



    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.log.info("Place order from cart with id %s.", str(cart_id))

        for product_in in self.cart_list[cart_id]:
            self.mutex_printing.acquire()
            print(currentThread().getName() + " bought " + str(product_in))  # print the details
            self.mutex_printing.release()
        self.log.info("Placed order from cart and got the list-> %s.", str(self.cart_list[cart_id]))

        return self.cart_list[cart_id]


class TestMarketplace(unittest.TestCase):
    """
    unittest class
    """
    def setUp(self):
        """
        initialization
        """
        self.marketplace = Marketplace(3)
        self.first_product = Tea("tea", 5, "hot")
        self.list = []
        self.list.append(self.first_product)

    def test_register_producer(self):
        """
        testing one registration
        """
        self.assertEqual(self.marketplace.register_producer(), 0)

    def test_publish(self):
        """
        testing one publish
        """
        self.marketplace.register_producer()
        self.assertTrue(self.marketplace.publish("0", self.first_product))

    def test_new_cart(self):
        """
        testing new cart
        """
        self.assertEqual(self.marketplace.new_cart(), 1)

    def test_add_to_cart(self):
        """
        testing adding new cart
        """
        self.marketplace.register_producer()
        self.marketplace.publish("0", self.first_product)
        self.marketplace.new_cart()
        self.assertTrue(self.marketplace.add_to_cart(1, self.first_product))

    def test_remove_from_cart(self):
        """
        testing removing from cart
        """
        self.marketplace.register_producer()
        self.marketplace.publish("0", self.first_product)
        self.marketplace.new_cart()
        self.marketplace.add_to_cart(1, self.first_product)
        self.assertTrue(self.marketplace.remove_from_cart(1, self.first_product))

    def test_place_order(self):
        """
        testing placing order
        """
        self.marketplace.register_producer()
        self.marketplace.publish("0", self.first_product)
        self.marketplace.new_cart()
        self.marketplace.add_to_cart(1, self.first_product)

if __name__ == '__main__':
    """
    for unittest
    """
    unittest.main()
