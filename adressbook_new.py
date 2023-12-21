from collections import defaultdict
from datetime import datetime, timedelta
import re
from rich.console import Console
from rich import print
from rich.table import Table



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Invalid birthday format. Use 'DD-MM-YYYY'.")
        super().__init__(value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):  
            raise ValueError("Invalid birthday format. Use 'Birthday' object.")
        self.birthday = birthday

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, name, phone, birthday=None):
        record = Record(name, birthday)
        record.add_phone(phone)
        self.data[name] = record

    def find(self, name):
        return self.data.get(name)
    
    def update_record(self, name, new_record):
        if name in self.data:
            self.data[name] = new_record
        else:
            raise KeyError(f"Contact not found: {name}")

    def delete(self, name):
        if name in self.data:
            del self.data[name]                

    def get_birthdays_per_week(self):
        birthdays_by_day = defaultdict(list)
        today = datetime.today().date()
        today_day = datetime.today().strftime("%A")

        for name, record in self.data.items():
            if record.birthday:              
                birthday = datetime.strptime(record.birthday.value, "%d-%m-%Y").date()
                birthday_this_year = birthday.replace(year=today.year) if record.birthday.value else None

                if birthday_this_year < today:
                    if ((birthday_this_year - today).days) > -3 and today_day not in ["Monday", "Sunday", "Saturday"]:
                        birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days if birthday_this_year else None

                if delta_days < 7 and delta_days >= -2:
                    birthday_weekday = (today + timedelta(days=delta_days)).strftime("%A")
                    if  delta_days is not None and delta_days < 7 and delta_days >= 0 and today_day not in ["Monday", 'Sunday', 'Saturday']:
                        if birthday_weekday in ['Sunday', 'Saturday']:
                            birthday_weekday = 'Monday'
                    elif delta_days < 7 and delta_days > 5 and today_day == "Monday":
                        continue
                    elif delta_days >= -2 and delta_days <= 0 and today_day == "Monday":
                        birthday_weekday = 'Monday'
                    elif delta_days >= -1 and delta_days == 0 and today_day == "Sunday":
                        birthday_weekday = 'Monday'
                    elif delta_days == 0 and today_day == "Sunday":
                        birthday_weekday = 'Monday'
                else:
                    continue

                birthdays_by_day[birthday_weekday].append(name)

        for day, names in birthdays_by_day.items():
            print(f"{day}: {', '.join(names)}")

   
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve) 
        except KeyError as e:
            return f"Contact not found: {e.args[0]}"
        except IndexError:
            return "Invalid command. Please provide the required arguments."

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    if len(args) != 2:
        return "Invalid command. Please provide a name and a phone number."
    name, phone = args
    book.add_record(name, phone, None)  
    return f"Contact {name} with phone {phone} added successfully."


@input_error
def change_contact(args, book):
    if len(args) != 2:
        return "Invalid command. Please provide a name and a new phone number."
    name, new_phone = args
    record = book.find(name)
    if record:
        record.remove_phone(record.phones[0].value)
        record.add_phone(new_phone)
        return "Contact updated."
    else:
        return f"Contact not found: {name}"


@input_error
def show_phone(args, book):
    if len(args) != 1:
        return "Invalid command. Please provide a name."
    name = args[0]
    record = book.find(name)
    if record:
        return f"{record.name.value}: {', '.join(str(p.value) for p in record.phones)}"
    else:
        return f"Contact not found: {name}"


#@input_error
#def show_all(args, book):
  #  if args:
  #      return "Invalid command. 'all' command doesn't require additional arguments."
  #  if book.data:
  #      for name, record in book.data.items():
  #          print(record)
  #  else:
  #      return "No contacts found."

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Invalid command. Please provide a name and a birthday (format: DD-MM-YYYY)."
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(Birthday(birthday)) 
        return f"Birthday added for {name}."
    else:
        return f"Contact not found: {name}"


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Invalid command. Please provide a name."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    elif record:
        return f"{name} has no recorded birthday."
    else:
        return f"Contact not found: {name}"


@input_error
def show_birthdays(args, book):
    if args:
        return "Invalid command. 'birthdays' command doesn't require additional arguments."
    book.get_birthdays_per_week()
    




def display_table(book, console):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Phones", style="yellow", width=40)
    table.add_column("Birthday", style="green", width=20)

    for name, record in book.data.items():
        phones_str = ', '.join(str(p.value) for p in record.phones)
        birthday_str = str(record.birthday) if record.birthday else "None"
        table.add_row(name, phones_str, birthday_str)

    console.print(table)

@input_error
def show_all(args, book, console):
    if args:
        return "Invalid command. 'all' command doesn't require additional arguments."

    if book.data:
        display_table(book, console)
    else:
        return "No contacts found."

def main():  
    console = Console()
    book = AddressBook()
    console.print("[red]Welcome to the assistant bot![/red]")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            console.print("[red]Goodbye![/red]")
            break
        elif command == "hello":
            console.print("[yellow]How can I help you?[/yellow]")
        elif command == "add":
            console.print(add_contact(args, book))
        elif command == "change":
            console.print(change_contact(args, book))
        elif command == "phone":
            console.print(show_phone(args, book))
        elif command == "all":
            show_all(args, book, console)
        elif command == "add-birthday":
            console.print(add_birthday(args, book))
        elif command == "show-birthday":
            console.print(show_birthday(args, book))
        elif command == "birthdays":
            show_birthdays(args, book)
        else:
            console.print("[blue]Invalid command.[/blue]")

if __name__ == "__main__":
    main()