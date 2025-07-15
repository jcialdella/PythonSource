import tkinter as tk
from tkinter import messagebox, filedialog
import csv

contacts = []

def add_contact():
    name = name_entry.get().strip()
    address = address_entry.get().strip()
    phone = phone_entry.get().strip()
    if not name or not phone:
        messagebox.showwarning("Input Error", "Name and phone are required.")
        return
    contact = f"{name} | {address} | {phone}"
    contacts.append(contact)
    contact_listbox.insert(tk.END, contact)
    clear_fields()
    status_label.config(text=f"Added: {name}")

def clear_fields():
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)

def clear_contacts():
    if messagebox.askyesno("Clear All", "Are you sure you want to delete all contacts?"):
        contacts.clear()
        contact_listbox.delete(0, tk.END)
        status_label.config(text="Contact list cleared.")

def save_contacts():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filepath:
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Address", "Phone"])
            for contact in contacts:
                writer.writerow(contact.split(" | "))
        status_label.config(text=f"Saved to {filepath}")

def load_contacts():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        contacts.clear()
        contact_listbox.delete(0, tk.END)
        with open(filepath, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                contact = f"{row['Name']} | {row['Address']} | {row['Phone']}"
                contacts.append(contact)
                contact_listbox.insert(tk.END, contact)
        status_label.config(text=f"Loaded from {filepath}")

def search_contacts(event=None):
    query = search_entry.get().strip().lower()
    contact_listbox.delete(0, tk.END)
    for contact in contacts:
        if query in contact.lower():
            contact_listbox.insert(tk.END, contact)
    status_label.config(text=f"Search results for: {query}")

def on_select(event):
    if not contact_listbox.curselection():
        return
    index = contact_listbox.curselection()[0]
    selected = contacts[index].split(" | ")
    name_entry.delete(0, tk.END)
    name_entry.insert(0, selected[0])
    address_entry.delete(0, tk.END)
    address_entry.insert(0, selected[1])
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, selected[2])

def update_contact():
    index = contact_listbox.curselection()
    if not index:
        messagebox.showinfo("Edit Contact", "Select a contact to update.")
        return
    name = name_entry.get().strip()
    address = address_entry.get().strip()
    phone = phone_entry.get().strip()
    if not name or not phone:
        messagebox.showwarning("Input Error", "Name and phone are required.")
        return
    new_contact = f"{name} | {address} | {phone}"
    contacts[index[0]] = new_contact
    contact_listbox.delete(index)
    contact_listbox.insert(index, new_contact)
    status_label.config(text=f"Updated: {name}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Elegant Address Book")

# Use a dedicated frame for clean layout
form_frame = tk.Frame(root)
form_frame.grid(row=0, column=0, padx=10, pady=10)

# Input Fields
tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
tk.Label(form_frame, text="Address:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
tk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky="e", padx=5, pady=2)

name_entry = tk.Entry(form_frame, width=40)
address_entry = tk.Entry(form_frame, width=40)
phone_entry = tk.Entry(form_frame, width=40)

name_entry.grid(row=0, column=1, padx=5, pady=2)
address_entry.grid(row=1, column=1, padx=5, pady=2)
phone_entry.grid(row=2, column=1, padx=5, pady=2)

# Buttons (aligned in a row)
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, pady=5)

tk.Button(button_frame, text="Add", width=15, command=add_contact).grid(row=0, column=0, padx=2)
tk.Button(button_frame, text="Update", width=15, command=update_contact).grid(row=0, column=1, padx=2)
tk.Button(button_frame, text="Clear All", width=15, command=clear_contacts).grid(row=0, column=2, padx=2)
tk.Button(button_frame, text="Save", width=15, command=save_contacts).grid(row=0, column=3, padx=2)
tk.Button(button_frame, text="Load", width=15, command=load_contacts).grid(row=0, column=4, padx=2)

# Search bar
search_frame = tk.Frame(root)
search_frame.grid(row=2, column=0, pady=(5, 0))
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", search_contacts)
tk.Button(search_frame, text="Search", command=search_contacts).pack(side="left")

# Contact list
contact_listbox = tk.Listbox(root, width=70, height=10)
contact_listbox.grid(row=3, column=0, padx=10, pady=5)
contact_listbox.bind("<<ListboxSelect>>", on_select)

# Status
status_label = tk.Label(root, text="", anchor="w", fg="darkgreen")
status_label.grid(row=4, column=0, sticky="we", padx=10, pady=(0, 5))

root.mainloop()