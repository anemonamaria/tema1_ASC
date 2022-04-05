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
        self.queue_size_per_producer = queue_size_per_producer
        self.sizes_per_producer = []  # How many items a producer has in the queue

        self.carts = {}  # Cart ID (Int) --> [Operation]
        self.number_of_carts = 0

        self.products = []  # the queue with all available products
        self.producers = {}  # Product --> Producer

        self.lock_for_sizes = Lock()  # for changing the size of a producer's queue
        self.lock_for_carts = Lock()  # for changing the number of carts
        self.lock_for_register = Lock()  # for atomic registration of a producer
        self.lock_for_print = Lock()  # for not interleaving the prints
        # pass

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.lock_for_register:
            producer_id = len(self.sizes_per_producer)
        self.sizes_per_producer.append(0)
        return producer_id
        # pass

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        num_prod_id = int(producer_id)

        max_size = self.queue_size_per_producer
        crt_size = self.sizes_per_producer[num_prod_id]

        if crt_size >= max_size:
            return False

        with self.lock_for_sizes:
            self.sizes_per_producer[num_prod_id] += 1
        self.products.append(product)
        self.producers[product] = num_prod_id

        return True
        # pass

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        ret_id = 0
        with self.lock_for_carts:
            self.number_of_carts += 1
            ret_id = self.number_of_carts

        self.carts[ret_id] = []

        return ret_id

        # pass

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.lock_for_sizes:
            if product not in self.products:
                return False

            self.products.remove(product)

            producer = self.producers[product]
            self.sizes_per_producer[producer] -= 1

        self.carts[cart_id].append(product)
        return True
        # pass

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
