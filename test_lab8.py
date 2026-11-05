# ------- #
# Imports
# ------- #

from main import Supplier, Product, PhysicalProduct, DigitalProduct, Inventory, Order

# -------------- #
# Test Functions
# -------------- #

# Association: Supplier and Product
def test_association() -> None:
    print("\n---- Association: Supplier and Product ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, 2.0, supplier)
    antivirus = DigitalProduct("P005", "Antivirus Software", 49.99, 100, 350.0, supplier)

    # Both Products Point to the Same Supplier Object
    print(f"Same supplier object: {laptop.get_supplier() is antivirus.get_supplier()}")

    # Delete the Variable, Not the Object
    del supplier
    print("\nAfter 'del supplier':")
    print("Laptop's supplier:")
    laptop.get_supplier().display_information()
    print("Antivirus's supplier:")
    antivirus.get_supplier().display_information()

# Aggregation: Inventory and Product
def test_aggregation() -> None:
    print("\n---- Aggregation: Inventory and Product ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")

    # Product Exists Before Any Inventory
    mouse = PhysicalProduct("P002", "Mouse", 25.5, 40, 0.1, supplier)
    inventory_a = Inventory()
    inventory_b = Inventory()

    inventory_a.add_product(mouse)
    print(f"In Inventory A: {inventory_a.find_product('P002') is not None}")

    inventory_a.remove_product("P002")
    print(f"In Inventory A after remove: {inventory_a.find_product('P002') is not None}")

    # Product Still Works After Removal
    print("\nMouse after removal from A:")
    mouse.display_information()

    inventory_b.add_product(mouse)
    print(f"\nIn Inventory B: {inventory_b.find_product('P002') is not None}")
    print(f"Same object in B: {inventory_b.find_product('P002') is mouse}")

    # Emptying an Inventory Does Not Destroy Products
    print(f"\nInventory A product count: {len(inventory_a.get_products())}")
    print(f"Mouse still exists: {mouse.get_name()}")

# Composition: Order and OrderLine
def test_composition() -> None:
    print("\n---- Composition: Order and OrderLine ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.0, 15, 2.0, supplier)
    keyboard = PhysicalProduct("P003", "Keyboard", 45.0, 25, 0.8, supplier)

    order_1 = Order("O001")
    order_1.add_order_line(laptop, 2)
    order_1.add_order_line(keyboard, 1)
    order_1.display_order()

    # Same Product in a Different Order
    order_2 = Order("O002")
    order_2.add_order_line(laptop, 1)
    print()
    order_2.display_order()

    line_1 = order_1.get_order_lines()[0]
    line_2 = order_2.get_order_lines()[0]
    print(f"\nSame OrderLine object: {line_1 is line_2}")
    print(f"Same Product object: {line_1.get_product() is line_2.get_product()}")
    print(f"OrderLine ids: {id(line_1)} / {id(line_2)}")
    print(f"Product ids:   {id(line_1.get_product())} / {id(line_2.get_product())}")

    # Removing a Line Goes Through the Order
    order_1.remove_order_line("P003")
    print("\nOrder O001 after removing Keyboard:")
    order_1.display_order()
    print(f"Keyboard still exists: {keyboard.get_name()}")

# LSP: Works with Any Product
def show_product_details(product: Product) -> None:
    product.display_information()
    print(product.get_fulfillment_info())

def test_substitutability() -> None:
    print("\n---- LSP: Substitutability ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")
    monitor = PhysicalProduct("P004", "Monitor", 299.99, 10, 5.5, supplier)
    antivirus = DigitalProduct("P005", "Antivirus Software", 49.99, 100, 350.0, supplier)

    # Same Function, Both Product Types
    print("Physical:")
    show_product_details(monitor)
    print("\nDigital:")
    show_product_details(antivirus)

    # Both Types Work with Normal Inventory Operations
    inventory = Inventory()
    inventory.add_product(monitor)
    inventory.add_product(antivirus)
    monitor.update_stock(8)
    antivirus.update_stock(90)
    print(f"\nMonitor stock: {inventory.find_product('P004').get_stock()}")
    print(f"Antivirus stock: {inventory.find_product('P005').get_stock()}")

    # Inventory Asks Each Product to Display Itself
    print("\n----- display_all_products() -----")
    inventory.display_all_products()

# Both Sub-Classes Keep the update_stock() Expectation
def test_parent_expectation() -> None:
    print("\n---- Parent Class Expectation: update_stock() ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")
    products: list[Product] = [
        PhysicalProduct("P003", "Keyboard", 45.0, 25, 0.8, supplier),
        DigitalProduct("P005", "Antivirus Software", 49.99, 100, 350.0, supplier)
    ]

    for product in products:
        # Valid Input Is Accepted
        product.update_stock(5)
        print(f"{product.get_name()} stock after update_stock(5): {product.get_stock()}")

        # Invalid Input Is Rejected the Same Way
        try:
            product.update_stock(-1)
        except ValueError as error:
            print(f"{product.get_name()} update_stock(-1): ValueError - {error}")

# Polymorphism: One Loop, No isinstance()
def test_polymorphism() -> None:
    print("\n---- Polymorphism ----")
    supplier = Supplier("S001", "TechWorld Supplies", "sales@techworld.example.com")
    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.0, 15, 2.0, supplier))
    inventory.add_product(DigitalProduct("P005", "Antivirus Software", 49.99, 100, 350.0, supplier))

    for product in inventory.get_products():
        product.display_information()
        print(f"get_fulfillment_info(): {product.get_fulfillment_info()}")
        print("------------------")

# ---- #
# Main
# ---- #

test_association()
test_aggregation()
test_composition()
test_substitutability()
test_parent_expectation()
test_polymorphism()
