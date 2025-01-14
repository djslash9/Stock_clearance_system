import streamlit as st

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Product Item Model
class ProductItem(Base):
    __tablename__ = 'product_items'
    item_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    purchase_price = Column(Float)
    selling_price = Column(Float)
    stock_shop = Column(Integer)
    stock_warehouse = Column(Integer)

# Customer Model (Updated with Email and Contact Number)
class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)  # Email field added
    contact_number = Column(String)  # Contact Number field added
    purchase_history = relationship("Sale", back_populates="customer")

# Employee Model
class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    designation = Column(String)
    salary = Column(Float)
    commission_rate = Column(Float)
    sales = relationship("Sale", back_populates="salesperson")

# Sales Model
class Sale(Base):
    __tablename__ = 'sales'
    sale_id = Column(Integer, primary_key=True)
    sale_date = Column(Date)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    salesperson_id = Column(Integer, ForeignKey('employees.employee_id'))
    item_id = Column(Integer, ForeignKey('product_items.item_id'))
    quantity_sold = Column(Integer)
    sales_price = Column(Float)
    total_sale_amount = Column(Float)
    commission_earned = Column(Float)
    
    customer = relationship("Customer", back_populates="purchase_history")
    salesperson = relationship("Employee", back_populates="sales")
    item = relationship("ProductItem")

# SQLite database URL (update to the location of your database)
DATABASE_URL = "sqlite:///app.db"

# Create the database engine and session
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


st.title('Ayurvedic Shop Inventory and Sales Management')

# Sidebar for navigation
st.sidebar.title('Menu')
option = st.sidebar.selectbox("Select Action", ["Manage Inventory", "Shop Inventory", "Process Sales", "Manage Employees", "Generate Reports"])

# Manage Inventory
if option == "Manage Inventory":
    st.header('Inventory Management')

    action = st.selectbox("Action", ["Add Item", "Remove Item", "Update Stock", "Generate Low Stock Alert"])

    if action == "Add Item":
        item_name = st.text_input('Item Name')
        description = st.text_area('Description')
        purchase_price = st.number_input('Purchase Price')
        selling_price = st.number_input('Selling Price')
        stock_shop = st.number_input('Stock Quantity (Shop)', min_value=0)
        stock_warehouse = st.number_input('Stock Quantity (Warehouse)', min_value=0)

        if st.button("Add Item"):
            # Ensure ProductItem model is used after it's defined
            new_item = ProductItem(
                name=item_name,
                description=description,
                purchase_price=purchase_price,
                selling_price=selling_price,
                stock_shop=stock_shop,
                stock_warehouse=stock_warehouse
            )
            session.add(new_item)
            session.commit()
            st.success(f"Item '{item_name}' added successfully!")


    # Other inventory actions: Remove Item, Update Stock, Low Stock Alert

# Shop Inventory Management
elif option == "Shop Inventory":
    st.header("Shop Inventory Management")

    # Select Action
    action = st.selectbox("Action", ["Daily Start Items", "Daily End Items"])

    # Daily Start Items (reduce from inventory)
    if action == "Daily Start Items":
        st.subheader("Daily Start Items")
        
        # Query all product items to populate dropdown
        items = session.query(ProductItem).all()
        item_names = [item.name for item in items]
        
        # Form for selecting items and reducing inventory
        selected_item = st.selectbox("Select Item", item_names)
        start_quantity = st.number_input("Start Quantity", min_value=0)

        # Get the selected item object
        item = session.query(ProductItem).filter_by(name=selected_item).first()

        if st.button("Reduce from Inventory"):
            if item and start_quantity <= item.stock_shop:
                # Reduce the start quantity from the shop stock
                item.stock_shop -= start_quantity
                session.commit()
                st.success(f"Reduced {start_quantity} from {selected_item} inventory. Remaining stock (Shop): {item.stock_shop}")
            else:
                st.error("Invalid quantity or insufficient stock.")

    # Daily End Items (provide current balance and transfer to inventory)
    elif action == "Daily End Items":
        st.subheader("Daily End Items")
        
        # Query all product items to populate dropdown
        items = session.query(ProductItem).all()
        item_names = [item.name for item in items]
        
        # Form for selecting items and viewing current balance
        selected_item = st.selectbox("Select Item", item_names)
        end_quantity = st.number_input("End Quantity", min_value=0)

        # Get the selected item object
        item = session.query(ProductItem).filter_by(name=selected_item).first()

        if item:
            st.write(f"Current balance in shop for {selected_item}: {item.stock_shop}")

        if st.button("Verify and Update Inventory"):
            if item and end_quantity >= 0:
                # Transfer the end balance back to inventory
                item.stock_shop = end_quantity
                session.commit()
                st.success(f"Updated {selected_item} inventory. New stock (Shop): {item.stock_shop}")
            else:
                st.error("Invalid quantity provided.")



# Process Sales
# Process Sales
elif option == "Process Sales":
    st.header('Sales Management')

    # Query all items that are available in the shop (i.e., stock_shop > 0)
    available_items = session.query(ProductItem).filter(ProductItem.stock_shop > 0).all()

    # Prepare item names for dropdown
    item_names = [f"{item.name} (Available: {item.stock_shop})" for item in available_items]

    if not available_items:
        st.warning("No items available in the shop.")
    else:
        # Form for processing sales
        selected_item = st.selectbox("Select Item", item_names)
        quantity_sold = st.number_input("Quantity Sold", min_value=1)

        # Query all salespeople to populate the salesperson dropdown
        salespeople = session.query(Employee).all()
        salesperson_names = [sp.name for sp in salespeople]

        selected_salesperson = st.selectbox("Select Salesperson", salesperson_names)

        # Customer details inputs
        customer_name = st.text_input('Customer Name')
        customer_email = st.text_input('Customer Email')
        customer_contact = st.text_input('Customer Contact Number')

        # Get the selected item and salesperson objects
        item = session.query(ProductItem).filter_by(name=selected_item.split(" (")[0]).first()
        salesperson = session.query(Employee).filter_by(name=selected_salesperson).first()

        # Calculate the total sale amount
        total_sale_amount = item.selling_price * quantity_sold
        commission_earned = (salesperson.commission_rate / 100) * total_sale_amount

        # Submit sale and update inventory
        if st.button("Process Sale"):
            if item and quantity_sold <= item.stock_shop:
                # Create a new Customer if not already in the database
                new_customer = Customer(
                    name=customer_name,
                    email=customer_email,
                    contact_number=customer_contact
                )
                session.add(new_customer)
                session.commit()

                # Reduce stock from the shop
                item.stock_shop -= quantity_sold

                # Create a new Sale entry
                new_sale = Sale(
                    sale_date=st.date_input("Sale Date"),
                    customer_id=new_customer.customer_id,  # Use new customer's ID
                    salesperson_id=salesperson.employee_id,
                    item_id=item.item_id,
                    quantity_sold=quantity_sold,
                    sales_price=item.selling_price,
                    total_sale_amount=total_sale_amount,
                    commission_earned=commission_earned
                )

                session.add(new_sale)
                session.commit()

                st.success(f"Sale processed successfully! {quantity_sold} units of {item.name} sold to {new_customer.name} by {salesperson.name}.")
                st.write(f"Total Sale Amount: {total_sale_amount}")
                st.write(f"Commission Earned: {commission_earned}")
                st.write(f"Remaining Stock (Shop): {item.stock_shop}")
            else:
                st.error("Invalid quantity or insufficient stock in the shop.")



# Manage Employees
elif option == "Manage Employees":
    st.header('Employee Management')

    # Add/remove employees, update salary and commission rates
    employee_action = st.selectbox("Employee Action", ["Add Employee", "Remove Employee", "Update Employee Details"])
    
    if employee_action == "Add Employee":
        employee_name = st.text_input('Employee Name')
        designation = st.text_input('Designation')
        salary = st.number_input('Salary')
        commission_rate = st.number_input('Commission Rate')

        if st.button("Add Employee"):
            new_employee = Employee(
                name=employee_name,
                designation=designation,
                salary=salary,
                commission_rate=commission_rate
            )
            session.add(new_employee)
            session.commit()
            st.success(f"Employee '{employee_name}' added successfully!")

# Generate Reports
elif option == "Generate Reports":
    st.header('Reporting')

    report_type = st.selectbox("Report Type", ["Sales Report", "Inventory Report", "Profit & Loss", "Employee Performance"])
    
    if report_type == "Sales Report":
        st.header("Sales Report")

        # Query all sales from the Sale table
        sales_data = session.query(Sale).all()

        # Prepare data for display as a table
        sales_report_data = []
        total_sales_amount = 0

        for sale in sales_data:
            # Get the customer and product details for the sale
            customer = session.query(Customer).filter_by(customer_id=sale.customer_id).first()
            item = session.query(ProductItem).filter_by(item_id=sale.item_id).first()

            # Append the sale details to the report
            sales_report_data.append({
                "Sale ID": sale.sale_id,
                "Date": sale.sale_date,
                "Customer Name": customer.name,
                "Item Name": item.name,
                "Quantity Sold": sale.quantity_sold,
                "Total Sale Amount": sale.total_sale_amount
            })

            total_sales_amount += sale.total_sale_amount

        # Display the sales data as a table
        if sales_report_data:
            st.table(sales_report_data)
            st.write(f"**Total Sales Amount: {total_sales_amount}**")
        else:
            st.warning("No sales data available.")
        
    elif report_type == "Inventory Report":
        st.header("Inventory Report")

        # Query all product items from the ProductItem table
        inventory_items = session.query(ProductItem).all()

        # Prepare data for display as a table
        inventory_data = []
        for item in inventory_items:
            inventory_data.append({
                "Item ID": item.item_id,
                "Item Name": item.name,
                "Description": item.description,
                "Purchase Price": item.purchase_price,
                "Selling Price": item.selling_price,
                "Stock (Shop)": item.stock_shop,
                "Stock (Warehouse)": item.stock_warehouse
            })

        # Display the inventory data as a table
        if inventory_data:
            st.table(inventory_data)
        else:
            st.warning("No inventory items found.")

    elif report_type == "Profit & Loss":
        st.header("Profit and Loss Report")

        # Query all sales from the Sales table
        sales_data = session.query(Sale).all()

        # Prepare data for display as a table
        profit_loss_data = []
        total_profit = 0
        total_sales = 0

        for sale in sales_data:
            # Get the corresponding product item for the sale
            item = session.query(ProductItem).filter_by(item_id=sale.item_id).first()
            
            # Calculate profit per sale
            profit = (sale.sales_price - item.purchase_price) * sale.quantity_sold
            total_sales += sale.total_sale_amount
            total_profit += profit
            
            # Append the data to the report
            profit_loss_data.append({
                "Sale ID": sale.sale_id,
                "Date": sale.sale_date,
                "Item Name": item.name,
                "Quantity Sold": sale.quantity_sold,
                "Total Sale Amount": sale.total_sale_amount,
                "Profit": profit
            })

        # Display the profit and loss data as a table
        if profit_loss_data:
            st.table(profit_loss_data)
            st.write(f"**Total Sales: {total_sales}**")
            st.write(f"**Total Profit: {total_profit}**")
        else:
            st.warning("No sales data available.")

    elif report_type == "Employee Performance":
        st.header("Employee Performance Report")

        # Query all employees from the Employee table
        employees = session.query(Employee).all()

        # Prepare data for display as a table
        employee_performance_data = []

        for employee in employees:
            # Query total sales and total commission for the employee
            sales_data = session.query(Sale).filter_by(salesperson_id=employee.employee_id).all()
            
            total_sales_amount = sum(sale.total_sale_amount for sale in sales_data)
            total_commission_earned = sum(sale.commission_earned for sale in sales_data)

            # Append employee performance data to the report
            employee_performance_data.append({
                "Employee ID": employee.employee_id,
                "Employee Name": employee.name,
                "Total Sales Amount": total_sales_amount,
                "Total Commission Earned": total_commission_earned
            })

        # Display the employee performance data as a table
        if employee_performance_data:
            st.table(employee_performance_data)
        else:
            st.warning("No employee performance data available.")



    # Add more reports for inventory, profit/loss, and employee performance