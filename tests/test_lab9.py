# ------- #
# Imports
# ------- #

import os
import unittest
from unittest.mock import patch

from main import (Supplier, Product, PhysicalProduct, DigitalProduct, Inventory, Order,
                  ProductFactory, NoDiscount, PercentageDiscount, BulkDiscount,
                  StudentDiscount, get_positive_float, load_products)

# --------- #
# Variables
# --------- #

# products.csv Is in the Project Folder, One Level Above tests/
PRODUCTS_CSV = os.path.join(os.path.dirname(__file__), "..", "products.csv")

# -------------- #
# Helper Functions
# -------------- #

# Function to Create a Supplier for the Tests
def make_supplier() -> Supplier:
    return Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")

# Function to Create an Order Whose Lines Add Up to 250
def make_order_250() -> Order:
    supplier = make_supplier()
    keyboard = ProductFactory.create("physical", "P003", "Keyboard", 45.0, 25, supplier, weight=0.8)
    mouse = ProductFactory.create("physical", "P002", "Mouse", 25.0, 40, supplier, weight=0.1)
    order = Order("O001")
    order.add_order_line(keyboard, 5)
    order.add_order_line(mouse, 1)
    return order

# ---------- #
# Test Cases
# ---------- #

# Section 2 - Strategy Pattern: Order Discounts
class TestDiscountStrategy(unittest.TestCase):

    def test_default_is_no_discount(self) -> None:
        order = make_order_250()
        self.assertEqual(order.calculate_total(), 250.0)

    def test_no_discount_returns_total_unchanged(self) -> None:
        self.assertEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount(self) -> None:
        self.assertEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_at_or_over_threshold(self) -> None:
        self.assertEqual(BulkDiscount(200, 20).apply(250.0), 230.0)
        self.assertEqual(BulkDiscount(200, 20).apply(200.0), 180.0)

    def test_bulk_discount_under_threshold(self) -> None:
        self.assertEqual(BulkDiscount(200, 20).apply(150.0), 150.0)

    # New Strategy Works Without Changing Order
    def test_student_discount_new_strategy(self) -> None:
        order = make_order_250()
        order.set_discount(StudentDiscount())
        self.assertEqual(order.calculate_total(), 237.5)

    # set_discount() Replaces the Strategy, It Does Not Stack
    def test_set_discount_changes_strategy(self) -> None:
        order = make_order_250()
        order.set_discount(BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 230.0)
        order.set_discount(PercentageDiscount(10))
        self.assertEqual(order.calculate_total(), 225.0)

    def test_strategy_given_when_order_created(self) -> None:
        order = Order("O002", PercentageDiscount(10))
        product = ProductFactory.create("digital", "D001", "Photo Editor", 100.0, 5,
                                        make_supplier(), download_size=500.0)
        order.add_order_line(product, 1)
        self.assertEqual(order.calculate_total(), 90.0)

# Section 3 - Factory Pattern: Creating Products
class TestProductFactory(unittest.TestCase):

    def test_creates_physical_product(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10,
                                        make_supplier(), weight=1.5)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertIsInstance(product, Product)

    def test_creates_digital_product(self) -> None:
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.90, 100,
                                        make_supplier(), download_size=800.0)
        self.assertIsInstance(product, DigitalProduct)
        self.assertIsInstance(product, Product)

    def test_unknown_type_raises_clear_error(self) -> None:
        with self.assertRaises(ValueError) as context:
            ProductFactory.create("service", "S001", "Installation", 30.0, 5, make_supplier())
        self.assertEqual(str(context.exception), "Unknown product type: service")

# Section 4 - Validation
class TestValidation(unittest.TestCase):

    def test_price_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P001", "Desk Lamp", 0, 10, make_supplier())

    def test_negative_price_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D001", "Photo Editor", -5.0, 10, make_supplier())

    def test_negative_stock_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, -1, make_supplier())

    # Both Sub-Classes Keep the Parent's Stock Rule (LSP)
    def test_negative_stock_rejected_for_digital(self) -> None:
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D001", "Photo Editor", 49.90, -1, make_supplier())

    def test_zero_stock_allowed(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 0, make_supplier())
        self.assertEqual(product.get_stock(), 0)

    def test_order_quantity_zero_rejected(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10, make_supplier())
        with self.assertRaises(ValueError):
            Order("O001").add_order_line(product, 0)

    def test_order_quantity_negative_rejected(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.0, 10, make_supplier())
        with self.assertRaises(ValueError):
            Order("O001").add_order_line(product, -2)

# Section 5.1 - Handling Invalid User Input
class TestUserInput(unittest.TestCase):

    # Fake User Types abc, -5, Then 12.50 (print Is Silenced to Keep Output Clean)
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["abc", "-5", "12.50"])
    def test_asks_again_until_valid(self, mock_input, mock_print) -> None:
        self.assertEqual(get_positive_float("Price: "), 12.5)
        self.assertEqual(mock_input.call_count, 3)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["abc", "-5", "12.50"])
    def test_correct_message_for_each_mistake(self, mock_input, mock_print) -> None:
        get_positive_float("Price: ")
        mock_print.assert_any_call("Please enter a valid number, e.g. 12.50")
        mock_print.assert_any_call("Please enter a number greater than zero.")

# Section 5.2 - Loading Products from a File
class TestLoadProducts(unittest.TestCase):

    @patch("builtins.print")
    def test_missing_file_does_not_crash(self, mock_print) -> None:
        inventory = Inventory()
        load_products("file_that_does_not_exist.csv", inventory, make_supplier())
        self.assertEqual(len(inventory.get_products()), 0)
        mock_print.assert_any_call("Load attempt finished.")

    @patch("builtins.print")
    def test_bad_rows_skipped_valid_rows_load(self, mock_print) -> None:
        inventory = Inventory()
        load_products(PRODUCTS_CSV, inventory, make_supplier())

        loaded_ids = []
        for product in inventory.get_products():
            loaded_ids.append(product.get_id())

        self.assertEqual(loaded_ids, ["P001", "D001", "P003"])
        mock_print.assert_any_call("3 products loaded.")

    @patch("builtins.print")
    def test_loaded_products_use_factory_types(self, mock_print) -> None:
        inventory = Inventory()
        load_products(PRODUCTS_CSV, inventory, make_supplier())
        self.assertIsInstance(inventory.find_product("P001"), PhysicalProduct)
        self.assertIsInstance(inventory.find_product("D001"), DigitalProduct)

# ---- #
# Main
# ---- #

if __name__ == "__main__":
    unittest.main()
