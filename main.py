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
        self.__id: str = productid
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        self.__supplier: Supplier = supplier

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

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
    def __init__(self, productid: str, name: str, price: float, stock: int,
                 weight: float, supplier: Supplier):
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
    def __init__(self, productid: str, name: str, price: float, stock: int,
                 download_size: float, supplier: Supplier):
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

    def remove_product(self, productid: str) -> bool:
        product = self.find_product(productid)
        if product is None:
            return False
        self.__products.remove(product)
        return True

    def display_all(self) -> None:
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

# Function to Get Valid Price from User
def get_valid_price_input(prompt: str) -> float:
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
    price = get_valid_price_input("Price: ")
    stock = get_valid_stock_input("Stock Quantity: ")

    # Ask for the Attribute Specific to the Chosen Product Type
    if product_type == "P":
        weight = get_valid_price_input("Weight (kg): ")
    else:
        download_size = get_valid_price_input("Download Size (MB): ")

    # Create the Supplier First, Then Pass It to the Product
    supplier_id = get_text_input("Supplier ID: ").upper()
    supplier_name = get_text_input("Supplier Name: ")
    supplier_email = get_text_input("Supplier Email: ")
    supplier = Supplier(supplier_id, supplier_name, supplier_email)

    if product_type == "P":
        inventory.add_product(PhysicalProduct(product_id, name, price, stock, weight, supplier))
    else:
        inventory.add_product(DigitalProduct(product_id, name, price, stock, download_size, supplier))
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
    suppliers = {}

    # Convert Each Product Dictionary into the Matching Product Sub-Class Using Its Type
    for item in data:
        supplier_data = item["supplier"]

        # Reuse the Same Supplier Object for Products with the Same Supplier
        if supplier_data["id"] not in suppliers:
            suppliers[supplier_data["id"]] = Supplier(supplier_data["id"], supplier_data["name"], supplier_data["email"])
        supplier = suppliers[supplier_data["id"]]

        if item["type"] == "physical":
            inventory.add_product(PhysicalProduct(item["id"], item["name"], item["price"], item["stock"], item["weight"], supplier))
        elif item["type"] == "digital":
            inventory.add_product(DigitalProduct(item["id"], item["name"], item["price"], item["stock"], item["download_size"], supplier))

    print("Inventory loaded successfully.\n")
    return inventory

# Function to Save Inventory to 'inventory.json'
def save_inventory(inventory: Inventory) -> None:
    with open(FILENAME, "w") as file:
        json.dump(inventory.to_list(), file, indent=4)

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
    print("6. Save Inventory")
    print("7. Exit")
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
        remove_product(inventory)
    elif option == "6":
        print("\nSaving inventory...")
        save_inventory(inventory)
        print(f"Inventory saved successfully to {FILENAME}.")
    elif option == "7":
        print("\nSaving inventory before exit...")
        save_inventory(inventory)
        print("Inventory saved successfully.")
        print("Thank you for using Inventory Management System.")
        print("Program terminated.")
        break
    else:
        print("Invalid option. Please enter a number from 1 to 7.")
        display_menu()
