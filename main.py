from flask import Flask, render_template, request, session
import pymysql as mysql
from datetime import date

db = mysql.connect(host="localhost",user="root",
                   password="password", database="Enterprise")

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/Home')
def home():
    return render_template('home.html')

@app.route('/Mac')
def mac():
    cursor = db.cursor()
    sql = "SELECT model_id,name,price, group_concat(configuration_specific) "\
          "FROM model_configurations NATURAL LEFT OUTER JOIN "\
          "stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND(name='iMac' OR name='Mac Mini' OR "\
          "name='MacBook Pro' OR name='MacBook') GROUP BY model_id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('mac.html', results=results)

@app.route('/iPod')
def ipad():
    cursor = db.cursor()
    sql = "SELECT model_id,name,price, group_concat(configuration_specific) "\
          "FROM model_configurations NATURAL LEFT OUTER JOIN "\
          "stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND name='iPod' GROUP BY model_id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('ipod.html',results=results)

@app.route('/iPhone')
def iphone():
    cursor = db.cursor()
    sql = "SELECT model_id,name,price, group_concat(configuration_specific) "\
          "FROM model_configurations NATURAL LEFT OUTER JOIN "\
          "stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND name='iPhone' GROUP BY model_id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('iphone.html',results=results)

@app.route('/Watch')
def watch():
    cursor = db.cursor()
    sql = "SELECT model_id,name,price, group_concat(configuration_specific) "\
          "FROM model_configurations NATURAL LEFT OUTER JOIN "\
          "stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND name='Apple Watch' GROUP BY model_id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('watch.html',results=results)

@app.route('/Apps')
def apps():
    return render_template('home.html')

@app.route('/Music')
def music():
    return render_template('home.html')

@app.route('/Other')
def other():
    cursor = db.cursor()
    sql = "SELECT model_id,brand,name,price "\
          "FROM stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND name<>'iPod' AND name<>'Apple Watch' AND name<>"\
          "'MacBook' AND name<>'iMac' AND name<>'Mac Mini' AND "\
          "name<>'MacBook Pro' AND name<>'iPhone' AND name<>'Apple Watch'"\
          " GROUP BY model_id"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('other.html',results=results)

@app.route('/Cart')
def cart():
    if 'cart' in session and len(session['cart'])>0:
        return render_template('cart.html',results=get_cart())
    else:
        return render_template('cart.html')

@app.route('/add_to_cart',methods=['POST'])
def add_to_cart():
    model = request.form.get('addtocart')
    if 'cart' in session and session['cart'] is not None:
        cart_list = session['cart']
        cart_list.append(model)
        session['cart'] = cart_list
        print("add " + str(model))
    else:
        session['cart'] = [model]
        print(str(model))
    print(session['cart'])
    return render_template('cart.html',results=get_cart())

@app.route('/clear_cart',methods=['POST'])
def clear_cart():
    session.pop('cart',None)
    return render_template('cart.html')

@app.route('/remove_from_cart',methods=['POST'])
def remove_from_cart():
    cart_list = session['cart']
    cart_list.remove(request.form.get('removefromcart'))
    session['cart'] = cart_list
    if len(cart_list) > 0:
        return render_template('cart.html',results=get_cart())
    else:
        return render_template('cart.html')

@app.route('/purchase_cart',methods=['POST'])
def purchase_cart():
    if 'cart' in session and len(session['cart'])>0:
        name = str(request.form['account_name'])
        print("name: "+name)
        # get their apple_id
        cursor = db.cursor()
        sql = "SELECT apple_id FROM apple_account WHERE name='"+name+"'"
        cursor.execute(sql)
        account_id = cursor.fetchone()[0]
        print(account_id)

        # insert into checkout
        today = date.today()
        today = today.strftime('%Y-%m-%d %H')
        sql = "INSERT INTO checkout(date,payment_method,store_id,apple_id) "\
              "VALUES ('"+today+"','Bitcoin',1,"+str(account_id)+")"
        cursor.execute(sql)
        db.commit()
    
        # get the checkout id
        sql = "SELECT checkout_id FROM checkout WHERE apple_id="+str(account_id)+\
              " ORDER BY checkout_id DESC LIMIT 1"
        cursor.execute(sql)
        checkout_id = cursor.fetchone()[0]
        print(checkout_id)
    
        # insert models into product_purchases
        for model in session['cart']:
            # get the current cost
            sql = "SELECT price FROM stock WHERE store_id=1 AND model_id="+str(model)
            cursor.execute(sql)
            cost = cursor.fetchone()[0]
            sql = "INSERT INTO product_purchases(model_id,checkout_id,cost)"\
                  " VALUES("+str(model)+","+str(checkout_id)+","+str(cost)+")"
            cursor.execute(sql)
            db.commit()
        models=get_cart()
        session.pop('cart',None)
        return render_template('purchase_successful.html',results=models)
    else:
        return render_template('cart.html')

def get_cart():
    cursor = db.cursor()
    sql = "SELECT model_id,name,price, group_concat(configuration_specific) "\
          "FROM model_configurations NATURAL RIGHT OUTER JOIN "\
          "stock NATURAL LEFT OUTER JOIN model NATURAL LEFT OUTER JOIN "\
          "product WHERE store_id=1 AND ("
    for model in session['cart']:
        sql += "model_id="+str(model)+" OR "
    sql = sql[:len(sql)-4]+") GROUP BY model_id"
    cursor.execute(sql)
    return cursor.fetchall()

if __name__ == "__main__":
    app.run(debug=True)
