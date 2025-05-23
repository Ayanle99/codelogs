from flask import Flask, render_template, flash, redirect, url_for
import os
from forms import LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


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


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Logged in user: {form.username.data}, remember me? {form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title="Login", form=form)

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