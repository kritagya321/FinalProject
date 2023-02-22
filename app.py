
from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session
from flask import jsonify

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'user'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306#8889
mysql.init_app(app)



app.secret_key = 'secret key can be anything!'


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showHome')
def showHome():
    return render_template('index.html')

@app.route('/showaboutUs')
def showaboutUS():
    return render_template('aboutUs.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/adminAddItem')
def adminAddItem():
    return render_template('adminAddItem.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
@app.route('/adminPage')
def adminPage():
    if session.get('user'):
        return render_template('adminPage.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddItem')
def showAddItem():
    return render_template('additem.html')
@app.route('/viewCart')
def viewCart():
    return render_template('viewCart.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        

        con = mysql.connect()
        cursor = con.cursor()
        

        cursor.execute("SELECT * FROM user WHERE user_email = %s", (_email))
        data = cursor.fetchall()
        
        if len(data) > 0:
            if str(data[0][3]) == _password:
                session['user'] = data[0][0]
                if data[0][4]==1:
                    return redirect('/adminPage')
                else:
                    return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

    
@app.route('/signUp',methods=['POST'])
def signUp():
    
    
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
 
    
    if _name and _email and _password:

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO user(user_name, user_email, user_password) VALUES (%s, %s, %s)", (_name, _email, _password))
        

        data = cursor.fetchall()

        if len(data) == 0:
            conn.commit()
            return json.dumps({'message':'User created successfully !'})
        else:
            return json.dumps({'error':str(data[0])})


    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})


@app.route('/addItem',methods=['POST'])
def addItem():
    try:
        if session.get('user')==1:
            _itemName = request.form['product_name']
            _description = request.form['product_description']
            _price = request.form['product_price']
            _qty = request.form['product_quantity']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO product(product_name,product_description,product_price,product_quantity) VALUES (%s,%s,%s,%s)", (_itemName,_description,_price,_qty))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return redirect('/adminPage')
            else:
                return render_template('error.html',error = 'An error Occured')
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/retrieve',methods=['GET', 'POST'])
def retrieve():
    conn = mysql.connect()
    cursor = conn.cursor()
    _user = session.get('user')
    cursor.execute("SELECT product_id,product_name,product_description,product_price,product_quantity, product_image FROM product")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/deleteItem',methods=['POST'])
def deleteItem():
    try:
        idd = request.args['id']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE product_id = %s",idd)
        conn.commit()
        return render_template('userHome.html')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/addToCart',methods=['POST'])
def addToCart():
    try:
        product_id = request.args['id']
        quantity = request.form['inputQty']
        conn = mysql.connect()
        cursor = conn.cursor()
        _user = session.get('user')
        cursor.execute("INSERT INTO cart(user_id,product_id,quantity) VALUES (%s,%s,%s)", (_user,product_id,quantity))
        conn.commit()
        return render_template('userHome.html')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/retrieveCart',methods=['GET', 'POST'])
def retrieveCart():
    print('The program is here')
    conn = mysql.connect()
    cursor = conn.cursor()
    _user = session.get('user')
    cursor.execute("Select p.product_id,p.product_name, p.product_description, p.product_price, C.quantity, p.product_image From Product as P Inner join Cart as C on C.product_id = P.Product_id Inner join User as U on U.user_id = C.user_id")
    data = cursor.fetchall()
    print(data)

    return jsonify(data)

@app.route('/updateCart',methods=['POST'])
def updateCart():
    try:
        product_id = request.args['id']
        quantity = request.form['inputQty']
        conn = mysql.connect()
        cursor = conn.cursor()
        _user = session.get('user')
        cursor.execute("UPDATE cart SET cart.quantity = %s WHERE cart.user_id = %s",(quantity,_user))
        conn.commit()
        return render_template('userHome.html')
    except Exception as e:
        return render_template('error.html',error = str(e))

    



if __name__ == "__main__":
    app.run()   

