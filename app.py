from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
load_dotenv()

from flask import redirect, url_for, flash, abort, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import abort
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import yfinance as yf
from automation_script import preprocess_text, correct_typos
from actions.ticker_mapping import get_ticker
from sqlalchemy.dialects.postgresql import ARRAY
# URL of Rasa's server
RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'
ACTION_SERVER_URL = 'http://localhost:5055/webhook'

app = Flask(__name__, static_url_path='/static')

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@localhost/{os.getenv('DB_NAME')}"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)
# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_SUPPRESS_SEND'] = False
mail.init_app(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = hashed_password.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class ReportedConversations(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String())
    bot_response = db.Column(db.String())

class Queries(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    message = db.Column(db.String())

class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker_symbols = db.Column(ARRAY(db.String(10)), nullable=False)
    email_service_status = db.Column(db.Boolean, default=True)

    def add_ticker_symbol(self, ticker_symbol):
        if len(self.ticker_symbols) < 10:
            # Check if the ticker symbol is already in the list
            if ticker_symbol not in self.ticker_symbols:
                self.ticker_symbols.append(ticker_symbol)
                return True
            else:
                return False, "Ticker symbol already exists in the watchlist"
        else:
            return False, "Maximum limit of 10 ticker symbols reached"

    def remove_ticker_symbol(self, ticker_symbol):
        if ticker_symbol in self.ticker_symbols:
            self.ticker_symbols.remove(ticker_symbol)
            return True
        else:
            return False
  
# Initialize Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Sign up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Print the length of the email string for debugging
        # print("Length of email string:", len(email))
        
        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('You have successfully signed up! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear flash messages from the session
    for message in get_flashed_messages():
        pass
    error = None  # Initialize error variable
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))  # Redirect to the main route upon successful login
            else:
                error = 'Invalid password'  # Set error message if password is incorrect
                abort(401)  # Return 401 status code for unauthorized access
        else:
            error = 'User not found'  # Set error message if user does not exist
            abort(401)  # Return 401 status code for unauthorized access
    return render_template('login.html', error=error)  # Pass error message to template

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Protected route
@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route'

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Reset password route
@app.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a token for password reset
            token = serializer.dumps(email, salt='reset-password')

            # Send the reset password link via email
            reset_link = url_for('new_password', token=token, _external=True)
            message = Message('Reset Your Password', recipients=[email])
            message.body = f'Click the link below to reset your password:\n{reset_link}'
            mail.send(message)

            flash('Password reset instructions sent to your email. Please check your inbox.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found. Please enter a registered email address.', 'error')
    return render_template('resetpassword.html')

# New Password route
@app.route('/newpassword/<token>', methods=['GET', 'POST'])
def new_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)  # Token expires in 1 hour
    except:
        flash('The reset link is invalid or expired. Please try again.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            password = request.form.get('password')
            confirm_password = request.form.get('confirmPassword')
            if password == confirm_password:
                user.set_password(password)
                try:
                    db.session.commit()
                    print("Password updated successfully.")
                    flash('Password updated successfully. You can now login with your new password.', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    print("Error updating password in the database:", e)
                    flash('An error occurred while updating your password. Please try again later.', 'error')
            else:
                flash('Passwords do not match. Please try again.', 'error')
        else:
            print("User not found for email:", email)
            flash('User not found. Please try again.', 'error')

    return render_template('newpassword.html', token=token)

# Report conversation route
@app.route('/report-conversation', methods=['POST'])
def report_conversation():
    # Get user message and bot response from the request data
    data = request.json
    user_message = data.get('user_message')
    bot_response = data.get('bot_response')

    # Check if both user message and bot response are present
    if user_message and bot_response:
        try:
            # Create a new instance of ReportedConversations model
            reported_conversation = ReportedConversations(user_message=user_message, bot_response=bot_response)
            
            # Add and commit the new conversation to the database
            db.session.add(reported_conversation)
            db.session.commit()

            # Return a success response
            return jsonify({'message': 'Conversation reported successfully'}), 200
        except Exception as e:
            # Log the exception
            print("Exception occurred:", e)
            # If an error occurs, rollback the transaction
            db.session.rollback()
            return jsonify({'message': 'Failed to report conversation. Please try again later.'}), 500
    else:
        # If user message or bot response is missing, return a bad request response
        return jsonify({'message': 'Both user message and bot response are required.'}), 400

# faq route
@app.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

# about route
@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# contact us route
@app.route('/contactus', methods=['GET', 'POST'])
@login_required
def contactus():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        new_query = Queries(name=name, email=email, message=message)

        try:
            db.session.add(new_query)
            db.session.commit()
        except Exception as e:
            print("Exception occurred while saving the query:", e)
            db.session.rollback()
            return redirect(url_for('contactus'))

    return render_template('contactus.html')

# Function to handle unexpected errors using Stack Exchange API
def handle_unexpected_error(user_message):
    try:
        bot_response = "An unexpected error occurred. Please try again later."

    except Exception as e:
        print("An unexpected error occurred:", e)
        bot_response = "An unexpected error occurred while processing your request."

    return bot_response

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        user_message = request.json.get('message', '')
        print("User message:", user_message)

        # preprocessed_message = preprocess_text(user_message) 
        # print("Preprocessed user message:", preprocessed_message)
        # corrected_message = correct_typos(user_message)
        # print("Corrected user message:", corrected_message)

        # Send the user's message to RASA and get the bot's response
        rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
        rasa_response.raise_for_status()  # Raise an exception for HTTP errors
        rasa_response_json = rasa_response.json()

        print("Rasa Response:", rasa_response_json)
        if 'image' in rasa_response_json[0]:
            print("Image Found")
            bot_response = rasa_response_json[0]['image'] if rasa_response_json else 'Sorry, I didn\'t understand that.'
        elif rasa_response_json[0]['text'] == "This conversation will reset in 3 seconds.":
            print("Reset Command Found")
            bot_response = rasa_response_json[0]['text']
        else:
            print("Text Found")
            bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I didn\'t understand that.'

    except requests.exceptions.RequestException as e:
        print("An error occurred while sending the request to Rasa:", e)
        bot_response = 'Sorry, I am currently unable to process your request. Please try again later.'

    except Exception as e:
        print("An error occurred:", e)
        bot_response = handle_unexpected_error(user_message)

    print(bot_response)
    return jsonify({'response': bot_response})

@app.route('/loc', methods=['GET'])
def loc():
    try:
        with open("loc.txt", "r") as f:
            loc = f.read()
            return jsonify({'loc': loc})
    except Exception as e:
        print("An error occurred while fetching LOC:", e)
        return jsonify({'loc': 'Error fetching LOC'}), 500  # Return a 500 status code for internal server error

# Route to fetch stock data
@app.route('/stock_data', methods=['GET'])
def get_stock_data():
    all_stock_data = []
    with open('stock_data.txt', 'r') as f:
        for line in f:
            symbol, price, change, percent_change, market_cap = line.strip().split(',')
            stock_data = {
                'symbol': symbol,
                'price': price,
                'change': change,
                'percent_change': percent_change,
                'market_cap': market_cap
            }
            all_stock_data.append(stock_data)
    return jsonify(all_stock_data)

# Route for location access
@app.route('/store-location', methods=['POST'])
def store_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Retrieve the current user from the Flask-Login session
    user = current_user 

    # Create a new UserLocation instance and associate it with the current user
    new_location = UserLocation(latitude=latitude, longitude=longitude, user_id=user.id)

    try:
        db.session.add(new_location)
        db.session.commit()
        return jsonify({'message': 'Location stored successfully'}), 200
    except Exception as e:
        print("Error storing location:", e)
        return jsonify({'message': 'Failed to store location'}), 500

# stock news route
@app.route('/stock_news', methods=['POST'])
def get_stock_news():
    company_name = request.form.get('company_name')
    print(company_name)
    ticker_symbol = get_ticker(company_name)
    news_data = yf.Ticker(ticker_symbol).news
    formatted_news = []
    for news_item in news_data:
        formatted_news.append({
            'title': news_item['title'],
            'publisher': news_item['publisher'],
            'link': news_item['link'],
            'published_date': news_item['providerPublishTime'],
            'thumbnail_url': news_item['thumbnail']['resolutions'][0]['url'] if 'thumbnail' in news_item else None
        })
    return jsonify(formatted_news)

@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    company_name = request.form.get('company_name')
    ticker_symbol = get_ticker(company_name)
    
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if not watchlist:
        watchlist = Watchlist(user_id=current_user.id, ticker_symbols=[ticker_symbol], email_service_status=True)
        db.session.add(watchlist)
    else:
        if not watchlist.add_ticker_symbol(ticker_symbol):
            return jsonify({'message': 'Maximum limit of 10 ticker symbols reached'}), 400
    
    db.session.commit() 
    return jsonify({'message': 'Stock added to watchlist'}), 200
  

# Add a route to handle removing a stock from the watchlist
@app.route('/remove_from_watchlist', methods=['POST'])
@login_required
def remove_from_watchlist():
    ticker_symbol = request.form.get('ticker_symbol')
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if watchlist:
        if watchlist.remove_ticker_symbol(ticker_symbol):
            db.session.commit()  # Commit changes to the database
            return jsonify({'message': 'Stock removed from watchlist'}), 200
        else:
            return jsonify({'message': 'Stock not found in watchlist'}), 400
    else:
        return jsonify({'message': 'Watchlist not found'}), 404  
  
@app.route('/get_watchlist', methods=['GET'])
@login_required
def get_watchlist():
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if watchlist:
        return jsonify({'watchlist': watchlist.ticker_symbols}), 200
    else:
        return jsonify({'watchlist': []}), 200

@app.route('/toggle_email_service', methods=['POST'])
@login_required
def toggle_email_service():
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if watchlist:
        # Toggle the email service status
        watchlist.email_service_status = not watchlist.email_service_status
        db.session.commit()  # Commit changes to the database
        return jsonify({'message': 'Email service toggled successfully'}), 200
    else:
        return jsonify({'message': 'Watchlist not found'}), 404

if __name__ == "__main__":
    app.run(debug=True, port=3000)


