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
    # pylint: disable=too-many-instance-attributes
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.sizes_per_producer = [] # How many items a producer has in the queue

        self.carts = {} # Cart ID (Int) --> [Operation]
        self.number_of_carts = 0

        self.products = [] # the queue with all available products
        self.producers = {} # Product --> Producer

        self.lock_for_sizes = Lock() # for changing the size of a producer's queue
        self.lock_for_carts = Lock() # for changing the number of carts
        self.lock_for_register = Lock() # for atomic registration of a producer
        self.lock_for_print = Lock() # for not interleaving the prints

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        Adds a new producer with no produced items

        We need to use a lock for the registration, because
        any operation which changes the size of a list is not a thread-safe operation.
        The length of the sizes list might be changed by another "register" thread
        before the current thread appends 0 the list.
        """
        with self.lock_for_register:
            producer_id = len(self.sizes_per_producer)
        self.sizes_per_producer.append(0)
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace.
        Returns False if the current size is above the queue capacity.
        Otherwise, return True and the product is added in the queue.

        THE 'append', 'dict[key] = value' and 'x = y' operations are thread-safe.
        The '+= 1' operation is not thread-safe, so it must be in a synchronized block.

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace
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

    def new_cart(self):
        """
        Creates a new cart for the consumer.

        :returns an int representing the cart_id

        The '+= 1' operation is not thread-safe, so we must use a specific lock.
        We also need to include the ret_id assignent in the lock, because
        the number of carts can be changed once more by another running thread.
        """
        ret_id = 0
        with self.lock_for_carts:
            self.number_of_carts += 1
            ret_id = self.number_of_carts

        self.carts[ret_id] = []

        return ret_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns.
        Removes the respective product from the list of available products

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False.
        If the caller receives False, it should wait and then try again

        In order not to have more consumers take the same product,
        we need a size-exclusive lock for the non-thread-safe size increment.
        """
        with self.lock_for_sizes:
            if product not in self.products:
                return False

            self.products.remove(product)

            producer = self.producers[product]
            self.sizes_per_producer[producer] -= 1

        self.carts[cart_id].append(product)
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        Adds the respective product back to the list of available products.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart

        In order not to have more consumers remove the same product from their carts,
        we need a size-exclusive lock for the non-thread-safe size increment.
        """
        self.carts[cart_id].remove(product)

        with self.lock_for_sizes:
            producer = self.producers[product]
            self.sizes_per_producer[producer] += 1

        self.products.append(product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.
        Prints the contents of the cart with a lock,
        so that the program doesn't interleave the output strings.

        :type cart_id: Int
        :param cart_id: id cart
        """

        product_list = self.carts.pop(cart_id, None)

        for prod in product_list:
            with self.lock_for_print:
                print(str(currentThread().getName()) + " bought " + str(prod))

        return product_list
