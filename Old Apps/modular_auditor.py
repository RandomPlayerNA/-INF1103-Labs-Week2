#------------------#
# GLOBAL VARIABLES
#------------------#

inv = 0 # Inventory Stock Quantity
rej = 0 # Rejected Stock Quantity
tax_rate = 0.1 # Tax Rate (10%)

#-----------#
# FUNCTIONS
#-----------#

# Function to Get Valid Input from User
def get_valid_input():
    
    # Ask User for Stock Quantity
    stock = input("\nEnter a stock quantity (or type 'quit' to finish): ").strip().lower()
    
    # Check if User Wants to Quit
    if stock == 'quit':
        return 'quit'
    
    # Check if User Input is a Digit (This One will Auto Block Negatives Numbers too)
    if stock.isdigit():
        return int(stock)
 
    return None

# Function to Process Delivery and Update Inventory
def process_delivery(current_total, new_value):
    return current_total + new_value
 
# Function to Calculate Tax on a Given Amount
def calculate_tax(amount):
    return amount * tax_rate

# Function to Generate a Report of Total Units and Failed Attempts
def generate_report(total_units, failed_attempts):
    print("Total Units Processed: ", total_units)
    print("Number of Failed/Rejected Entries: ", failed_attempts)

#------#
# Main
#------#

# Continue Running Until User is Done or Inventory exceeds 500 Units
while True:
    
    # Get Valid Input from User
    stock = get_valid_input()
    
    # Check if User Wants to Quit
    if stock == 'quit':
        break
    
    # Handle Invalid Input
    if stock is None:
        rej += 1
        print("Invalid input! Please enter a positive integer or type 'quit' to exit.\n\n")
        continue
    
    # Process Valid Input and Update Inventory
    inv = process_delivery(inv, stock)
    
    # Calculate Tax
    tax = calculate_tax(stock)
    
    # Print Current Inventory and Tax Information
    print(f"Added {stock} to inventory. Running total: {inv}")
    print(f"Tax on this delivery (10%): {tax:.2f}")
    
    # Check if Inventory Exceeds 500 Units
    if inv > 500:
        print("Overstocked! Inventory exceeds 500 units!")
        break
    
# Print Report
generate_report(inv, rej)