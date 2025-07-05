from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
import uuid
import os
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "9a4f90b2b6df594f2e16f6c1f3d9e0ab0cd431c0f0176a2544e740c94cb75a0e"

# --------------------------------------------------
# DynamoDB Setup
# --------------------------------------------------
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # change if needed
cart_table = dynamodb.Table("PickleShop_Carts")  # Your DynamoDB table name

# --------------------------------------------------
# Dummy Product Catalogs
# --------------------------------------------------
veg_products = [
    {"id": 101, "name": "Avakaya Pickle", "price": 110, "image": "Avakaya pickle.jpg"},
    {"id": 102, "name": "Amla Pickle", "price": 100, "image": "Amla pickle.jpg"},
    {"id": 103, "name": "Tomato Pickle", "price": 95, "image": "Tomato pickle.jpg"},
    {"id": 104, "name": "Lemon_Pickle", "price": 90, "image": "lemon_pickle.jpg"},
    {"id": 105, "name": "Mixed Pickle", "price": 105, "image": "mixed pickle.jpg"},
    {"id": 106, "name": "Gongura Pickle", "price": 120, "image": "gongura pickle.jpg"},
    {"id": 107, "name": "Pickles Box", "price": 250, "image": "pickles boxes.jpg"},
    {"id": 108, "name": "Mixed Veg Pickle", "price": 100, "image": "pickles.jpg"},
]
non_veg_products = [
    {"id": 201, "name": "Mutton Pickle", "price": 180, "image": "MuttonPickle.jpg"},
    {"id": 202, "name": "Chicken Pickle", "price": 160, "image": "Chicken_pickle.jpg"},
    {"id": 203, "name": "Prawn Pickle", "price": 200, "image": "prawn pickle.jpg"},
    {"id": 204, "name": "Fish Boneless Pickle", "price": 170, "image": "fish boneless pickle.jpg"},
    {"id": 205, "name": "Gongura Chicken Pickle", "price": 190, "image": "Gongura chicken pickle.jpg"},
    {"id": 206, "name": "Gongura Prawns Pickle", "price": 195, "image": "Gongura prawns pickle.jpg"},
    {"id": 207, "name": "Premium Mutton Pickle 500 g", "price": 500, "image": "MuttonPickle.jpg"},
]
snack_products = [
    {"id": 301, "name": "chekkalu", "price": 80, "image": "murukku.jpg"},
    {"id": 302, "name": "mixture", "price": 90, "image": "chekkalu.jpg"},
    {"id": 303, "name": "Deserts", "price": 70, "image": "boondi.jpg"},
    {"id": 304, "name": "Cookies", "price": 60, "image": "sev.jpg"},
    {"id": 305, "name": "Crackers", "price": 85, "image": "jantikalu.jpg"},
]

all_products = veg_products + non_veg_products + snack_products

# --------------------------------------------------
# Helper: Get Cart from DynamoDB
# --------------------------------------------------
def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Temp user session
    return session['user_id']

def get_cart():
    try:
        response = cart_table.get_item(Key={'UserID': get_user_id()})
        return response.get('Item', {}).get('CartItems', [])
    except ClientError as e:
        print(e.response['Error']['Message'])
        return []

def update_cart(cart_items):
    try:
        cart_table.put_item(
            Item={
                'UserID': get_user_id(),
                'CartItems': cart_items
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Add login logic here if needed
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/veg-pickles")
def veg_pickles():
    return render_template("veg_pickles.html", products=veg_products)

@app.route("/non-veg-pickles")
def non_veg_pickles():
    return render_template("non_veg_pickles.html", products=non_veg_products)

@app.route("/snacks")
def snacks():
    return render_template("snacks.html", products=snack_products)

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = next((p for p in all_products if p["id"] == product_id), None)
    if product:
        cart = get_cart()
        cart.append(product)
        update_cart(cart)
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    cart = get_cart()
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/clear-cart")
def clear_cart():
    update_cart([])
    return redirect(url_for("view_cart"))

@app.route("/success")
def success():
    return render_template("success.html")

# --------------------------------------------------
if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)
