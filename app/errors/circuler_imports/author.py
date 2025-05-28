# Error version, the book is imported here

class Author:
    def __init__(self, name):
        self.name = name
        self.books = []

    def write_book(self, title):
        # here is how to fix the circuler imports, to delay the import until the class is loaded
        from book import Book  # Local import avoids circular issue
        new_book = Book(title, self)
        self.books.append(new_book)
