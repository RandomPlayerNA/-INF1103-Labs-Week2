# --------#
# Imports
# --------#

import json
import os

# ----------#
# Variables
# ----------#

FILENAME = "inventory.json"

# ----------------#
# Input Functions
# ----------------#

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


# --------------------#
# Inventory Functions
# --------------------#

# Function to Find a Product Dictionary by ID (Returns None if Not Found)
def find_product(inventory, product_id):
    for product in inventory:
        if product["id"] == product_id:
            return product
    return None


# Function to Display All Products
def display_all(inventory):
    print("\nCurrent Inventory")
    print("------------------")

    if not inventory:
        print("No products in inventory.")

    for product in inventory:
        print(f"ID: {product['id']} | Name: {product['name']} | "
              f"Price: ${product['price']:.2f} | Stock: {product['stock']}")

    print("------------------")


# Function to Add a New Product
def add_product(inventory):
    print("\nAdd New Product")
    product_id = get_text_input("Product ID: ").upper()

    # Product IDs Must Be Unique
    if find_product(inventory, product_id):
        print("Product ID already exists. Use Update Stock instead.")
        return

    name = get_text_input("Product Name: ")
    price = get_valid_price_input("Price: ")
    stock = get_valid_stock_input("Stock Quantity: ")

    inventory.append({"id": product_id, "name": name, "price": price, "stock": stock})
    print("\nProduct added successfully!")


# Function to Update the Stock of an Existing Product
def update_stock(inventory):
    print("\nUpdate Stock")
    product = find_product(inventory, get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product['name']}")
    print(f"Current Stock: {product['stock']}")
    product["stock"] = get_valid_stock_input("\nNew Stock Quantity: ")
    print("\nStock updated successfully!")


# Function to Search for a Product by ID
def search_product(inventory):
    print("\nSearch Product")
    product = find_product(inventory, get_text_input("Enter Product ID: ").upper())

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("------------------")
    print(f"ID: {product['id']}")
    print(f"Name: {product['name']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock']}")
    print("------------------")


# ----------------------#
# Persistence Functions
# ----------------------#

# Function to Load Inventory from 'inventory.json' (Empty List if Missing)
def load_inventory():
    if not os.path.exists(FILENAME):
        print(f"\n{FILENAME} not found.")
        print("Starting with an empty inventory.")
        return []

    print(f"\n{FILENAME} found.")
    try:
        with open(FILENAME, "r") as file:
            inventory = json.load(file)
    except json.JSONDecodeError:
        print("\File is empty or corrupted. Starting with an empty inventory.")
        return []

    print("Inventory loaded successfully.\n")
    return inventory


# Function to Save Inventory to 'inventory.json'
def save_inventory(inventory):
    with open(FILENAME, "w") as file:
        json.dump(inventory, file, indent=4)


# ------#
# Menu
# ------#

def display_menu():
    print("----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


# ------#
# Main
# ------#

print("================================")
print("INVENTORY MANAGEMENT SYSTEM")
print("================================")

inventory = load_inventory()  # List of Product Dictionaries
display_menu()

# Continue Running Until User Chooses Exit
while True:
    option = input("\nEnter option: ").strip()

    if option == "1":
        display_all(inventory)
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
            