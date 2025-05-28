# main.py ( entry point for the program)
from author import Author
# the interpreter pauses here, the interpreter goes to author.py

a = Author("Orwell")
a.write_book("1984")



# Circular Import Example

# author.py

# from Book import Book
#
# class Author:
#     def __init__(self, name):
#         self.name = name
#         self.books = []
#
#     def add_book(self, book: Book):
#         self.books.append(book)

# book.py

# from Author import Author
#
# class Book:
#     def __init__(self, title, author: Author):
#         self.title = title
#         self.author = author



# main.py (main entry point for the Python interpreter)

# from Author import Author
# from Book import Book
#
# author = Author("J.K. Rowling")
# book = Book("Harry Potter", author)
# author.add_book(book)

# Error you most likely get in the terminal is:
# ImportError: cannot import name 'Author' from partially initialized module 'author' (most likely due to a circular import)

# End Circuler Imports Version

#________________________________________________#

# author.py

# class Author:
#     def __init__(self, name):
#         self.name = name
#         self.books = []
#     def write_book(self, title):
#         # only import the book when author class is already loaded in memory
#         from book import Book  # Local import avoids circular issue
#         new_book = Book(title, self)
#         self.books.append(new_book)
#

# book.py

# from author import Author
#
# class Book:
#     def __init__(self, title: str, author: 'Author'):  # This causes circular reference
#         self.title = title
#         self.author = author


# main.py

# from author import Author
#
# a = Author("Orwell")
# a.write_book("1984")
#
# main.py > autho from AUthor
# author  > import book from Book  circuler
# bookk >import Author from author

#__________________________________________#

# Python Interpreter Flow:

# 1. main.py opens: Interpreter starts at the top, importing Author from author.py.
# 2. In author.py: Interpreter starts at the top again. Since there are no imports at the top level, the interpreter continues from top to bottom and loads the Author class definition without executing the __init__ function or write_book function. It then goes back to main.py
# 3. In main.py: The interpreter sees a = Author("Orwell"), then goes to author.py and executes the __init__ function. The interpreter comes back to main.py and sees the line a.write_book("1984"). It goes back to author.py and executes the write_book() function in the Author class.
# 4. Inside write_book(): When from book import Book appears, the interpreter pauses and jumps to book.py, starting from the top. It tries to import Author from author.py, but since Author is already in memory and loaded, the interpreter continues with the file contents and loads the Book class into memory.
# 5. Back to write_book(): The interpreter returns to the write_book() method, creates the Book instance, adds it to the books list, and then returns to main.py where execution finishes.


