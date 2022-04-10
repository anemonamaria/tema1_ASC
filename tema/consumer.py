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
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        """
        Creates a new cart instance for each of the current consumer's carts
        and executes every given operation.

        If one operation fails, the consumer will wait for its retry_wait_time
        until he can retry the current operation.
        Once he finishes all his operations, he moves on to the next cart.

        return_code = True (successful "add"), None ("remove") or False (failed "add")
        """
        for crt_cart in self.carts:
            cart_id = self.marketplace.new_cart()

            for crt_operation in crt_cart:

                number_of_operations = 0
                while number_of_operations < crt_operation["quantity"]:

                    op_product = crt_operation["product"]

                    # Execute the current operation
                    if crt_operation["type"] == "add":
                        return_code = self.marketplace.add_to_cart(cart_id, op_product)
                    elif crt_operation["type"] == "remove":
                        return_code = self.marketplace.remove_from_cart(cart_id, op_product)

                    if return_code == True or return_code is None:
                        number_of_operations += 1
                    else:
                        time.sleep(self.retry_wait_time)

            # Place the order with all the products from the current cart
            self.marketplace.place_order(cart_id)
