from collections import UserDict
import csv
from datetime import datetime
from pathlib import Path
import re


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return self.__str__()    

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):
    def __init__(self, name):
        super().__init__(name)
    

class Phone(Field):
    def __init__(self, phone):
        if phone:
            if phone.isdigit():
                self.phone = phone
            else:
                self.phone = None
                print('bot>> Error, phone must contain only digits')
        super().__init__(phone)

    # @Field.value.setter
    # def value(self, value: str):
    #     if value.isdigit():
    #         self.__value = value
    #         # print('Field.value.setter ',value, self.value)
    #     else:
    #         self.__value = None
    #         print('bot>> Error, phone must contain only digits')


class Birthday(Field):
    def __init__(self, birthday: str):  #format: 'dd.mm.YYYY or dd/mm/YYYY or dd-mm-YYYY'
        if birthday:
            self.data_str = re.sub(r'[/-]', '.', birthday.strip())
            try:
                data = datetime.strptime(self.data_str, '%d.%m.%Y')
            except ValueError as err:
                print('bot>> Error, ' + str(err))
            else:
                self.data = data 
        else:
            self.data_str = ''

        # super().__init__(data)

    # @Field.value.setter
    # def value(self, birthday: str):
    #     self.data_str = re.sub(r'[/-]', '.', birthday.strip())
    #     try:
    #         data = datetime.strptime(self.data_str, '%d.%m.%Y')
    #     except ValueError as err:
    #         print('bot>> Error, ' + str(err))
    #     else:
    #         self.__value = data            

    def __str__(self):
        return self.data_str

class Record:
    def __init__(self, name: Name, phone=None, birthday=None): 
        self.name = name
        self.phones = []
        
        if phone:
            if type(phone) is Phone:                
                if phone.value:
                    self.phones.append(phone)
            else:
                print('bot>> Error. phone must be an object of class Phone!')

        if birthday:
            if type(birthday) is Birthday:
                self.birthday = birthday
            else:
                print('bot>> Error, birthday must be an object of class Birthday!')

    def __str__(self):
        return f'# {self.name}: {self.phones} ({self.birthday})' # '#' - разделитель записей

    def __repr__(self):
        return self.__str__()
    
    def show_rec(self):
        return self.__str__()
    
    def add_new_phone(self, new_phone):
        if type(new_phone) is Phone:
            self.phones.append(new_phone)
        else:
            self.phones.append(Phone(new_phone))

    def del_phone(self, phone=''):
        if not phone:
            self.phones.pop()  #delete the last phone number
        else:
            phone = phone.strip()
            if phone in self.phones:
                self.phones.remove(phone)
                return 'Phone number was deleted'
            else:
                return 'Error. This number is not in the phone list'


    def change_bd(self, bd: str): #format: 'dd.mm.YYYY or dd/mm/YYYY or dd-mm-YYYY'
        self.birthday = Birthday(bd)

    def days_to_birthday(self):
        current = datetime.now()
        d = self.birthday.data.day
        m = self.birthday.data.month
        next_bd = datetime(year=current.year, month=m, day=d)
        delta = next_bd - current
        if delta.days < 0:
            next_bd = datetime(year=current.year+1, month=m, day=d)
            delta = next_bd - current
            
        return delta.days + 1
        

class AddressBook(UserDict):
    quant_iter = 3 # генератор за записами AddressBook за одну ітерацію повертає представлення для N записів
    current_index = 0
    def __iter__(self):
        return self

    def __next__(self): 
        out_list = []
        if self.current_index < len(self):
            for i, record in enumerate(self.data.values()):
                if i < self.current_index:
                    continue
                elif self.current_index <= i < self.current_index + self.quant_iter:
                    out_list.append(record)
                else:
                    break
            
            self.current_index += self.quant_iter
            return out_list
        
        else:
            raise StopIteration

    def add_record(self, record):
        self.data[record.name.value] = record

    def del_record(self, name):
        if name not in self.data:
            print(f'bot>> Record with the name {name} not found')
        else:
            self.data.pop(name)
            # write_AB(path_file, self)
            

    def show_all_names(self):
        return f'bot>> {list(self.data)}'


    def change_name(self, old_name: str, new_name: str):
        if old_name not in self.data:
           return f'bot>> Record with the name {old_name} not found'
        else:
            temp_record = self.data[old_name]
            self.del_record(old_name)
            temp_record.name = Name(new_name)
            self.data[new_name] = temp_record
            return 'bot>> Name changed'
            # write_AB(path_file, self)


    def find_name(self, part_str): #Search by part of a name 
        list_names = list(self.data)
        out_list = []
        for name in list_names:
            if part_str in name:
                out_list.append(name)
        if not out_list:
            return 'bot>> Nothing was found.'     
        else:
            return 'bot>> ' + str(out_list)

    def find_phone(self, part_number): #Search by part of a phone number 
        list_names = list(self.data)
        out_dict = {}
        for name in list_names:
            list_phones = []
            for phone in self.data[name].phones:
                if part_number in phone.value:
                    list_phones.append(phone)
                    if name not in out_dict:
                        out_dict[name] = list_phones
        if not out_dict:
            return 'bot>> Nothing was found.'     
        else:
            return 'bot>> ' + str(out_dict)



################################################################################
def help_bot():
    help_text = '''    List of available commands:
    "good bye", "close", "exit" - for exit the bot
    "hello" - ?
    "help" - Display a list of commands
    "show all" - Show all names from AddressBook
    "add" - Add new record on AddressBook -> add <name>(, <phone>, <birthday>)
    "del" - Delete record from the AddressBook -> del <name>
    "find" - Search by part of a name or part of a phone number -> find <str>
    "enter" - Select an entry to edit -> enter <name>
    In record: 
        "back" - Exit the entry to save changes
        "help" - Display a list of commands
        "show" - Show all data from the record
        "del" - Delete this record from the AddressBook
        "change name" - Change the name -> change name <new name>
        "change bd" - Change date of birth -> change bd <new bd> #format: dd.mm.YYYY or dd/mm/YYYY or dd-mm-YYYY
        "del phone" - Delete phone number. The last, if no number is specified -> del phone <phone>
        "add phone" - Add phone number -> add phone <phone>
        "days bd" - Calculate the days to the next birthday'''
    return help_text
    
################################################################################

def read_AB(path):  #read AddressBook from file    
    if path.exists():
        AB = AddressBook()
        with open(path, 'r', newline='', encoding='utf-8') as file:  #'cp1251'
            reader = csv.DictReader(file)
            field_names = reader.fieldnames #list(list(reader)[0])
            for row in reader:
                name = Name(row[field_names[0]])
                phones = row[field_names[1]].strip("[']").replace("'", '').replace('"', '').split(', ')
                phone = Phone(phones[0])
                bd = Birthday(row[field_names[2]])
                rec = Record(name, phone, bd)
                if len(phones) > 1:
                    for i in range(1, len(phones)):
                        rec.add_new_phone(Phone(phones[i]))
                
                AB.add_record(rec)
        return AB
    else:
        print('bot>> path in not exists!')


def sort_dict(obj):   # sorts and converts in dict
    return dict(sorted(obj.items()))


def write_AB(path, adr_book):    #write AddressBook in file
    if not len(adr_book):
        print('bot>> AddressBook is empty!')
    else:
        adr_book = sort_dict(adr_book.data)
        # field_names = list(adr_book.data[list(adr_book.data)[0]].__dict__) # if type(adr_book) = class AddressBook
        field_names = list(adr_book[list(adr_book)[0]].__dict__) # if type(adr_book) = dict
        with open(path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            for rec in adr_book.values():
                writer.writerow(rec.__dict__)

        # print('bot>> AddressBook writed in file ok!')


# def input_error(func):
#     def inner(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except KeyError:
#             return 'bot>> Contact not found'
#         except ValueError:
#             return 'bot>> Invalid input'
#         except IndexError:
#             return 'bot>> Invalid data'
#     return inner



def parser(input_str):
    if input_str.strip().lower() in ["good bye", "close", "exit"]:
        return 'bot>> Good bye!'
    
    elif input_str.strip().lower().startswith('hello'):
        return 'bot>> How can I help you?'
    
    elif input_str.strip().lower().startswith('help'):
        return help_bot()
    
    elif 'show all' in input_str.strip().lower():
        return AB.show_all_names()
    
    elif input_str.strip().lower().startswith('add'):
        data = input_str[3:].strip().split(',')
        if len(data) > 3:
            return 'bot>> Error. Incorrect data!'
        else:
            if len(data) > 0:
                if not data[0]:
                    return 'bot>> Repeat please at least with the name'
                else:
                    name = data[0].strip()

            if len(data) > 1:
                phone = data[1].strip()
            else:
                phone = ''

            if len(data) > 2:
                bd = data[2].strip()
            else:
                bd = ''
            
        AB.add_record(Record(Name(name), Phone(phone), Birthday(bd)))
        return 'bot>> Record added'
    
    elif input_str.strip().lower().startswith('del'):
        name = input_str[3:].strip()
        if name in list(AB.data):
            AB.data.pop(name)

        return 'bot>> Record deleted'
        # 'Do you really want to delete it? y/n'

    elif input_str.strip().lower().startswith('find'):
        part = input_str[4:].strip()
        if part.isdigit():
            return AB.find_phone(part)

        else:
            return AB.find_name(part)

    else:
        return 'bot>> Command was not identified, repeat please'
    


def parser_for_record(input_str, name):
    if input_str.strip().lower().startswith('help'):
        return help_bot()
    
    elif input_str.strip().lower().startswith('show'):
        return f'bot>>{name}>>> ' + AB[name].show_rec()
    
    elif input_str.strip().lower().startswith('del'):
        y = input(f'bot>>{name}>>> Do you really want to delete this record? y/n\n')
        if y == 'y':
            AB.del_record(name)
            return f'bot>> Record with the name {name} deleted'
        
    elif input_str.strip().lower().startswith('change name'):
        new_name = input_str[11:].strip()
        return AB.change_name(name, new_name)

    elif input_str.strip().lower().startswith('change bd'):
        new_bd = input_str[9:].strip()
        AB[name].change_bd(new_bd)
        return f'bot>>{name}>>>' # Date of birth was changed  ...maybe
    
    elif input_str.strip().lower().startswith('del phone'):
        phone = input_str[9:].strip()
        return f'bot>>{name}>>> ' + AB[name].del_phone(phone)

    elif input_str.strip().lower().startswith('add phone'):
        phone = input_str[9:].strip()
        AB[name].add_new_phone(phone)
        return f'bot>>{name}>>> ' # Phone number was added  ...maybe
    
    elif input_str.strip().lower().startswith('days bd'):
        return f'bot>>{name}>>> ' + str(AB[name].days_to_birthday()) + ' days until his next birthday'

    else:
        return f'bot>>{name}>>> Command was not identified, repeat please'




def main():
    print('Welcome to the AddressBook bot!')
    print('Enter the word "help" to display a list of commands')
    while True:
        input_str = input('bot>> ')
        if not input_str.strip().lower().startswith('enter'):
            out_str = parser(input_str)
            print(out_str)
            if out_str == 'bot>> Good bye!': 
                write_AB(path_file, AB)
                break
            
        else:
            name = input_str[5:].strip()
            if name not in AB.data:
                print(f'bot>> Record with the name {name} not found')
            else:
                while True:
                    input_str = input(f'bot>>{name}>>> ')
                    if input_str.strip().lower().startswith('back'):
                        break
                    else:
                        out_str = parser_for_record(input_str, name)
                        print(out_str)
                        if out_str in [f'bot>> Record with the name {name} deleted', 'bot>> Name changed']: 
                            write_AB(path_file, AB)
                            break
            
    
if __name__ == "__main__":
    path_file = Path(__file__).parent / 'AddressBook.csv'
    AB = read_AB(path_file)  #AddressBook -> dict
    main()




    # for k in AB:
    #     print(k)
    #     input('--Press Enter--')

    
