import tkinter as tk
from tkinter import messagebox
import sqlite3


# ---------------- BACKEND ---------------- #
class HotelManagementSystem:
    def __init__(self):
        self.conn = sqlite3.connect("hotel_management.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INTEGER PRIMARY KEY,
                room_type TEXT,
                price REAL,
                availability INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                name TEXT,
                contact TEXT,
                room_booked INTEGER
            )
        """)
        self.conn.commit()

    def add_room(self, room_number, room_type, price):
        self.cursor.execute(
            "INSERT INTO rooms VALUES (?, ?, ?, ?)",
            (room_number, room_type, price, 1)
        )
        self.conn.commit()

    def view_rooms(self):
        self.cursor.execute("SELECT * FROM rooms")
        return self.cursor.fetchall()

    def book_room(self, name, contact, room_number):
        self.cursor.execute(
            "SELECT availability FROM rooms WHERE room_number=?",
            (room_number,)
        )
        row = self.cursor.fetchone()

        if not row:
            return False, "Room does not exist"
        if row[0] == 0:
            return False, "Room not available"

        self.cursor.execute(
            "UPDATE rooms SET availability=0 WHERE room_number=?",
            (room_number,)
        )
        self.cursor.execute(
            "INSERT INTO customers VALUES (?, ?, ?)",
            (name, contact, room_number)
        )
        self.conn.commit()
        return True, "Room booked successfully"

    def checkout(self, room_number):
        self.cursor.execute(
            "SELECT * FROM customers WHERE room_booked=?",
            (room_number,)
        )
        if not self.cursor.fetchone():
            return False, "No customer found"

        self.cursor.execute(
            "DELETE FROM customers WHERE room_booked=?",
            (room_number,)
        )
        self.cursor.execute(
            "UPDATE rooms SET availability=1 WHERE room_number=?",
            (room_number,)
        )
        self.conn.commit()
        return True, "Checkout successful"


# ---------------- GUI ---------------- #
class HotelGUI:
    ADMIN_USER = "admin"
    ADMIN_PASS = "admin321"

    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry("850x500")

        self.hotel = HotelManagementSystem()

        tk.Label(root, text="Hotel Management System",
                 font=("Arial", 22, "bold")).pack(pady=10)

        # Navigation bar
        nav = tk.Frame(root)
        nav.pack(pady=5)

        tk.Button(nav, text="Admin Panel", width=15,
                  command=self.show_admin_login).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Customer Panel", width=15,
                  command=self.show_customer).grid(row=0, column=1, padx=5)
        tk.Button(nav, text="View Rooms", width=15,
                  command=self.show_rooms).grid(row=0, column=2, padx=5)

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.admin_login_frame()
        self.admin_panel_frame()
        self.customer_frame()
        self.rooms_frame()

        self.show_rooms()

    def clear_frames(self):
        for widget in self.container.winfo_children():
            widget.pack_forget()

    # ---------- ADMIN LOGIN ---------- #
    def admin_login_frame(self):
        self.admin_login = tk.Frame(self.container)

        tk.Label(self.admin_login, text="Admin Login",
                 font=("Arial", 18)).pack(pady=10)

        tk.Label(self.admin_login, text="Username").pack()
        self.admin_user = tk.Entry(self.admin_login)
        self.admin_user.pack()

        tk.Label(self.admin_login, text="Password").pack()
        self.admin_pass = tk.Entry(self.admin_login, show="*")
        self.admin_pass.pack()

        tk.Button(self.admin_login, text="Login",
                  command=self.validate_admin).pack(pady=10)

    def validate_admin(self):
        if (self.admin_user.get() == self.ADMIN_USER and
                self.admin_pass.get() == self.ADMIN_PASS):
            messagebox.showinfo("Success", "Admin Login Successful")
            self.show_admin_panel()
        else:
            messagebox.showerror("Error", "Invalid Admin Credentials")

    def show_admin_login(self):
        self.clear_frames()
        self.admin_login.pack(fill="both", expand=True)

    # ---------- ADMIN PANEL ---------- #
    def admin_panel_frame(self):
        self.admin_panel = tk.Frame(self.container)

        tk.Label(self.admin_panel, text="Admin Panel",
                 font=("Arial", 18)).pack(pady=10)

        tk.Label(self.admin_panel, text="Room Number").pack()
        self.room_no = tk.Entry(self.admin_panel)
        self.room_no.pack()

        tk.Label(self.admin_panel, text="Room Type").pack()
        self.room_type = tk.Entry(self.admin_panel)
        self.room_type.pack()

        tk.Label(self.admin_panel, text="Price").pack()
        self.price = tk.Entry(self.admin_panel)
        self.price.pack()

        tk.Button(self.admin_panel, text="Add Room",
                  command=self.add_room).pack(pady=10)

    def add_room(self):
        try:
            self.hotel.add_room(
                int(self.room_no.get()),
                self.room_type.get(),
                float(self.price.get())
            )
            messagebox.showinfo("Success", "Room Added Successfully")
            self.show_rooms()
        except:
            messagebox.showerror("Error", "Invalid Input")

    def show_admin_panel(self):
        self.clear_frames()
        self.admin_panel.pack(fill="both", expand=True)

    # ---------- CUSTOMER ---------- #
    def customer_frame(self):
        self.customer = tk.Frame(self.container)

        tk.Label(self.customer, text="Customer Panel",
                 font=("Arial", 18)).pack(pady=10)

        tk.Label(self.customer, text="Name").pack()
        self.c_name = tk.Entry(self.customer)
        self.c_name.pack()

        tk.Label(self.customer, text="Contact").pack()
        self.c_contact = tk.Entry(self.customer)
        self.c_contact.pack()

        tk.Label(self.customer, text="Room Number").pack()
        self.c_room = tk.Entry(self.customer)
        self.c_room.pack()

        tk.Button(self.customer, text="Book Room",
                  command=self.book_room).pack(pady=5)
        tk.Button(self.customer, text="Checkout",
                  command=self.checkout).pack(pady=5)

    def book_room(self):
        success, msg = self.hotel.book_room(
            self.c_name.get(),
            self.c_contact.get(),
            int(self.c_room.get())
        )
        messagebox.showinfo("Info", msg)
        self.show_rooms()

    def checkout(self):
        success, msg = self.hotel.checkout(int(self.c_room.get()))
        messagebox.showinfo("Info", msg)
        self.show_rooms()

    def show_customer(self):
        self.clear_frames()
        self.customer.pack(fill="both", expand=True)

    # ---------- ROOMS ---------- #
    def rooms_frame(self):
        self.rooms = tk.Frame(self.container)

        tk.Label(self.rooms, text="Room Details",
                 font=("Arial", 18)).pack(pady=10)

        self.room_list = tk.Listbox(self.rooms, width=80)
        self.room_list.pack(pady=10)

    def show_rooms(self):
        self.clear_frames()
        self.room_list.delete(0, tk.END)

        for r in self.hotel.view_rooms():
            status = "Available" if r[3] else "Booked"
            self.room_list.insert(
                tk.END,
                f"Room {r[0]} | {r[1]} | ₹{r[2]} | {status}"
            )

        self.rooms.pack(fill="both", expand=True)


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    HotelGUI(root)
    root.mainloop()
