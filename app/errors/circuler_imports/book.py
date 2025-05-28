# this only be executed when the main file author = Author() is instantiate and write_book() is execute
from author import Author

class Book:
    def __init__(self, title: str, author: 'Author'):  # This causes circular reference
        self.title = title
        self.author = author
