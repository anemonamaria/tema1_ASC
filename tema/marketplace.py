"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import currentThread
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
        self.id = 0
        self.size = {}

        self.product_list = list()
        self.producer_list = {}

        self.cart_list = {}
        self.id_carts = 0

        self.mutex_qsize = threading.Lock()
        self.mutex_addcart = threading.Lock()
        self.mutex_cart = threading.Lock()
        self.mutex_printing = threading.Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.id = self.id + 1
        self.size[self.id - 1] = 0  #queue size for producs
        return self.id - 1

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
        if self.size[int(producer_id)] is not self.queue_size_per_producer:
            self.size[int(producer_id)] += 1
            self.product_list.append(product)
            self.producer_list[product] = int(producer_id)
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

        self.cart_list[self.id_carts] = list()  # queue for products from the cart

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
        with self.mutex_addcart:
            if product in self.product_list:  # check if the product is valid
                self.cart_list[cart_id].append(product)
                self.product_list.remove(product)  # remove it from the product lists
                producer = self.producer_list[product]
                self.size[producer] = self.size[producer] - 1
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
        if self.cart_list[cart_id] is not None:  # check if the cart is valid
            if product in self.cart_list[cart_id]:  # check if the product is in the cart
                self.cart_list[cart_id].remove(product)  # remove it from the cart

                self.mutex_qsize.acquire()  # and add it back tp the products list
                producer = self.producer_list[product]
                self.size[producer] = self.size[producer] + 1
                self.product_list.append(product)
                self.mutex_qsize.release()
        return True



    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        for cart in self.cart_list[cart_id]:
            self.mutex_printing.acquire()
            print(currentThread().getName() + " bought " + str(cart))  # print the details
            self.mutex_printing.release()
        return self.cart_list[cart_id]