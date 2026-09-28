import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# ================= DATABASE =================

db = sqlite3.connect("pharmacy.db")
cursor = db.cursor()

# Medicine table
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    quantity INTEGER,
    price REAL,
    expiry TEXT
)
""")

# Customer table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    address TEXT
)
""")

# Sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine TEXT,
    quantity INTEGER,
    total REAL
)
""")

db.commit()


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Pharmacy Management System")
root.geometry("1100x700")
root.configure(bg="#f4f6f7")


# ================= FUNCTIONS =================

def clear_medicine():
    medicine_name.delete(0, tk.END)
    company_name.delete(0, tk.END)
    medicine_quantity.delete(0, tk.END)
    medicine_price.delete(0, tk.END)
    expiry_date.delete(0, tk.END)


def show_medicines():

    for item in medicine_table.get_children():
        medicine_table.delete(item)

    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()

    for medicine in medicines:
        medicine_table.insert("", tk.END, values=medicine)


def add_medicine():

    name = medicine_name.get()
    company = company_name.get()
    quantity = medicine_quantity.get()
    price = medicine_price.get()
    expiry = expiry_date.get()

    if name == "" or quantity == "" or price == "":
        messagebox.showerror("Error", "Please enter medicine details")
        return

    try:
        quantity = int(quantity)
        price = float(price)

        cursor.execute("""
        INSERT INTO medicines
        (name, company, quantity, price, expiry)
        VALUES (?, ?, ?, ?, ?)
        """, (name, company, quantity, price, expiry))

        db.commit()

        messagebox.showinfo(
            "Success",
            "Medicine added successfully"
        )

        clear_medicine()
        show_medicines()

    except ValueError:
        messagebox.showerror(
            "Error",
            "Quantity and price must be numbers"
        )


def select_medicine(event):

    selected = medicine_table.focus()

    if selected == "":
        return

    data = medicine_table.item(selected, "values")

    clear_medicine()

    medicine_name.insert(0, data[1])
    company_name.insert(0, data[2])
    medicine_quantity.insert(0, data[3])
    medicine_price.insert(0, data[4])
    expiry_date.insert(0, data[5])


def update_medicine():

    selected = medicine_table.focus()

    if selected == "":
        messagebox.showerror(
            "Error",
            "Please select a medicine"
        )
        return

    data = medicine_table.item(selected, "values")
    medicine_id = data[0]

    name = medicine_name.get()
    company = company_name.get()
    quantity = medicine_quantity.get()
    price = medicine_price.get()
    expiry = expiry_date.get()

    if name == "" or quantity == "" or price == "":
        messagebox.showerror(
            "Error",
            "Please fill all required fields"
        )
        return

    try:
        quantity = int(quantity)
        price = float(price)

        cursor.execute("""
        UPDATE medicines
        SET name=?, company=?, quantity=?, price=?, expiry=?
        WHERE id=?
        """, (
            name,
            company,
            quantity,
            price,
            expiry,
            medicine_id
        ))

        db.commit()

        messagebox.showinfo(
            "Success",
            "Medicine updated successfully"
        )

        clear_medicine()
        show_medicines()

    except ValueError:
        messagebox.showerror(
            "Error",
            "Enter valid quantity and price"
        )


def delete_medicine():

    selected = medicine_table.focus()

    if selected == "":
        messagebox.showerror(
            "Error",
            "Please select a medicine"
        )
        return

    data = medicine_table.item(selected, "values")
    medicine_id = data[0]

    answer = messagebox.askyesno(
        "Delete",
        "Do you want to delete this medicine?"
    )

    if answer:

        cursor.execute(
            "DELETE FROM medicines WHERE id=?",
            (medicine_id,)
        )

        db.commit()

        messagebox.showinfo(
            "Success",
            "Medicine deleted"
        )

        clear_medicine()
        show_medicines()


def search_medicine():

    search = search_box.get()

    for item in medicine_table.get_children():
        medicine_table.delete(item)

    cursor.execute("""
    SELECT * FROM medicines
    WHERE name LIKE ?
    """, ("%" + search + "%",))

    medicines = cursor.fetchall()

    for medicine in medicines:
        medicine_table.insert(
            "",
            tk.END,
            values=medicine
        )


# ================= CUSTOMER =================

def add_customer():

    name = customer_name.get()
    mobile = customer_mobile.get()
    address = customer_address.get()

    if name == "" or mobile == "":
        messagebox.showerror(
            "Error",
            "Please enter customer name and mobile"
        )
        return

    cursor.execute("""
    INSERT INTO customers
    (name, mobile, address)
    VALUES (?, ?, ?)
    """, (name, mobile, address))

    db.commit()

    messagebox.showinfo(
        "Success",
        "Customer added successfully"
    )

    customer_name.delete(0, tk.END)
    customer_mobile.delete(0, tk.END)
    customer_address.delete(0, tk.END)


# ================= BILLING =================

def generate_bill():

    name = bill_medicine.get()
    quantity = bill_quantity.get()

    if name == "" or quantity == "":
        messagebox.showerror(
            "Error",
            "Please enter medicine and quantity"
        )
        return

    try:
        quantity = int(quantity)

        cursor.execute("""
        SELECT price, quantity
        FROM medicines
        WHERE name=?
        """, (name,))

        medicine = cursor.fetchone()

        if medicine is None:
            messagebox.showerror(
                "Error",
                "Medicine not found"
            )
            return

        price = medicine[0]
        available = medicine[1]

        if quantity > available:
            messagebox.showerror(
                "Error",
                "Not enough stock"
            )
            return

        total = price * quantity

        # Reduce stock
        new_quantity = available - quantity

        cursor.execute("""
        UPDATE medicines
        SET quantity=?
        WHERE name=?
        """, (new_quantity, name))

        # Save sale
        cursor.execute("""
        INSERT INTO sales
        (medicine, quantity, total)
        VALUES (?, ?, ?)
        """, (name, quantity, total))

        db.commit()

        bill_result.config(
            text=f"Medicine: {name}\n"
                 f"Quantity: {quantity}\n"
                 f"Price: ₹{price:.2f}\n"
                 f"Total: ₹{total:.2f}"
        )

        show_medicines()

    except ValueError:

        messagebox.showerror(
            "Error",
            "Quantity must be a number"
        )


# ================= TITLE =================

title = tk.Label(
    root,
    text="PHARMACY MANAGEMENT SYSTEM",
    font=("Arial", 24, "bold"),
    bg="#1976d2",
    fg="white",
    pady=15
)

title.pack(fill=tk.X)


# ================= MEDICINE FRAME =================

medicine_frame = tk.LabelFrame(
    root,
    text="Medicine Management",
    font=("Arial", 13, "bold"),
    bg="#f4f6f7",
    padx=10,
    pady=10
)

medicine_frame.pack(
    fill=tk.X,
    padx=15,
    pady=10
)


# Medicine Name

tk.Label(
    medicine_frame,
    text="Medicine Name",
    bg="#f4f6f7"
).grid(row=0, column=0, padx=5, pady=5)

medicine_name = tk.Entry(
    medicine_frame,
    width=20
)

medicine_name.grid(row=0, column=1)


# Company

tk.Label(
    medicine_frame,
    text="Company",
    bg="#f4f6f7"
).grid(row=0, column=2)

company_name = tk.Entry(
    medicine_frame,
    width=20
)

company_name.grid(row=0, column=3)


# Quantity

tk.Label(
    medicine_frame,
    text="Quantity",
    bg="#f4f6f7"
).grid(row=1, column=0)

medicine_quantity = tk.Entry(
    medicine_frame,
    width=20
)

medicine_quantity.grid(row=1, column=1)


# Price

tk.Label(
    medicine_frame,
    text="Price",
    bg="#f4f6f7"
).grid(row=1, column=2)

medicine_price = tk.Entry(
    medicine_frame,
    width=20
)

medicine_price.grid(row=1, column=3)


# Expiry

tk.Label(
    medicine_frame,
    text="Expiry Date",
    bg="#f4f6f7"
).grid(row=2, column=0)

expiry_date = tk.Entry(
    medicine_frame,
    width=20
)

expiry_date.grid(row=2, column=1)


# Buttons

tk.Button(
    medicine_frame,
    text="Add",
    width=12,
    bg="green",
    fg="white",
    command=add_medicine
).grid(row=2, column=2, padx=5)

tk.Button(
    medicine_frame,
    text="Update",
    width=12,
    bg="orange",
    command=update_medicine
).grid(row=2, column=3, padx=5)

tk.Button(
    medicine_frame,
    text="Delete",
    width=12,
    bg="red",
    fg="white",
    command=delete_medicine
).grid(row=3, column=2, pady=5)

tk.Button(
    medicine_frame,
    text="Clear",
    width=12,
    command=clear_medicine
).grid(row=3, column=3)


# ================= SEARCH =================

search_frame = tk.Frame(
    root,
    bg="#f4f6f7"
)

search_frame.pack(fill=tk.X, padx=15)

tk.Label(
    search_frame,
    text="Search Medicine:",
    font=("Arial", 11, "bold"),
    bg="#f4f6f7"
).pack(side=tk.LEFT)

search_box = tk.Entry(
    search_frame,
    width=30
)

search_box.pack(
    side=tk.LEFT,
    padx=10
)

tk.Button(
    search_frame,
    text="Search",
    command=search_medicine,
    bg="#1976d2",
    fg="white"
).pack(side=tk.LEFT)

tk.Button(
    search_frame,
    text="Show All",
    command=show_medicines
).pack(side=tk.LEFT, padx=5)


# ================= MEDICINE TABLE =================

table_frame = tk.Frame(root)

table_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=15,
    pady=10
)

columns = (
    "ID",
    "Medicine",
    "Company",
    "Quantity",
    "Price",
    "Expiry"
)

medicine_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:

    medicine_table.heading(
        column,
        text=column
    )

    medicine_table.column(
        column,
        width=130
    )

medicine_table.pack(
    fill=tk.BOTH,
    expand=True
)

medicine_table.bind(
    "<ButtonRelease-1>",
    select_medicine
)


# ================= CUSTOMER FRAME =================

customer_frame = tk.LabelFrame(
    root,
    text="Customer Details",
    font=("Arial", 13, "bold"),
    bg="#f4f6f7"
)

customer_frame.pack(
    fill=tk.X,
    padx=15,
    pady=5
)


tk.Label(
    customer_frame,
    text="Name:",
    bg="#f4f6f7"
).grid(row=0, column=0)

customer_name = tk.Entry(
    customer_frame,
    width=20
)

customer_name.grid(row=0, column=1)


tk.Label(
    customer_frame,
    text="Mobile:",
    bg="#f4f6f7"
).grid(row=0, column=2)

customer_mobile = tk.Entry(
    customer_frame,
    width=15
)

customer_mobile.grid(row=0, column=3)


tk.Label(
    customer_frame,
    text="Address:",
    bg="#f4f6f7"
).grid(row=0, column=4)

customer_address = tk.Entry(
    customer_frame,
    width=20
)

customer_address.grid(row=0, column=5)


tk.Button(
    customer_frame,
    text="Add Customer",
    command=add_customer,
    bg="#1976d2",
    fg="white"
).grid(row=0, column=6, padx=10)


# ================= BILLING =================

billing_frame = tk.LabelFrame(
    root,
    text="Billing",
    font=("Arial", 13, "bold"),
    bg="#f4f6f7"
)

billing_frame.pack(
    fill=tk.X,
    padx=15,
    pady=5
)


tk.Label(
    billing_frame,
    text="Medicine:",
    bg="#f4f6f7"
).grid(row=0, column=0)

bill_medicine = tk.Entry(
    billing_frame,
    width=20
)

bill_medicine.grid(row=0, column=1)


tk.Label(
    billing_frame,
    text="Quantity:",
    bg="#f4f6f7"
).grid(row=0, column=2)

bill_quantity = tk.Entry(
    billing_frame,
    width=10
)

bill_quantity.grid(row=0, column=3)


tk.Button(
    billing_frame,
    text="Generate Bill",
    command=generate_bill,
    bg="green",
    fg="white",
    width=15
).grid(row=0, column=4, padx=10)


bill_result = tk.Label(
    billing_frame,
    text="Total: ₹0.00",
    font=("Arial", 12, "bold"),
    bg="#f4f6f7",
    justify=tk.LEFT
)

bill_result.grid(
    row=0,
    column=5,
    padx=20
)


# ================= START =================

show_medicines()

root.mainloop()