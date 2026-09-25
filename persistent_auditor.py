#-----------#
# FUNCTIONS
#-----------#

# Funtion to get Product Name or 'quit' from User
def get_product_name():
    product_name = input("Enter Product Name: ").strip()
    
    while not product_name:
        print("Product name cannot be empty. Please try again.")
        product_name = input("Enter Product Name: ").strip()
    
    # Check if User Wants to Quit
    if product_name.lower() == 'quit':
        return 'quit'
    
    return product_name

# Function to Get Valid Input from User
def get_valid_stock_input():
    
    # Ask User for Stock Quantity
    stock = input("Enter Quantity: ").strip().lower()
    
    # Check if User Input is a Digit (This One will Auto Block Negatives Numbers too)
    while not stock.isdigit():
        print("Invalid input! Please enter a positive integer.")
        stock = input("Enter Quantity: ").strip().lower()
    
    return int(stock)

# Function to Print out Order in 'inventory.txt' File & Return Total Order Count
def load_inventory():
    print("Current Orders:")
    with open('inventory.txt', 'a+') as file:
        file.seek(0)  # Move the cursor to the beginning of the file
        contents = file.read()
        length = len(contents.splitlines())
        
        # Check if File is Empty and Print Contents or Message
        if length == 0:
            print("No orders found." + "\n")
        else:
            print(contents + "\n")
        
    return length

# Function to Save Inventory to 'inventory.txt' File
def save_inventory(inventory):
    with open('inventory.txt', 'a') as file:
        for item in inventory:
            file.write(f"{item[0]},{item[1]},{item[2]}\n")
            
# -----------------#
# GLOBAL VARIABLES
# -----------------#

INV = [] #Initialize Inventory List
LEN_ORDER = load_inventory() # Get Current Order
ID = 1000 + LEN_ORDER # Get Current Product ID

#------#
# Main
#------#

# Continue Running Until User is Done or Wants to Quit
while True:
    
    # Get Product Name from User
    product_name = get_product_name()
    
    # Check if User Wants to Quit
    if product_name == 'quit':
        break
    
    # Get Valid Input from User
    stock = get_valid_stock_input()
    
    ID += 1  # Increment Product ID for Each New Order
    
    # Print New Order Added
    print(f"\nNew Order Added:\n{ID},{product_name},{stock}\n")
    
    # Append Product to Inventory List
    INV.append((ID, product_name, stock))
    
# Save Inventory to 'inventory.txt' File
save_inventory(INV)
print("\nOrder successfully saved to inventory.txt")