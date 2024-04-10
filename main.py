from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        if name is None:
            raise ValueError("Name cannot be empty")
        super().__init__(name)


class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError("Phone number must be a string of 10 digits")


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, '%d.%m.%Y').date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = list()
        self.birthday = None

    def add_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                print(f"Phone number {phone_number} deleted")
                return
        else:
            print(f"Phone number {phone_number} not found")

    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number
                return
        else:
            print(f"Phone number {old_phone_number} not found")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        print(f"Phone number {phone_number} not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def __repr__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        name = record.name.value
        self.update({name: record})

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        del self[name]
        print(f"Record {name} deleted")

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.values():
            if record.birthday:
                if today.isocalendar()[1] == record.birthday.date.isocalendar()[1]:
                    upcoming_birthdays.append(record)

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        if not args:
            print("Missing arguments. Provide necessary arguments for the command.")
            return "Missing arguments"
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone"
        except KeyError:
            return "Contact not found"
        except IndexError:
            print("Missing arguments")
            return "Incomplete command. Provide necessary arguments"
        except Exception as e:
            return str(e)

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args

    if not name.replace(" ", "").isalpha():
        return "The name must include letters only."

    if len(phone) != 10 or not phone.isdigit():
        return "The phone must consist of 10 digits."

    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        if old_phone in [phone.value for phone in record.phones]:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated successfully"
        else:
            return "Old phone number not found for this contact"
    else:
        return "Contact not found"


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"Contact name: {record.name.value}, phones: {'; '.join(str(phone) for phone in record.phones)}"
    else:
        return "Contact not found"


@input_error
def show_all(book: AddressBook):
    if book:
        return "\n".join([f"{name}: {phone}" for name, phone in book.items()])
    else:
        return "No contacts found"


@input_error
def add_birthday(args, book: AddressBook):
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        print("Birthday added.")
    else:
        print("Contact not found")


@input_error
def show_birthday(name, book: AddressBook):
    name = name[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"{name}'s birthday: {record.birthday}")
    elif record:
        print(f"{name} doesn't have a birthday set.")
    else:
        print("Contact not found")


@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(
            [f"Upcoming birthdays this week: \n {record.name.value}:  {record.birthday.date.strftime('%d.%m')}"
             for record in upcoming_birthdays
             ])
    else:
        return "No upcoming birthdays this week."


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            if book:
                for record in book.values():
                    print(record)
            else:
                print("No contacts found")

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            print(birthdays(book))

        elif command == "remove-phone":
            if len(args) != 2:
                print("Missing arguments. Provide name and phone number to remove.")
                continue
            else:
                name, phone_number = args
                if record := book.find(name):
                    record.remove_phone(phone_number)
                else:
                    print("Contact not found")

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
