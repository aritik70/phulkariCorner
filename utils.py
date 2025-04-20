from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash
from models import User, Product

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_total(cart_items, products_dict):
    total = 0
    for item in cart_items:
        product = products_dict.get(item.product_id)
        if product:
            total += product.price * item.quantity
    return total

def init_sample_data(users, products, next_product_id):
    # Create admin user
    admin = User(
        id="1",
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("admin123"),
        is_admin=True
    )
    users[admin.id] = admin
    
    # Create test user
    test_user = User(
        id="2",
        username="testuser",
        email="test@example.com",
        password_hash=generate_password_hash("test123"),
        is_admin=False
    )
    users[test_user.id] = test_user
    
    # Create sample products
    sample_products = [
        {
            "name": "Phulkari Dupatta - Red",
            "price": 2500,
            "description": "Traditional Punjabi embroidery Phulkari dupatta in vibrant red color with intricate gold threadwork. Perfect for special occasions and festivals.",
            "category": "Dupattas",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-009_A_1800x1800.jpg",
            "stock": 15,
            "featured": True
        },
        {
            "name": "Phulkari Kurta - Blue",
            "price": 3500,
            "description": "Hand-embroidered blue Phulkari kurta with traditional motifs. Made from high-quality cotton fabric for comfort and durability.",
            "category": "Clothing",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-3491_1800x1800.jpg",
            "stock": 10,
            "featured": True
        },
        {
            "name": "Phulkari Cushion Cover Set",
            "price": 1200,
            "description": "Set of 2 vibrant Phulkari cushion covers with traditional embroidery. Add a touch of Punjabi culture to your home decor.",
            "category": "Home Decor",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/el-cushion-01_1800x1800.jpg",
            "stock": 20,
            "featured": False
        },
        {
            "name": "Phulkari Wall Hanging",
            "price": 1800,
            "description": "Beautifully crafted Phulkari wall hanging to elevate your home decor. Features traditional Punjabi motifs in vibrant colors.",
            "category": "Home Decor",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-MUL-1_1800x1800.jpg",
            "stock": 8,
            "featured": False
        },
        {
            "name": "Phulkari Stole - Green",
            "price": 1500,
            "description": "Elegant green Phulkari stole with intricate embroidery. Light and comfortable for everyday wear.",
            "category": "Accessories",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-MUL-2_1800x1800.jpg",
            "stock": 12,
            "featured": True
        },
        {
            "name": "Phulkari Saree - Maroon",
            "price": 5500,
            "description": "Luxurious maroon Phulkari saree with elaborate embroidery. Perfect for weddings and special occasions.",
            "category": "Clothing",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-008_A_1800x1800.jpg",
            "stock": 5,
            "featured": True
        },
        {
            "name": "Phulkari Table Runner",
            "price": 900,
            "description": "Beautiful Phulkari table runner to add a splash of color to your dining table. Features traditional embroidery.",
            "category": "Home Decor",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-097_A_1800x1800.jpg",
            "stock": 15,
            "featured": False
        },
        {
            "name": "Phulkari Potli Bag",
            "price": 800,
            "description": "Handcrafted Phulkari potli bag with drawstring closure. Perfect accessory for ethnic outfits.",
            "category": "Accessories",
            "image_url": "https://cdn.shopify.com/s/files/1/0030/9759/1872/products/ELD-07-097_C_1800x1800.jpg",
            "stock": 18,
            "featured": False
        }
    ]
    
    id_counter = 1
    for product_data in sample_products:
        product = Product(
            id=str(id_counter),
            name=product_data["name"],
            price=product_data["price"],
            description=product_data["description"],
            category=product_data["category"],
            image_url=product_data["image_url"],
            stock=product_data["stock"],
            featured=product_data["featured"]
        )
        products[product.id] = product
        id_counter += 1
