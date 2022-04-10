"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

        Thread.__init__(self, **kwargs)

    def check_code(self, code, iteration):
        """
        check if there is need for delay
        """
        if code is True:
            iteration = iteration + 1
        else:
            time.sleep(self.retry_wait_time)
        return iteration

    def run(self):
        """
        generate carts for that size
        """
        for i in range(len(self.carts)):
            id_cart = self.marketplace.new_cart()
            for command in self.carts[i]:
                my_type = command["type"]
                quantity = command["quantity"]
                my_product = command["product"]
                iteration = 0
				# checks what type of command we have and then we do that
                if my_type == "add":
                    while iteration < quantity:
                        code = self.marketplace.add_to_cart(id_cart, my_product)
                        iteration = Consumer.check_code(self, code, iteration)

                elif my_type == "remove":
                    while iteration < quantity:
                        code = self.marketplace.remove_from_cart(id_cart, my_product)
                        iteration = Consumer.check_code(self, code, iteration)

            self.marketplace.place_order(id_cart)
