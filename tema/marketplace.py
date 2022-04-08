"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread
import threading

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
        self.producer_capacity = {}

        self.products = list()
        self.producers = {}

        self.carts = {}
        self.id_carts = 0

        self.mutex_qsize = threading.Lock()
        self.mutex_addcart = threading.Lock()
        self.mutex_cart = threading.Lock()
        self.mutex_printing = threading.Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.id_producer = self.id_producer + 1
        self.producer_capacity[self.id_producer - 1] = 0
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

        if self.producer_capacity[int(producer_id)] < self.queue_size_per_producer:
            self.producer_capacity[int(producer_id)] += 1
            self.products.append(product)
            self.producers[product] = int(producer_id)
            return True

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.mutex_cart.acquire()
        self.id_carts = self.id_carts + 1
        self.mutex_cart.release()

        self.carts[self.id_carts] = list()

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
        mutex = threading.Lock()
        with self.mutex_addcart:
            if product in self.products:
                self.carts[cart_id].append(product)
                self.products.remove(product)
                producer = self.producers[product]
                self.producer_capacity[producer] = self.producer_capacity[producer] - 1
                return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        if product in self.carts[cart_id]:
            self.carts[cart_id].remove(product)

            self.mutex_qsize.acquire()
            producer = self.producers[product]
            self.producer_capacity[producer] = self.producer_capacity[producer] + 1
            self.products.append(product)
            self.mutex_qsize.release()



    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        for cart in self.carts[cart_id]:
            self.mutex_printing.acquire()
            print(str(currentThread().getName()) + " bought " + str(cart))
            self.mutex_printing.release()
        return self.carts[cart_id]