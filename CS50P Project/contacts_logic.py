# contacts_logic.py
def format_contact(name, address, phone):
    if not name or not phone:
        raise ValueError("Name and phone are required.")
    return f"{name} | {address} | {phone}"

def parse_contact(contact_str):
    return contact_str.split(" | ")

def search_contacts(contacts, query):
    query = query.strip().lower()
    return [c for c in contacts if query in c.lower()]
