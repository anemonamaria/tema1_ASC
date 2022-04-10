import unittest

from marketplace import Marketplace
import product

class TestMarketplace(unittest.TestCase):

    def setUp(self):
        self.marketplace = Marketplace(3)
        # self.marketplace.queue_size_per_producer = 3
        self.first_product = product.Tea("tea", 5, "hot")
        self.list = []
        self.list.append(self.first_product)

    def test_register_producer(self):
        self.assertEqual(self.marketplace.register_producer(), 0)

    def test_publish(self):
        # print(self.marketplace.queue_size_per_producer)
        # print(self.marketplace.size[0])
        self.assertTrue(self.marketplace.publish("0", self.first_product))

    def test_new_cart(self):
        self.assertEqual(self.marketplace.new_cart(), 1)

    def test_add_to_cart(self):
        self.assertFalse(self.marketplace.add_to_cart(1, self.first_product))

    def test_remove_from_cart(self):
        self.assertTrue(self.marketplace.remove_from_cart(1, self.first_product))

    def test_place_order(self):
        self.assertEqual(self.marketplace.place_order(1), self.list)

if __name__ == '__main__':
    unittest.main()
