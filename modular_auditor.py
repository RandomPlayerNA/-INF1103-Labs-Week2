inv = 0 # Inventory Stock Quantity
rej = 0 # Rejected Stock Quantity

# Continue Running Until User is Done or Inventory exceeds 500 Units
while True:
    
    # Ask User for Stock Quantity (Must be a Positive Integer)
    stock = input("\nEnter a stock quantity (or type 'quit' to finish): ")
    
    # Check if User Input is a Digit (This One will Auto Block Negatives Numbers too)
    if stock.isdigit():
                
        inv += int(stock)
        print(f"Added {stock} to Inventory: {inv}.\n\n")
        
        # Check if Inventory Exceeds 500 Units
        if inv > 500:
            print("Overstocked! Inventory exceeds 500 units!\n\n")
            break
        
    # Check if User Wants to Quit
    elif stock.lower() == 'quit':
        break
    
    # Handle Invalid Input
    else:
        rej += 1
        print("Invalid input! Please enter a positive integer or type 'quit' to exit.\n\n")

# Final Outputs
print("Total Units Processed: ", inv)
print("Number of Failed/Rejected Entries: ", rej)