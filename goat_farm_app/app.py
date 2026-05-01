import os
import sqlite3
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'dev_secret_key_for_goat_farm'
DB_FILE = os.path.join(app.root_path, 'database.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS goats_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_number TEXT NOT NULL,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                notes TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS master_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                si_no TEXT, tag_no TEXT NOT NULL, breed TEXT, breed_percent TEXT,
                status TEXT, sold TEXT, expired TEXT, gender TEXT, purchase_date DATE,
                color TEXT, weight_kg REAL, purchase_amount REAL, insurance_date DATE,
                vaccination TEXT, vaccination_period TEXT, medicine TEXT, medicine_period TEXT,
                feed TEXT, feed_amount TEXT, mating_date DATE, mating_goat_no TEXT,
                goat_week_period TEXT, delivery_date DATE, new_goat_gender TEXT,
                new_goat_color TEXT, birth_weight REAL, selling_date DATE, selling_weight REAL,
                selling_price REAL, mortality_date DATE, mortality_weight REAL,
                mortality_reason TEXT, insurance_claim_amount REAL, insurance_inform_date DATE,
                insurance_claim_date DATE
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sales_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sr_no TEXT,
                tag_id TEXT NOT NULL,
                breed TEXT,
                breed_percent TEXT,
                gender TEXT,
                weight REAL,
                sold_price REAL,
                date_of_sale DATE,
                buyer_name TEXT,
                buyer_city TEXT,
                buyer_contact TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS medicine_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sr_no TEXT,
                tag_no TEXT NOT NULL,
                breed TEXT,
                breed_percent TEXT,
                med1_date DATE, med1_name TEXT,
                vac1_date DATE, vac1_name TEXT,
                med2_date DATE, med2_name TEXT,
                med3_date DATE, med3_name TEXT,
                vac2_date DATE, vac2_name TEXT,
                medicine_amount REAL,
                vaccine_amount REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mortality_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sr_no TEXT,
                tag_id TEXT NOT NULL,
                breed TEXT,
                breed_percent TEXT,
                gender TEXT,
                birth_date DATE,
                expired_date DATE,
                total_age_month TEXT,
                weight_kgs REAL,
                insurance_inform_date DATE,
                insurance_claim_date DATE,
                current_value REAL,
                claim_amount REAL,
                cause_of_death TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feed_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                si_no TEXT,
                date DATE NOT NULL,
                feed_name TEXT NOT NULL,
                opening_qty REAL,
                purchase_qty REAL,
                growing_qty REAL,
                consumption_qty REAL,
                wastage_qty REAL,
                closing_stock REAL,
                purchase_amount REAL,
                consumption_amount REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS kid_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                s_no TEXT,
                kid_id TEXT NOT NULL,
                breed TEXT,
                breed_percent TEXT,
                gender TEXT,
                color TEXT,
                litter_size INTEGER,
                birth_date DATE,
                age_month TEXT,
                birth_weight REAL,
                mother_id TEXT,
                father_id TEXT
            )
        ''')
        try:
            conn.execute("ALTER TABLE kid_records ADD COLUMN mother_id TEXT")
            conn.execute("ALTER TABLE kid_records ADD COLUMN father_id TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_name TEXT NOT NULL,
                invoice_details TEXT,
                purchase_date DATE NOT NULL,
                tag_id TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        # Check if admin user exists
        user = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not user:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         ('admin', generate_password_hash('admin123')))
        conn.commit()

# Initialize DB on startup
init_db()

@app.before_request
def require_login():
    allowed_routes = ['login', 'static', 'register', 'verify_otp', 'goats', 'goat_detail']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
            
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        print(f"\n" + "="*50)
        print(f" MOCK OTP NOTIFICATION")
        print(f" Registration OTP for '{username}' is: {otp}")
        print("="*50 + "\n")
        
        session['reg_username'] = username
        session['reg_password'] = generate_password_hash(password)
        session['reg_otp'] = otp
        
        flash('We have generated an OTP for you. Since this is a demo, please check the console for the code.', 'info')
        return redirect(url_for('verify_otp'))
        
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reg_otp' not in session:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_otp = request.form['otp'].strip()
        if user_otp == session['reg_otp']:
            # OTP matches, create user
            username = session['reg_username']
            password_hash = session['reg_password']
            
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))
            db.commit()
            
            # Clear registration session data
            session.pop('reg_username', None)
            session.pop('reg_password', None)
            session.pop('reg_otp', None)
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify_otp.html')

@app.route('/')
@app.route('/dashboard')
def dashboard():
    db = get_db()
    
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    def get_sum(table, sum_col, date_col, extra_cond=""):
        q = f"SELECT SUM({sum_col}) FROM {table} WHERE 1=1 {extra_cond}"
        p = []
        if start_date:
            q += f" AND {date_col} >= ?"
            p.append(start_date)
        if end_date:
            q += f" AND {date_col} <= ?"
            p.append(end_date)
        return db.execute(q, p).fetchone()[0] or 0.0
    
    base_inc = get_sum("goats_data", "amount", "date", "AND category='income'")
    sales_inc = get_sum("sales_records", "sold_price", "date_of_sale")
    claim_inc = get_sum("mortality_records", "claim_amount", "insurance_claim_date")
    master_inc = get_sum("master_records", "selling_price", "selling_date")
    income = base_inc + sales_inc + claim_inc + master_inc
    
    base_exp = get_sum("goats_data", "amount", "date", "AND category='expense'")
    med_exp = get_sum("medicine_records", "IFNULL(medicine_amount, 0) + IFNULL(vaccine_amount, 0)", "COALESCE(med1_date, vac1_date)")
    feed_exp = get_sum("feed_records", "purchase_amount", "date")
    master_exp = get_sum("master_records", "purchase_amount", "purchase_date")
    purchase_exp = get_sum("purchases", "price", "purchase_date")
    expense = base_exp + med_exp + feed_exp + master_exp + purchase_exp
    
    profit = income - expense
    return render_template('dashboard.html', income=income, expense=expense, profit=profit, start_date=start_date, end_date=end_date)

@app.route('/records')
def records():
    db = get_db()
    tag_search = request.args.get('tag_number', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = "SELECT * FROM goats_data WHERE 1=1"
    params = []
    
    if tag_search:
        query += " AND tag_number LIKE ?"
        params.append(f"%{tag_search}%")
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
        
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    query += " ORDER BY date DESC"
    
    records = db.execute(query, params).fetchall()
    return render_template('records.html', records=records)

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        tag_number = request.form['tag_number'].strip()
        date = request.form['date']
        category = request.form['category']
        type_val = request.form['type'].strip()
        amount = request.form['amount']
        notes = request.form.get('notes', '').strip()
        
        if not tag_number or not date or not category or not type_val or not amount:
            flash('All fields except notes are required.', 'danger')
            return render_template('add_record.html')
            
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number.', 'danger')
            return render_template('add_record.html')
            
        db = get_db()
        db.execute('INSERT INTO goats_data (tag_number, date, category, type, amount, notes) VALUES (?, ?, ?, ?, ?, ?)',
                   (tag_number, date, category, type_val, amount, notes))
        db.commit()
        flash('Record added successfully.', 'success')
        return redirect(url_for('records'))
        
    return render_template('add_record.html')

@app.route('/edit_record/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    db = get_db()
    record = db.execute('SELECT * FROM goats_data WHERE id = ?', (id,)).fetchone()
    
    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('records'))
        
    if request.method == 'POST':
        tag_number = request.form['tag_number'].strip()
        date = request.form['date']
        category = request.form['category']
        type_val = request.form['type'].strip()
        amount = request.form['amount']
        notes = request.form.get('notes', '').strip()
        
        if not tag_number or not date or not category or not type_val or not amount:
            flash('All fields except notes are required.', 'danger')
            return render_template('edit_record.html', record=record)
            
        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number.', 'danger')
            return render_template('edit_record.html', record=record)
            
        db.execute('''UPDATE goats_data 
                      SET tag_number = ?, date = ?, category = ?, type = ?, amount = ?, notes = ? 
                      WHERE id = ?''',
                   (tag_number, date, category, type_val, amount, notes, id))
        db.commit()
        flash('Record updated successfully.', 'success')
        return redirect(url_for('records'))
        
    return render_template('edit_record.html', record=record)

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    db = get_db()
    db.execute('DELETE FROM goats_data WHERE id = ?', (id,))
    db.commit()
    flash('Record deleted successfully.', 'success')
    return redirect(url_for('records'))

@app.route('/goats')
def goats():
    db = get_db()
    
    # Get all unique tag numbers and their summary
    goats_summary = db.execute('''
        SELECT tag_number, 
               MIN(date) as first_record,
               MAX(date) as last_record,
               COUNT(*) as total_records,
               SUM(CASE WHEN category = 'income' THEN amount ELSE 0 END) as total_income,
               SUM(CASE WHEN category = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM goats_data
        GROUP BY tag_number
        ORDER BY tag_number ASC
    ''').fetchall()
    
    return render_template('goats.html', goats=goats_summary)

@app.route('/goat/<tag_number>')
def goat_detail(tag_number):
    db = get_db()
    
    history_query = '''
    SELECT date, category, type, amount, notes FROM goats_data WHERE tag_number = ?
    UNION ALL
    SELECT date_of_sale as date, 'income' as category, 'Sales' as type, sold_price as amount, '' as notes FROM sales_records WHERE tag_id = ? AND date_of_sale IS NOT NULL
    UNION ALL
    SELECT COALESCE(med1_date, vac1_date) as date, 'expense' as category, 'Medicine/Vaccine' as type, IFNULL(medicine_amount, 0) + IFNULL(vaccine_amount, 0) as amount, '' as notes FROM medicine_records WHERE tag_no = ? AND (med1_date IS NOT NULL OR vac1_date IS NOT NULL)
    UNION ALL
    SELECT expired_date as date, 'expense' as category, 'Mortality Loss' as type, IFNULL(current_value, 0) as amount, cause_of_death as notes FROM mortality_records WHERE tag_id = ? AND expired_date IS NOT NULL
    UNION ALL
    SELECT insurance_claim_date as date, 'income' as category, 'Insurance Claim' as type, IFNULL(claim_amount, 0) as amount, '' as notes FROM mortality_records WHERE tag_id = ? AND insurance_claim_date IS NOT NULL
    UNION ALL
    SELECT purchase_date as date, 'expense' as category, 'Purchase' as type, IFNULL(purchase_amount, 0) as amount, '' as notes FROM master_records WHERE tag_no = ? AND purchase_date IS NOT NULL
    ORDER BY date DESC
    '''
    history = db.execute(history_query, (tag_number, tag_number, tag_number, tag_number, tag_number, tag_number)).fetchall()
    
    income = sum(r['amount'] for r in history if r['category'] == 'income')
    expense = sum(r['amount'] for r in history if r['category'] == 'expense')
    profit = income - expense
    
    return render_template('goat_detail.html', tag_number=tag_number, income=income, expense=expense, profit=profit, history=history)

@app.route('/master_add', methods=['GET', 'POST'])
def master_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO master_records (
                si_no, tag_no, breed, breed_percent, status, sold, expired, gender, purchase_date, color,
                weight_kg, purchase_amount, insurance_date, vaccination, vaccination_period, medicine,
                medicine_period, feed, feed_amount, mating_date, mating_goat_no, goat_week_period,
                delivery_date, new_goat_gender, new_goat_color, birth_weight, selling_date,
                selling_weight, selling_price, mortality_date, mortality_weight, mortality_reason,
                insurance_claim_amount, insurance_inform_date, insurance_claim_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('si_no'), f.get('tag_no'), f.get('breed'), f.get('breed_percent'), f.get('status'),
            f.get('sold'), f.get('expired'), f.get('gender'), f.get('purchase_date'), f.get('color'),
            f.get('weight_kg'), f.get('purchase_amount'), f.get('insurance_date'), f.get('vaccination'),
            f.get('vaccination_period'), f.get('medicine'), f.get('medicine_period'), f.get('feed'),
            f.get('feed_amount'), f.get('mating_date'), f.get('mating_goat_no'), f.get('goat_week_period'),
            f.get('delivery_date'), f.get('new_goat_gender'), f.get('new_goat_color'), f.get('birth_weight'),
            f.get('selling_date'), f.get('selling_weight'), f.get('selling_price'), f.get('mortality_date'),
            f.get('mortality_weight'), f.get('mortality_reason'), f.get('insurance_claim_amount'),
            f.get('insurance_inform_date'), f.get('insurance_claim_date')
        ))
        db.commit()
        flash('Master record added successfully!', 'success')
        return redirect(url_for('master'))
    return render_template('master_add.html')

@app.route('/master')
def master():
    db = get_db()
    tag_search = request.args.get('tag_no', '')
    if tag_search:
        records = db.execute('SELECT * FROM master_records WHERE tag_no LIKE ? OR si_no LIKE ? ORDER BY id DESC', 
             (f"%{tag_search}%", f"%{tag_search}%")).fetchall()
    else:
        records = db.execute('SELECT * FROM master_records ORDER BY id DESC').fetchall()
    return render_template('master.html', records=records)

@app.route('/sales_add', methods=['GET', 'POST'])
def sales_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO sales_records (
                sr_no, tag_id, breed, breed_percent, gender, weight, sold_price, 
                date_of_sale, buyer_name, buyer_city, buyer_contact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('sr_no'), f.get('tag_id'), f.get('breed'), f.get('breed_percent'), f.get('gender'),
            f.get('weight'), f.get('sold_price'), f.get('date_of_sale'), f.get('buyer_name'),
            f.get('buyer_city'), f.get('buyer_contact')
        ))
        db.commit()
        flash('Sales record added successfully!', 'success')
        return redirect(url_for('sales'))
    return render_template('sales_add.html')

@app.route('/sales')
def sales():
    db = get_db()
    tag_search = request.args.get('tag_id', '')
    if tag_search:
        records = db.execute('SELECT * FROM sales_records WHERE tag_id LIKE ? OR buyer_name LIKE ? ORDER BY date_of_sale DESC', 
             (f"%{tag_search}%", f"%{tag_search}%")).fetchall()
    else:
        records = db.execute('SELECT * FROM sales_records ORDER BY date_of_sale DESC').fetchall()
    return render_template('sales.html', records=records)

@app.route('/medicine_add', methods=['GET', 'POST'])
def medicine_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO medicine_records (
                sr_no, tag_no, breed, breed_percent,
                med1_date, med1_name, vac1_date, vac1_name,
                med2_date, med2_name, med3_date, med3_name,
                vac2_date, vac2_name, medicine_amount, vaccine_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('sr_no'), f.get('tag_no'), f.get('breed'), f.get('breed_percent'),
            f.get('med1_date'), f.get('med1_name'), f.get('vac1_date'), f.get('vac1_name'),
            f.get('med2_date'), f.get('med2_name'), f.get('med3_date'), f.get('med3_name'),
            f.get('vac2_date'), f.get('vac2_name'), f.get('medicine_amount') or None, f.get('vaccine_amount') or None
        ))
        db.commit()
        flash('Medicine record added successfully!', 'success')
        return redirect(url_for('medicine'))
    return render_template('medicine_add.html')

@app.route('/medicine')
def medicine():
    db = get_db()
    tag_search = request.args.get('tag_no', '')
    if tag_search:
        records = db.execute('SELECT * FROM medicine_records WHERE tag_no LIKE ? ORDER BY id DESC', 
             (f"%{tag_search}%",)).fetchall()
    else:
        records = db.execute('SELECT * FROM medicine_records ORDER BY id DESC').fetchall()
    return render_template('medicine.html', records=records)

@app.route('/mortality_add', methods=['GET', 'POST'])
def mortality_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO mortality_records (
                sr_no, tag_id, breed, breed_percent, gender, birth_date, expired_date, 
                total_age_month, weight_kgs, insurance_inform_date, insurance_claim_date,
                current_value, claim_amount, cause_of_death
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('sr_no'), f.get('tag_id'), f.get('breed'), f.get('breed_percent'), f.get('gender'),
            f.get('birth_date'), f.get('expired_date'), f.get('total_age_month'), f.get('weight_kgs'), 
            f.get('insurance_inform_date'), f.get('insurance_claim_date'), f.get('current_value'), 
            f.get('claim_amount'), f.get('cause_of_death')
        ))
        db.commit()
        flash('Mortality record added successfully!', 'success')
        return redirect(url_for('mortality'))
    return render_template('mortality_add.html')

@app.route('/mortality')
def mortality():
    db = get_db()
    tag_search = request.args.get('tag_id', '')
    if tag_search:
        records = db.execute('SELECT * FROM mortality_records WHERE tag_id LIKE ? ORDER BY expired_date DESC', 
             (f"%{tag_search}%",)).fetchall()
    else:
        records = db.execute('SELECT * FROM mortality_records ORDER BY expired_date DESC').fetchall()
    return render_template('mortality.html', records=records)

@app.route('/feed_add', methods=['GET', 'POST'])
def feed_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO feed_records (
                si_no, date, feed_name, opening_qty, purchase_qty, growing_qty, 
                consumption_qty, wastage_qty, closing_stock, purchase_amount, consumption_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('si_no'), f.get('date'), f.get('feed_name'), f.get('opening_qty') or 0, 
            f.get('purchase_qty') or 0, f.get('growing_qty') or 0, f.get('consumption_qty') or 0, 
            f.get('wastage_qty') or 0, f.get('closing_stock') or 0, f.get('purchase_amount') or 0, 
            f.get('consumption_amount') or 0
        ))
        db.commit()
        flash('Feed inventory record added successfully!', 'success')
        return redirect(url_for('feed'))
    return render_template('feed_add.html')

@app.route('/feed')
def feed():
    db = get_db()
    feed_search = request.args.get('feed_name', '')
    if feed_search:
        records = db.execute('SELECT * FROM feed_records WHERE feed_name LIKE ? ORDER BY date DESC', 
             (f"%{feed_search}%",)).fetchall()
    else:
        records = db.execute('SELECT * FROM feed_records ORDER BY date DESC').fetchall()
    return render_template('feed.html', records=records)

@app.route('/kid_add', methods=['GET', 'POST'])
def kid_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO kid_records (
                s_no, kid_id, breed, breed_percent, gender, color, 
                litter_size, birth_date, age_month, birth_weight, mother_id, father_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.get('s_no'), f.get('kid_id'), f.get('breed'), f.get('breed_percent'), f.get('gender'),
            f.get('color'), f.get('litter_size'), f.get('birth_date'), f.get('age_month'), f.get('birth_weight'),
            f.get('mother_id'), f.get('father_id')
        ))
        db.commit()
        flash('Kid record added successfully!', 'success')
        return redirect(url_for('kid'))
    return render_template('kid_add.html')

@app.route('/kid')
def kid():
    db = get_db()
    kid_search = request.args.get('kid_id', '')
    if kid_search:
        records = db.execute('SELECT * FROM kid_records WHERE kid_id LIKE ? ORDER BY birth_date DESC', 
             (f"%{kid_search}%",)).fetchall()
    else:
        records = db.execute('SELECT * FROM kid_records ORDER BY birth_date DESC').fetchall()
    return render_template('kid.html', records=records)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('dashboard'))
        
    db = get_db()
    
    # Check if exact tag match in master
    tag_master = db.execute("SELECT * FROM master_records WHERE tag_no = ?", (query,)).fetchone()
    # Or in goats_data
    tag_goats = db.execute("SELECT * FROM goats_data WHERE tag_number = ?", (query,)).fetchone()
    
    if tag_master or tag_goats:
        return redirect(url_for('goat_detail', tag_number=query))
        
    flash(f"No records found for '{query}'", 'info')
    return redirect(url_for('dashboard'))
@app.route('/purchase_add', methods=['GET', 'POST'])
def purchase_add():
    if request.method == 'POST':
        f = request.form
        db = get_db()
        db.execute('''
            INSERT INTO purchases (
                seller_name, invoice_details, purchase_date, tag_id, price
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            f.get('seller_name'), f.get('invoice_details'), f.get('purchase_date'), 
            f.get('tag_id'), f.get('price')
        ))
        db.commit()
        flash('Purchase record added successfully!', 'success')
        return redirect(url_for('purchases'))
    return render_template('purchase_add.html')

@app.route('/purchases')
def purchases():
    db = get_db()
    tag_search = request.args.get('tag_id', '')
    if tag_search:
        records = db.execute('SELECT * FROM purchases WHERE tag_id LIKE ? ORDER BY purchase_date DESC', 
             (f"%{tag_search}%",)).fetchall()
    else:
        records = db.execute('SELECT * FROM purchases ORDER BY purchase_date DESC').fetchall()
    return render_template('purchases.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
