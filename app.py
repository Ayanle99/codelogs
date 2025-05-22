from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    user = {
        'username': 'max',
        'email': 'max@example.com',
        'info': 'about page'
    }
    return  render_template('about.html', title='About', user=user)

if __name__ == '__main__':
    app.run(debug=True)

