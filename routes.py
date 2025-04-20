import logging
from flask import render_template, url_for, flash, redirect, request, session, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, Product, CartItem, Order, OrderItem
from forms import RegistrationForm, LoginForm, ProductForm, AddToCartForm, CheckoutForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Home route
@app.route('/')
@app.route('/home')
def home():
    featured_products = Product.query.limit(4).all()
    return render_template('home.html', title='Welcome to Phulkari Corner', products=featured_products)

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Check if account is active
            if not user.is_active:
                flash('This account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('login.html', title='Login', form=form)
                
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Product routes
@app.route('/products')
def products():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    
    products = query.all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('products.html', title='Products', products=products, categories=categories, 
                          current_category=category, search_term=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    form.product_id.data = product.id
    return render_template('product_detail.html', title=product.name, product=product, form=form)

# Cart routes
@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    form = AddToCartForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        quantity = form.quantity.data
        
        # Check if product exists and has enough stock
        product = Product.query.get_or_404(product_id)
        if product.stock < quantity:
            flash(f'Sorry, only {product.stock} items available in stock', 'warning')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        
        if cart_item:
            # Update quantity if already in cart
            cart_item.quantity += quantity
            flash('Cart updated successfully!', 'success')
        else:
            # Add new item to cart
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
            flash('Item added to cart!', 'success')
        
        db.session.commit()
        return redirect(url_for('cart'))
    
    flash('Error adding item to cart', 'danger')
    return redirect(url_for('products'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', title='Shopping Cart', cart_items=cart_items, total=total)

@app.route('/update-cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure item belongs to current user
    if cart_item.user_id != current_user.id:
        abort(403)
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart', 'info')
    else:
        if quantity > cart_item.product.stock:
            flash(f'Only {cart_item.product.stock} items available in stock', 'warning')
            quantity = cart_item.product.stock
            
        cart_item.quantity = quantity
        flash('Cart updated', 'success')
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure item belongs to current user
    if cart_item.user_id != current_user.id:
        abort(403)
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))

# Checkout routes
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'info')
        return redirect(url_for('products'))
    
    total = sum(item.quantity * item.product.price for item in cart_items)
    
    form = CheckoutForm()
    if form.validate_on_submit():
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total if total > 999 else total + 100,  # Add shipping if total < 1000
            payment_method=form.payment_method.data,
            shipping_address=form.shipping_address.data,
            billing_address=form.billing_address.data,
            contact_phone=form.contact_phone.data
        )
        
        # Store payment details based on method
        payment_details = {}
        if form.payment_method.data == 'upi':
            payment_details['upi_id'] = form.upi_id.data
        elif form.payment_method.data in ['credit_card', 'debit_card']:
            payment_details['card_last_four'] = form.card_number.data
            payment_details['card_expiry'] = form.card_expiry.data
        elif form.payment_method.data == 'bank_transfer':
            payment_details['bank_name'] = form.bank_name.data
            payment_details['account_holder'] = form.account_holder.data
            payment_details['account_number'] = form.account_number.data
            payment_details['ifsc_code'] = form.ifsc_code.data
        
        # Convert payment details to string
        if payment_details:
            order.payment_details = str(payment_details)
            
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            product = item.product
            product.stock -= item.quantity
            
            # Remove cart item
            db.session.delete(item)
        
        try:
            db.session.commit()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error placing order: {str(e)}', 'danger')
            return redirect(url_for('checkout'))
    
    return render_template('checkout.html', title='Checkout', form=form, cart_items=cart_items, total=total)

@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure order belongs to current user
    if order.user_id != current_user.id:
        abort(403)
    
    return render_template('order_confirmation.html', title='Order Confirmation', order=order)

# User profile routes
@app.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', title='My Profile')

@app.route('/orders')
@login_required
def user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', title='My Orders', orders=orders)

# Admin routes
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Count products, orders, users
    product_count = Product.query.count()
    order_count = Order.query.count()
    user_count = User.query.count()
    
    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Low stock products
    low_stock_products = Product.query.filter(Product.stock < 10).order_by(Product.stock).limit(5).all()
    
    # Orders by status
    pending_orders = Order.query.filter_by(status='pending').count()
    processing_orders = Order.query.filter_by(status='processing').count()
    shipped_orders = Order.query.filter_by(status='shipped').count()
    delivered_orders = Order.query.filter_by(status='delivered').count()
    cancelled_orders = Order.query.filter_by(status='cancelled').count()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard', 
                          product_count=product_count, order_count=order_count, 
                          user_count=user_count, recent_orders=recent_orders,
                          total_revenue=total_revenue, low_stock_products=low_stock_products,
                          pending_orders=pending_orders, processing_orders=processing_orders,
                          shipped_orders=shipped_orders, delivered_orders=delivered_orders,
                          cancelled_orders=cancelled_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/manage_products.html', title='Manage Products', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
            category=form.category.data,
            stock=form.stock.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', title='Add Product', form=form, is_edit=False)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.image_url = form.image_url.data
        product.category = form.category.data
        product.stock = form.stock.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    # Pre-populate form fields
    if request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.image_url.data = product.image_url
        form.category.data = product.category
        form.stock.data = product.stock
    
    return render_template('admin/product_form.html', title='Edit Product', form=form, is_edit=True)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    # Get filter parameters
    status = request.args.get('status')
    date_range = request.args.get('date_range', 'all')
    search = request.args.get('search', '')
    
    # Start with all orders
    query = Order.query
    
    # Apply status filter
    if status:
        query = query.filter(Order.status == status)
    
    # Apply date filter
    today = datetime.now().date()
    if date_range == 'today':
        query = query.filter(db.func.date(Order.created_at) == today)
    elif date_range == 'yesterday':
        yesterday = today - timedelta(days=1)
        query = query.filter(db.func.date(Order.created_at) == yesterday)
    elif date_range == 'this_week':
        start_of_week = today - timedelta(days=today.weekday())
        query = query.filter(db.func.date(Order.created_at) >= start_of_week)
    elif date_range == 'this_month':
        start_of_month = today.replace(day=1)
        query = query.filter(db.func.date(Order.created_at) >= start_of_month)
    
    # Apply search filter (search by order ID or customer name/email)
    if search:
        search_term = f"%{search}%"
        query = query.join(User).filter(
            (db.cast(Order.id, db.String).like(search_term)) |
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term))
        )
    
    # Get results and sort by most recent
    orders = query.order_by(Order.created_at.desc()).all()
    
    return render_template('admin/manage_orders.html', title='Manage Orders',
                          orders=orders, status=status, date_range=date_range, search=search)

@app.route('/admin/orders/<int:order_id>')
@admin_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_details.html', title=f'Order #{order.id}', order=order)

@app.route('/admin/orders/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    from notifications import send_order_status_notification, send_tracking_update
    
    order = Order.query.get_or_404(order_id)
    customer = User.query.get(order.user_id)
    
    # Get form data
    status = request.form.get('status')
    tracking_number = request.form.get('tracking_number')
    notes = request.form.get('notes')
    carrier = request.form.get('carrier', 'Standard Shipping')
    
    # Track status change for notifications
    status_changed = False
    tracking_updated = False
    old_status = order.status
    old_tracking = order.tracking_number
    
    # Update order data
    if status and status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        if old_status != status:
            status_changed = True
            order.status = status
        
        # Update dates based on status
        if status == 'shipped' and old_status != 'shipped':
            order.shipped_date = datetime.utcnow()
        elif status == 'delivered' and old_status != 'delivered':
            order.delivered_date = datetime.utcnow()
            
    if tracking_number is not None:
        if tracking_number != old_tracking and tracking_number.strip() != '':
            tracking_updated = True
            order.tracking_number = tracking_number
            order.carrier = carrier
        
    if notes is not None:
        order.admin_notes = notes
        
    # Update timestamp
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash(f'Order #{order.id} has been updated.', 'success')
    
    # Send notifications if status changed
    if status_changed and customer:
        try:
            email_sent, sms_sent = send_order_status_notification(
                order_id=order.id,
                status=order.status,
                customer_name=customer.username,
                customer_email=customer.email,
                customer_phone=order.contact_phone
            )
            
            if email_sent:
                flash('Customer notification email sent successfully.', 'info')
            if sms_sent:
                flash('Customer notification SMS sent successfully.', 'info')
        except Exception as e:
            flash(f'Error sending status notification: {str(e)}', 'warning')
    
    # Send tracking update if tracking information was added or changed
    if tracking_updated and customer and order.tracking_number:
        try:
            email_sent, sms_sent = send_tracking_update(
                order_id=order.id,
                tracking_number=order.tracking_number,
                carrier=order.carrier or 'Standard Shipping',
                status=order.status,
                customer_name=customer.username,
                customer_email=customer.email,
                customer_phone=order.contact_phone
            )
            
            if email_sent:
                flash('Tracking information email sent to customer.', 'info')
            if sms_sent:
                flash('Tracking information SMS sent to customer.', 'info')
        except Exception as e:
            flash(f'Error sending tracking update: {str(e)}', 'warning')
    
    # Redirect back to the referring page
    if request.referrer and 'order_details' in request.referrer:
        return redirect(url_for('order_details', order_id=order.id))
    else:
        return redirect(url_for('admin_orders'))
        
@app.route('/admin/users')
@admin_required
def admin_users():
    # Get filter parameters
    role = request.args.get('role')
    status = request.args.get('status')
    search = request.args.get('search', '')
    
    # Start with all users
    query = User.query
    
    # Apply role filter
    if role:
        query = query.filter(User.role == role)
    
    # Apply status filter
    if status == 'active':
        query = query.filter(User.is_active == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            User.username.ilike(search_term) | 
            User.email.ilike(search_term)
        )
    
    # Get results and sort by ID
    users = query.order_by(User.id).all()
    
    return render_template('admin/manage_users.html', title='Manage Users',
                          users=users, role=role, status=status, search=search)

@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admins from changing their own role or status
    if user.id == current_user.id:
        flash('You cannot change your own role or status.', 'warning')
        return redirect(url_for('admin_users'))
    
    # Get form data
    role = request.form.get('role')
    is_active = 'is_active' in request.form
    
    # Update user data
    if role and role in ['user', 'admin']:
        user.role = role
    
    user.is_active = is_active
    
    db.session.commit()
    flash(f'User {user.username} has been updated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admins from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot change your own status.', 'warning')
        return redirect(url_for('admin_users'))
    
    # Toggle status
    user.is_active = not user.is_active
    
    db.session.commit()
    flash(f'User {user.username} has been {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin_users'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
    logging.error(f"Server error: {e}")
    return render_template('500.html'), 500

# Initialize admin user if not exists
def create_admin_user():
    admin_exists = User.query.filter_by(role='admin').first()
    if not admin_exists:
        admin = User(
            username='admin',
            email='admin@phulkaricorner.com',
            role='admin'
        )
        admin.set_password('adminpass')
        db.session.add(admin)
        
        test_user = User(
            username='testuser',
            email='test@phulkaricorner.com',
            role='user'
        )
        test_user.set_password('testpass')
        db.session.add(test_user)
        
        # Add some initial products with open-source images
        products = [
            {
                'name': 'Traditional Phulkari Dupatta',
                'description': 'Handcrafted Phulkari Dupatta with traditional embroidery patterns. Made with pure cotton and featuring vibrant colors that are characteristic of the Phulkari art form.',
                'price': 1499.99,
                'image_url': 'https://images.unsplash.com/photo-1602810316498-ab67cf68c8e1?q=80&w=1470&auto=format&fit=crop',
                'category': 'Dupattas',
                'stock': 20
            },
            {
                'name': 'Phulkari Embroidered Saree',
                'description': 'Elegant saree with Phulkari embroidery work. The intricate patterns and bright colors make this saree a perfect choice for special occasions.',
                'price': 2999.99,
                'image_url': 'https://images.unsplash.com/photo-1610030469668-8e4a7917273e?q=80&w=1374&auto=format&fit=crop',
                'category': 'Sarees',
                'stock': 15
            },
            {
                'name': 'Phulkari Cushion Cover (Set of 2)',
                'description': 'Brighten up your living space with these handcrafted Phulkari cushion covers. Each cover features unique embroidery patterns inspired by Punjab\'s rich cultural heritage.',
                'price': 799.99,
                'image_url': 'https://images.unsplash.com/photo-1595731589559-53b08611c8fc?q=80&w=1480&auto=format&fit=crop',
                'category': 'Home Decor',
                'stock': 30
            },
            {
                'name': 'Designer Phulkari Kurti',
                'description': 'Modern Kurti with traditional Phulkari embroidery. A perfect blend of traditional craftsmanship and contemporary design.',
                'price': 1299.99,
                'image_url': 'https://images.pexels.com/photos/11679861/pexels-photo-11679861.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
                'category': 'Clothing',
                'stock': 25
            },
            {
                'name': 'Phulkari Embroidered Jacket',
                'description': 'Stylish jacket with traditional Phulkari embroidery, perfect for festive occasions and adding an ethnic touch to your outfit.',
                'price': 3499.99,
                'image_url': 'https://images.pexels.com/photos/10484363/pexels-photo-10484363.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
                'category': 'Clothing',
                'stock': 10
            },
            {
                'name': 'Phulkari Table Runner',
                'description': 'Beautiful handcrafted table runner with vibrant Phulkari embroidery. Add a touch of traditional elegance to your dining table.',
                'price': 899.99,
                'image_url': 'https://images.pexels.com/photos/6306157/pexels-photo-6306157.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
                'category': 'Home Decor',
                'stock': 15
            }
        ]
        
        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
            
        db.session.commit()
