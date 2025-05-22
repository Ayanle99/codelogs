from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    books = [
        {
            'title': 'The River War',
            'author': 'Winston Spencer Churchill',
            'pages': 350
        },
        {
            'title': 'FIVE WEEKS IN A BALLOON',
            'author': 'Jules Verne',
            'pages': 300
        }
    ]
    return render_template('index.html', title='Home', books=books)

@app.route('/about')
def about():
    user = {
        'author': 'max',
        'email': 'max@example.com',
        'info': 'About Page'
    }
    return render_template('about.html', title='About', user=user)


if __name__ == '__main__':
    app.run(debug=True)