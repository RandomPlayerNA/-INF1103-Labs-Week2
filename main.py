# ------- #
# Imports
# ------- #

import csv
import json
import os
from abc import ABC, abstractmethod

# --------- #
# Variables
# --------- #

FILENAME = "inventory.json"

# ------- #
# Classes
# ------- #

# Supplier Class
class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.__supplier_id}")
        print(f"Supplier Name: {self.__name}")
        print(f"Contact Email: {self.__contact_email}")

    def to_dict(self) -> dict:
        return {
            "id": self.__supplier_id,
            "name": self.__name,
            "email": self.__contact_email
        }

# Abstract Base Class for Products that Can Be Shipped
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass

# Abstract Product Class
class Product(ABC):
    def __init__(self, productid: str, name: str, price: float, stock: int, supplier: Supplier):
        
        # Product Protects Its Own Rules
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock cannot be negative.")

        self.__id: str = productid
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        self.__supplier: Supplier = supplier

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    @abstractmethod
    def get_fulfillment_info(self) -> str:
        pass

    def update_stock(self, quantity: int) -> None:
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Stock must be a non-negative integer.")
        self.__stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self.__id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")
        print(f"Fulfillment: {self.get_fulfillment_info()}")
        self.__supplier.display_information()

    def to_dict(self) -> dict:
        return {
            "id": self.__id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier": self.__supplier.to_dict()
        }

# Product Sub-Class with New Attribute, Weight
class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, productid: str, name: str, price: float, stock: int, weight: float, supplier: Supplier):
        super().__init__(productid, name, price, stock, supplier)
        self.__weight: float = weight

    def calculate_shipping_cost(self) -> float:
        return self.__weight * 10  # $10 per kg

    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.__weight} kg")
        print(f"Shipping Cost: ${self.calculate_shipping_cost():.2f}")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data

    def get_fulfillment_info(self) -> str:
        return "Product requires physical shipping."

# Product Sub-Class with New Attribute, Download Size
class DigitalProduct(Product):
    def __init__(self, productid: str, name: str, price: float, stock: int, download_size: float, supplier: Supplier):
        super().__init__(productid, name, price, stock, supplier)
        self.__download_size: float = download_size

    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.__download_size} MB")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data

    def get_fulfillment_info(self) -> str:
        return "Product is delivered digitally."

# Product Factory Class (The Only Place that Creates Products)
class ProductFactory:
    
    # Weight Is Only Used by Physical, Download Size Only by Digital
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float, stock: int, supplier: Supplier, weight: float = 0.0, download_size: float = 0.0) -> Product:
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock, weight, supplier)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock, download_size, supplier)
        else:
            raise ValueError(f"Unknown product type: {product_type}")

# Inventory Class
class Inventory:
    def __init__(self):
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> None:
        self.__products.append(product)

    def find_product(self, productid: str) -> Product | None:
        for product in self.__products:
            if product.get_id() == productid:
                return product
        return None

    def get_products(self) -> list[Product]:
        return self.__products

    def remove_product(self, productid: str) -> bool:
        product = self.find_product(productid)
        if product is None:
            return False
        self.__products.remove(product)
        return True

    def display_all_products(self) -> None:
        if not self.__products:
            print("No products in inventory.")
            return
        print("\nCurrent Inventory")
        print("------------------")
        for product in self.__products:
            product.display_information()
            print("------------------")
    
    def to_list(self) -> list[dict]:
        return [product.to_dict() for product in self.__products]

# Abstract Discount Strategy Class
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass

# Discount Strategy that Leaves the Total Unchanged
class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total

# Discount Strategy that Takes a Percentage Off
class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.__percentage: float = percentage

    def apply(self, total: float) -> float:
        return total - (total * self.__percentage / 100)

# Discount Strategy that Takes an Amount Off Totals Over a Threshold
class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float):
        self.__threshold: float = threshold
        self.__amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount
        return total

# Discount Strategy for Students (5% Off)
class StudentDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total - (total * 5 / 100)

# OrderLine Class (Refers to a Product, Does Not Own It)
class OrderLine:
    def __init__(self, product: Product, quantity: int):
        
        # OrderLine Protects Its Own Quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(f"{self.__product.get_name()} x {self.__quantity} = ${self.calculate_subtotal():.2f}")

# Order Class (Creates and Owns Its OrderLines)
class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None):
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

        # Use No Discount if None Is Given
        if discount is None:
            discount = NoDiscount()
        self.__discount: DiscountStrategy = discount

    # Strategy Can Be Swapped Later
    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    # OrderLine Is Created Inside the Order, Never Passed In
    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def get_order_lines(self) -> list[OrderLine]:
        return self.__order_lines

    def remove_order_line(self, productid: str) -> bool:
        for line in self.__order_lines:
            if line.get_product().get_id() == productid:
                self.__order_lines.remove(line)
                return True
        return False

    # Each OrderLine Calculates Its Own Subtotal, Then the Strategy Applies the Discount
    def calculate_total(self) -> float:
        total = 0.0
        for line in self.__order_lines:
            total += line.calculate_subtotal()
        return self.__discount.apply(total)

    def display_order(self) -> None:
        print(f"Order ID: {self.__order_id}")
        if not self.__order_lines:
            print("No order lines.")
            return
        for line in self.__order_lines:
            line.display_information()
        print(f"Total: ${self.calculate_total():.2f}")

# --------------- #
# Input Functions
# --------------- #

# Function to Get Non-Empty Text from User
def get_text_input(prompt: str) -> str:
    text = input(prompt).strip()

    while not text:
        print("Input cannot be empty. Please try again.")
        text = input(prompt).strip()

    return text

# Function to Get Valid Stock Quantity from User
def get_valid_stock_input(prompt: str) -> int:
    stock = input(prompt).strip()

    # isdigit() Blocks Negatives, Decimals and Text
    while not stock.isdigit():
        print("Invalid input! Please enter a non-negative integer.")
        stock = input(prompt).strip()

    return int(stock)

# Function to Get a Positive Number from User
def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt).strip())

            # Validation: Must Be Above Zero
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value

        # Exception: Text that Is Not a Number
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")

# ------------------- #
# Inventory Functions
# ------------------- #

# Function to Add a New Product
def add_product(inventory: Inventory) -> None:
    print("\nAdd New Product")
    product_id = get_text_input("Product ID: ").upper()

    # Product IDs Must Be Unique
    if inventory.find_product(product_id):
        print("Product ID already exists. Use Update Stock instead.")
        return

    product_type = get_text_input("Product Type (P = Physical, D = Digital): ").upper()

    while product_type not in ("P", "D"):
        print("Invalid input! Please enter P or D.")
        product_type = get_text_input("Product Type (P = Physical, D = Digital): ").upper()

    name = get_text_input("Product Name: ")
    price = get_positive_float("Price: ")
    stock = get_valid_stock_input("Stock Quantity: ")

    # Ask for the Attribute Specific to the Chosen Product Type
    weight = 0.0
    download_size = 0.0
    if product_type == "P":
        product_type = "physical"
        weight = get_positive_float("Weight (kg): ")
    else:
        product_type = "digital"
        download_size = get_positive_float("Download Size (MB): ")

    # Create the Supplier First, Then Pass It to the Product
    supplier_id = get_text_input("Supplier ID: ").upper()
    supplier_name = get_text_input("Supplier Name: ")
    supplier_email = get_text_input("Supplier Email: ")
    supplier = Supplier(supplier_id, supplier_name, supplier_email)

    # Factory Decides Which Product Class to Create
    product = ProductFactory.create(product_type, product_id, name, price, stock, supplier, weight, download_size)
    inventory.add_product(product)
    print("\nProduct added successfully!")

# Function to Update the Stock of an Existing Product
def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product = inventory.find_product(get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")
    product.update_stock(get_valid_stock_input("\nNew Stock Quantity: "))
    print("\nStock updated successfully!")

# Function to Search for a Product by ID
def search_product(inventory: Inventory) -> None:
    print("\nSearch Product")
    product = inventory.find_product(get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("------------------")
    product.display_information()
    print("------------------")

# Function to Remove a Product by ID
def remove_product(inventory: Inventory) -> None:
    print("\nRemove Product")
    product_id = get_text_input("Enter Product ID: ").upper()

    if inventory.remove_product(product_id):
        print("\nProduct removed successfully!")
    else:
        print("\nProduct not found.")

# --------------- #
# Order Functions
# --------------- #

# Function to Create a New Order from Inventory Products
def create_order(inventory: Inventory, orders: list[Order]) -> None:
    print("\nCreate Order")
    order = Order(get_text_input("Order ID: ").upper())
    lines_added = 0

    # Keep Adding Products Until User Enters a Blank ID
    while True:
        product_id = input("Product ID (Blank to Finish): ").strip().upper()
        if not product_id:
            break

        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue

        quantity = get_valid_stock_input("Quantity: ")
        while quantity == 0:
            print("Quantity must be at least 1.")
            quantity = get_valid_stock_input("Quantity: ")

        order.add_order_line(product, quantity)
        lines_added += 1
        print(f"{product.get_name()} added to order.")

    # Empty Orders Are Not Kept
    if lines_added == 0:
        print("\nNo products added. Order cancelled.")
        return

    orders.append(order)
    print("\nOrder created successfully!")
    print("------------------")
    order.display_order()
    print("------------------")

# Function to Display All Orders Created This Session
def view_orders(orders: list[Order]) -> None:
    if not orders:
        print("\nNo orders created yet.")
        return
    print("\nAll Orders")
    print("------------------")
    for order in orders:
        order.display_order()
        print("------------------")

# --------------------- #
# Persistence Functions
# --------------------- #

# Function to Load Inventory from 'inventory.json' (Empty Inventory if Missing)
def load_inventory() -> Inventory:
    inventory = Inventory()

    if not os.path.exists(FILENAME):
        print(f"\n{FILENAME} not found.")
        print("Starting with an empty inventory.")
        return inventory

    print(f"\n{FILENAME} found.")
    try:
        with open(FILENAME, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("\nFile is empty or corrupted. Starting with an empty inventory.")
        return inventory

    # Suppliers Already Created, Stored by Supplier ID
    suppliers: dict[str, Supplier] = {}

    # Convert Each Product Dictionary into a Product Using the Factory
    for item in data:
        supplier_data = item["supplier"]

        # Reuse the Same Supplier Object for Products with the Same Supplier
        if supplier_data["id"] not in suppliers:
            suppliers[supplier_data["id"]] = Supplier(supplier_data["id"], supplier_data["name"], supplier_data["email"])
        supplier = suppliers[supplier_data["id"]]

        # Unknown Types Are Skipped Instead of Crashing the Program
        try:
            product = ProductFactory.create(
                item["type"], 
                item["id"], 
                item["name"], 
                item["price"],
                item["stock"], 
                supplier, 
                item.get("weight", 0.0),
                item.get("download_size", 0.0)
            )
            
            inventory.add_product(product)
        except ValueError as error:
            print(f"Skipped {item['id']}: {error}")

    print("Inventory loaded successfully.\n")
    return inventory

# Function to Save Inventory to 'inventory.json'
def save_inventory(inventory: Inventory) -> None:
    with open(FILENAME, "w") as file:
        json.dump(inventory.to_list(), file, indent=4)

# Function to Load Products from a CSV File (Bad Rows Are Skipped)
def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        with file:
            reader = csv.reader(file)
            next(reader)  # Skip the Header Row
            loaded = 0

            # Each Row Has Its Own try, So One Bad Row Does Not Stop the Rest
            for row in reader:
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    float(price), int(stock), supplier)
                    inventory.add_product(product)
                    loaded += 1
                except ValueError as error:
                    print(f"Skipped row {row}: {error}")

        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")

# ---- #
# Menu
# ---- #

def display_menu() -> None:
    print("----------- MENU ----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Create Order")
    print("7. View Orders")
    print("8. Save Inventory")
    print("9. Exit")
    print("---------------------------")

# ---- #
# Main
# ---- #

# Menu Only Runs When main.py Is Run Directly, Not When Imported
if __name__ == "__main__":
    print("================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("================================")

    inventory = load_inventory()

    # Orders Are Kept in Memory Only (Not Saved)
    orders: list[Order] = []
    display_menu()

    # Continue Running Until User Chooses Exit
    while True:
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all_products()
        elif option == "2":
            add_product(inventory)
        elif option == "3":
            update_stock(inventory)
        elif option == "4":
            search_product(inventory)
        elif option == "5":
            remove_product(inventory)
        elif option == "6":
            create_order(inventory, orders)
        elif option == "7":
            view_orders(orders)
        elif option == "8":
            print("\nSaving inventory...")
            save_inventory(inventory)
            print(f"Inventory saved successfully to {FILENAME}.")
        elif option == "9":
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 9.")
            display_menu()