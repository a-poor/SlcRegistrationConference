"""
SLC Flask Registration
Created by Austin Poor

Repo: https://github.com/a-poor/SlcRegistrationConference
"""    

    
from flask import Flask, render_template, request, flash, session, escape, redirect, url_for 

from RegDB import RegDB


DB_PATH = 'db/slc_reg.db'


app = Flask(__name__)

app.secret_key = b'\x06t\x82P{\x1b\xc6\x04p\x16\x0e\xb2\xcb\xf7\x01\x9d'
 

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        username = None
    else:
        username = session['username']
    return render_template('index.html', username=username)

@app.route('/results', methods = ['POST', 'GET'])
def result():
    if 'username' not in session:
        username = None
    else:
        username = session['username']
    if 'cart' not in session:
        session['cart'] = []
        existing_cart = []
    else:
        existing_cart = session['cart']
    rdb = RegDB()
    form_response = request.form
    keyword = form_response['keyword']
    search_results = rdb.pull_courses(form_response)
    return render_template("results.html", keyword=keyword, search_results=search_results, username=username, existing_cart=','.join(existing_cart))


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    rdb = RegDB()
    if 'username' not in session:
        username = None
        saved_cart = []
    else:
        username = session['username']
        saved_cart = rdb.get_cart(username)
    if 'cart' not in session:
        cart = saved_cart[:]
    else:
        cart = session['cart']
        for c in saved_cart:
            if c not in cart:
                cart.append(c)
    if request.method == 'POST' and 'results' in request.referrer:
        cart = set(cart)
        cart_add = request.form['add'].split(',')
        cart_del = request.form['del'].split(',')
        for course in cart_del:
            if course in cart:
                cart.remove(course)
        for course in cart_add:
            cart.add(course)
        cart = list(cart)
        session['cart'] = cart
    elif request.method == 'POST' and 'cart' in request.referrer:
        dropClass = request.form['dropClass']
        cart = set(session['cart'])
        if dropClass in cart:
            cart.remove(dropClass)
        if username is not None:
            print('Deleteing %s from %s cart' % (dropClass, username))
            rdb.del_class_from_cart(username, dropClass)
        cart = list(cart)
        session['cart'] = cart
    if username is not None:
        for c in cart:
            if c not in saved_cart:
                rdb.add_class_to_cart(username, c)
        for c in saved_cart:
            if c not in cart:
                rdb.del_class_from_cart(username, c)
    course_info = sorted([rdb.get_course_info(id)[0] for id in cart])
    cart_conflicts = rdb.formatted_conflicts(cart)
    return render_template('cart.html', username=username, cart_info=course_info, cart_conflicts=cart_conflicts)

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signout')
def signout():
    if 'username' in session:
        del session['username']
    if 'cart' in session:
        del session['cart']
    return redirect('/')


@app.route('/authuser', methods=['POST'])
def authuser():
    referrer = request.referrer
    if '/signin' in referrer:
        email = request.form['email']
        password = request.form['password']
        rdb = RegDB()
        if rdb.confirm_login(email, password):
            # Successfully logged in! Add username to session
            session['username'] = email
            session['cart'] = []
            return redirect('/')
        else:
            # Couldn't login. Redirect back to signin
            print('ERROR! u/p didnt match. Redirecting back to signin.')
            return redirect('/signin')
        pass
    elif '/signup' in referrer:
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        v_password = request.form['verrify'].strip()
        if '' in [email, password, v_password] or password != v_password:
            # One of the form fields was empty or passwords didn't match
            print('ERROR! One of the form fields was empty or passwords didnt match')
            return redirect('/signup')
        rdb = RegDB()
        if not rdb.user_already_exists(email):
            rdb.add_user(email, password)
            session['username'] = email
            session['cart'] = []
            return redirect('/')
        else:
            print('ERROR! username already exists')
            return redirect('/signup')
    else:
        return redirect('/')

@app.route('/schedules')
def schedules():
    if 'username' not in session:
        username = None
    else:
        username = session['username']
    if 'cart' not in session:
        cart = []
    else:
        cart = session['cart']

    rdb = RegDB()
    schedules = rdb.cart_to_schedules(cart)

    schedules_of_names = [{
            'liTextA': s[0][0]['course_title'],
            'liTextB': s[1][0]['course_title'],
            'liTextC': s[2][0]['course_title']
         } for s in schedules]

    return render_template('schedules.html', schedules_of_names=schedules_of_names,  schedule_dict=schedules)


if __name__ == '__main__':
    app.run(debug = True)

