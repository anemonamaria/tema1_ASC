"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread

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
		# TODO change these types
        self.queue_size_per_producer = queue_size_per_producer
        self.id_producer = 0
        self.sizes_per_producer = list()  # How many items a producer has in the queue

        self.carts = {}  # Cart ID (Int) --> [Operation]
        self.id_carts = 0

        self.products = list()  # the queue with all available products
        self.producers = {}  # Product --> Producer

        self.lock_for_sizes = Lock()  # for changing the size of a producer's queue
        self.lock_for_carts = Lock()  # for changing the number of carts
        # self.lock_for_register = Lock()  # for atomic registration of a producer
        self.lock_for_print = Lock()  # for not interleaving the prints
        # pass

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.id_producer = self.id_producer + 1
        self.sizes_per_producer.append(0)
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

        if self.sizes_per_producer[int(producer_id)] < self.queue_size_per_producer:
            self.sizes_per_producer[int(producer_id)] += 1
            self.products.append(product)
            self.producers[product] = int(producer_id)
            return True

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.lock_for_carts.acquire()
        self.id_carts = self.id_carts + 1
        self.lock_for_carts.release()

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
		# TODO from here to modify
        with self.lock_for_sizes:
            if product in self.products:
                self.products.remove(product)
                producer = self.producers[product]
                self.sizes_per_producer[producer] -= 1
                self.carts[cart_id].append(product)
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
        self.carts[cart_id].remove(product)

        with self.lock_for_sizes:
            producer = self.producers[product]
            self.sizes_per_producer[producer] += 1

        self.products.append(product)
        # pass

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        product_list = self.carts.pop(cart_id, None)

        for prod in product_list:
            with self.lock_for_print:
                print(str(currentThread().getName()) + " bought " + str(prod))

        return product_list

        # pass
