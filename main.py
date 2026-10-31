# ------- #
# Imports
# ------- #

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

# Abstract Base Class for Products that Can Be Shipped
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self):
        pass

# Abstract Product Class
class Product(ABC):
    def __init__(self, productid, name, price, stock):
        self.__id = productid
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_stock(self):
        return self.__stock
    
    @abstractmethod
    def get_fulfillment_info(self):
        pass

    def update_stock(self, quantity):
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Stock must be a non-negative integer.")
        self.__stock = quantity

    def display_information(self):
        print(f"ID: {self.__id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")
        print(f"Fulfillment: {self.get_fulfillment_info()}")

    def to_dict(self):
        return {
            "id": self.__id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock
        }

# Product Sub-Class with New Attribute, Weight
class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, productid, name, price, stock, weight):
        super().__init__(productid, name, price, stock)
        self.__weight = weight

    def calculate_shipping_cost(self):
        return self.__weight * 10  # $10 per kg

    def display_information(self):
        super().display_information()
        print(f"Weight: {self.__weight} kg")
        print(f"Shipping Cost: ${self.calculate_shipping_cost():.2f}")

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data
    
    def get_fulfillment_info(self):
        return "Product requires physical shipping."

# Product Sub-Class with New Attribute, Download Size
class DigitalProduct(Product):
    def __init__(self, productid, name, price, stock, download_size):
        super().__init__(productid, name, price, stock)
        self.__download_size = download_size

    def display_information(self):
        super().display_information()
        print(f"Download Size: {self.__download_size} MB")

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data
    
    def get_fulfillment_info(self):
        return "Product is delivered digitally."

# Inventory Class
class Inventory:
    def __init__(self):
        self.__products = []
        
    def add_product(self, product):
        self.__products.append(product)
        
    def search_product(self, productid):
        for product in self.__products:
            if product.get_id() == productid:
                return product
        return None
        
    def display_all(self):
        if not self.__products:
            print("No products in inventory.")
            return
        print("\nCurrent Inventory")
        print("------------------")
        for product in self.__products:
            product.display_information()
            print("------------------")
    
    def to_list(self):
        return [product.to_dict() for product in self.__products]

# --------------- #
# Input Functions
# --------------- #

# Function to Get Non-Empty Text from User
def get_text_input(prompt):
    text = input(prompt).strip()

    while not text:
        print("Input cannot be empty. Please try again.")
        text = input(prompt).strip()

    return text

# Function to Get Valid Stock Quantity from User
def get_valid_stock_input(prompt):
    stock = input(prompt).strip()

    # isdigit() Blocks Negatives, Decimals and Text
    while not stock.isdigit():
        print("Invalid input! Please enter a non-negative integer.")
        stock = input(prompt).strip()

    return int(stock)

# Function to Get Valid Price from User
def get_valid_price_input(prompt):
    while True:
        try:
            price = float(input(prompt).strip())
            if price >= 0:
                return price
        except ValueError:
            pass
        print("Invalid input! Please enter a non-negative number.")

# ------------------- #
# Inventory Functions
# ------------------- #

# Function to Add a New Product
def add_product(inventory):
    print("\nAdd New Product")
    product_id = get_text_input("Product ID: ").upper()

    # Product IDs Must Be Unique
    if inventory.search_product(product_id):
        print("Product ID already exists. Use Update Stock instead.")
        return

    product_type = get_text_input("Product Type (P = Physical, D = Digital): ").upper()

    while product_type not in ("P", "D"):
        print("Invalid input! Please enter P or D.")
        product_type = get_text_input("Product Type (P = Physical, D = Digital): ").upper()

    name = get_text_input("Product Name: ")
    price = get_valid_price_input("Price: ")
    stock = get_valid_stock_input("Stock Quantity: ")

    # Ask for the Attribute Specific to the Chosen Product Type
    if product_type == "P":
        weight = get_valid_price_input("Weight (kg): ")
        inventory.add_product(PhysicalProduct(product_id, name, price, stock, weight))
    else:
        download_size = get_valid_price_input("Download Size (MB): ")
        inventory.add_product(DigitalProduct(product_id, name, price, stock, download_size))
    print("\nProduct added successfully!")

# Function to Update the Stock of an Existing Product
def update_stock(inventory):
    print("\nUpdate Stock")
    product = inventory.search_product(get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")
    product.update_stock(get_valid_stock_input("\nNew Stock Quantity: "))
    print("\nStock updated successfully!")

# Function to Search for a Product by ID
def search_product(inventory):
    print("\nSearch Product")
    product = inventory.search_product(get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("------------------")
    product.display_information()
    print("------------------")

# --------------------- #
# Persistence Functions
# --------------------- #

# Function to Load Inventory from 'inventory.json' (Empty Inventory if Missing)
def load_inventory():
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

    # Convert Each Product Dictionary into the Matching Product Sub-Class Using Its Type
    for item in data:
        if item["type"] == "physical":
            inventory.add_product(PhysicalProduct(item["id"], item["name"], item["price"],
                                                  item["stock"], item["weight"]))
        elif item["type"] == "digital":
            inventory.add_product(DigitalProduct(item["id"], item["name"], item["price"],
                                                 item["stock"], item["download_size"]))

    print("Inventory loaded successfully.\n")
    return inventory

# Function to Save Inventory to 'inventory.json'
def save_inventory(inventory):
    with open(FILENAME, "w") as file:
        json.dump(inventory.to_list(), file, indent=4)

# ---- #
# Menu
# ---- #

def display_menu():
    print("----------- MENU ----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("---------------------------")

# ---- #
# Main
# ---- #

print("================================")
print("INVENTORY MANAGEMENT SYSTEM")
print("================================")

inventory = load_inventory()
display_menu()

# Continue Running Until User Chooses Exit
while True:
    option = input("\nEnter option: ").strip()

    if option == "1":
        inventory.display_all()
    elif option == "2":
        add_product(inventory)
    elif option == "3":
        update_stock(inventory)
    elif option == "4":
        search_product(inventory)
    elif option == "5":
        print("\nSaving inventory...")
        save_inventory(inventory)
        print(f"Inventory saved successfully to {FILENAME}.")
    elif option == "6":
        print("\nSaving inventory before exit...")
        save_inventory(inventory)
        print("Inventory saved successfully.")
        print("Thank you for using Inventory Management System.")
        print("Program terminated.")
        break
    else:
        print("Invalid option. Please enter a number from 1 to 6.")
        display_menu()
