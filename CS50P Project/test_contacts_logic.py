# test_contacts_logic.py
import pytest
from contacts_logic import format_contact, parse_contact, search_contacts

def test_format_contact_valid():
    result = format_contact("Alice", "123 Main St", "555-1234")
    assert result == "Alice | 123 Main St | 555-1234"

def test_format_contact_missing_name():
    with pytest.raises(ValueError):
        format_contact("", "123 Main St", "555-1234")

def test_format_contact_missing_phone():
    with pytest.raises(ValueError):
        format_contact("Alice", "123 Main St", "")

def test_parse_contact():
    contact = "Alice | 123 Main St | 555-1234"
    result = parse_contact(contact)
    assert result == ["Alice", "123 Main St", "555-1234"]

def test_search_contacts_found():
    contacts = [
        "Alice | Wonderland | 111",
        "Bob | Builder Blvd | 222",
        "Carol | Crestview | 333"
    ]
    results = search_contacts(contacts, "bob")
    assert results == ["Bob | Builder Blvd | 222"]

def test_search_contacts_case_insensitive():
    contacts = ["Alice | Wonderland | 111"]
    assert search_contacts(contacts, "ALICE") == ["Alice | Wonderland | 111"]

def test_search_contacts_no_match():
    contacts = ["Alice | Wonderland | 111"]
    assert search_contacts(contacts, "xyz") == []
