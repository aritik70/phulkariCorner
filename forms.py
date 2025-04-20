from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField, HiddenField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional, Regexp
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Product')

class AddToCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('Add to Cart')

class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired()])
    billing_address = TextAreaField('Billing Address', validators=[DataRequired()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired(), Length(min=10, max=20)])
    payment_method = SelectField('Payment Method', validators=[DataRequired()], 
                                 choices=[('credit_card', 'Credit Card'), 
                                          ('debit_card', 'Debit Card'), 
                                          ('bank_transfer', 'Bank Transfer'),
                                          ('upi', 'UPI'), 
                                          ('cod', 'Cash on Delivery')])
    
    # Bank transfer details
    bank_name = StringField('Bank Name', validators=[Optional(), Length(max=100)])
    account_holder = StringField('Account Holder Name', validators=[Optional(), Length(max=100)])
    account_number = StringField('Account Number', validators=[Optional(), Length(min=8, max=20)])
    ifsc_code = StringField('IFSC Code', validators=[Optional(), Length(min=11, max=11), 
                                               Regexp('^[A-Z]{4}0[A-Z0-9]{6}$', 
                                                      message='Invalid IFSC code format')])
    
    # Card details
    card_number = StringField('Card Number (Last 4 digits)', validators=[Optional(), Length(min=4, max=4),
                                                       Regexp('^\d{4}$', message='Please enter only last 4 digits')])
    card_expiry = StringField('Expiry Date (MM/YY)', validators=[Optional(),
                                                  Regexp('^\d{2}/\d{2}$', message='Format must be MM/YY')])
    
    # UPI details
    upi_id = StringField('UPI ID', validators=[Optional(), 
                                     Regexp('^[\w\.\-]+@[\w\-]+$', message='Invalid UPI ID format')])
    
    submit = SubmitField('Place Order')
    
    def validate(self, *args, **kwargs):
        result = super().validate(*args, **kwargs)
            
        # Validate based on payment method only if not COD
        if self.payment_method.data == 'bank_transfer':
            if not self.bank_name.data or not self.account_holder.data or not self.account_number.data or not self.ifsc_code.data:
                self.bank_name.errors = ['Bank details are required for bank transfer']
                return False
        elif self.payment_method.data in ['credit_card', 'debit_card']:
            if not self.card_number.data or not self.card_expiry.data:
                self.card_number.errors = ['Card details are required for card payment']
                return False
        elif self.payment_method.data == 'upi':
            if not self.upi_id.data:
                self.upi_id.errors = ['UPI ID is required for UPI payment']
                return False
                
        return result
        
class OrderStatusForm(FlaskForm):
    status = SelectField('Order Status', validators=[DataRequired()],
                        choices=[('pending', 'Pending'), 
                                ('processing', 'Processing'),
                                ('shipped', 'Shipped'),
                                ('delivered', 'Delivered'),
                                ('cancelled', 'Cancelled')])
    tracking_number = StringField('Tracking Number', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Admin Notes', validators=[Optional()])
    submit = SubmitField('Update Status')
    
class UserManagementForm(FlaskForm):
    role = SelectField('User Role', validators=[DataRequired()],
                      choices=[('user', 'Customer'), ('admin', 'Administrator')])
    is_active = BooleanField('Active Account')
    submit = SubmitField('Update User')
    
class AnalyticsFilterForm(FlaskForm):
    date_range = SelectField('Time Period', validators=[DataRequired()],
                           choices=[('daily', 'Daily'), 
                                   ('weekly', 'Weekly'),
                                   ('monthly', 'Monthly'),
                                   ('custom', 'Custom Range')])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Apply Filter')
    
class ThemeSettingsForm(FlaskForm):
    primary_color = StringField('Primary Color', validators=[DataRequired(), 
                                                           Regexp('^#[0-9A-Fa-f]{6}$', 
                                                                 message='Please enter a valid hex color code')])
    secondary_color = StringField('Secondary Color', validators=[DataRequired(), 
                                                              Regexp('^#[0-9A-Fa-f]{6}$', 
                                                                    message='Please enter a valid hex color code')])
    accent_color = StringField('Accent Color', validators=[DataRequired(), 
                                                         Regexp('^#[0-9A-Fa-f]{6}$', 
                                                               message='Please enter a valid hex color code')])
    theme_name = StringField('Theme Name', validators=[DataRequired(), Length(max=50)])
    is_active = BooleanField('Set as Active Theme')
    submit = SubmitField('Save Theme')
