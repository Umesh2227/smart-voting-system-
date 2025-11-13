from flask import Flask, render_template, url_for, request, session, flash, redirect
import requests
import pymysql
import pandas as pd
import datetime
import time
import pyotp
import random
import string

mydb=pymysql.connect(host='localhost', user='root', password='root', port=3306, database='smart_voting_system')

# Email sending removed in this simplified edition. Verification is automatic.

app=Flask(__name__)
app.config['SECRET_KEY']='ajsihh98rw3fyes8o3e9ey3w5dc'

@app.before_request
def initialize():
    if 'IsAdmin' not in session:
        session['IsAdmin']=False
    if 'User' not in session:
        session['User']=None

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['POST','GET'])
def admin():
    # Login attempt
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        if (email=='admin@voting.com') and (password=='admin'):
            session['IsAdmin']=True
            session['User']='admin'
            flash('Admin login successful','success')

    # If admin is logged in, compute progress and results and show dashboard data
    if session.get('IsAdmin'):
        try:
            # total registered voters
            voters_df = pd.read_sql_query('SELECT * FROM voters', mydb)
            total_registered = len(voters_df)
            # verified voters
            total_verified = len(voters_df[voters_df['verified'] == 'yes']) if 'verified' in voters_df.columns else 0
            # votes cast
            votes_df = pd.read_sql_query('SELECT * FROM vote', mydb)
            total_votes = len(votes_df)
            # per-nominee counts (as list of {symbol,count})
            if not votes_df.empty:
                vc = votes_df['vote'].value_counts().to_dict()
                per_nominee_counts = [{'symbol': k, 'count': v} for k, v in vc.items()]
            else:
                per_nominee_counts = []
            # nominees
            df_nom = pd.read_sql_query('SELECT * FROM nominee', mydb)
            all_nom = df_nom['symbol_name'].values.tolist() if not df_nom.empty else []
            stats = {
                'total_registered': total_registered,
                'total_verified': total_verified,
                'total_votes': total_votes,
                'per_nominee_counts': per_nominee_counts
            }
        except Exception as e:
            # On any DB error, show minimal info
            stats = {'error': str(e)}
            all_nom = []
        return render_template('admin.html', admin=True, stats=stats, noms=all_nom)

    return render_template('admin.html', admin=session.get('IsAdmin', False))


@app.route('/admin_logout')
def admin_logout():
    session['IsAdmin'] = False
    session['User'] = None
    flash('Admin logged out', 'info')
    return redirect(url_for('home'))

@app.route('/add_nominee', methods=['POST','GET'])
def add_nominee():
    # Only admin can add nominees
    if not session.get('IsAdmin'):
        flash('Administrator login required to add nominees.', 'warning')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        member = request.form.get('member_name', '').strip()
        party = request.form.get('party_name', '').strip()
        logo = request.form.get('test', '').strip()
        if not member or not party or not logo:
            flash('All fields are required.', 'warning')
            return redirect(url_for('add_nominee'))

        # Check for duplicates
        nominee = pd.read_sql_query('SELECT * FROM nominee', mydb)
        all_members = nominee.member_name.values if 'member_name' in nominee.columns else []
        all_parties = nominee.party_name.values if 'party_name' in nominee.columns else []
        all_symbols = nominee.symbol_name.values if 'symbol_name' in nominee.columns else []
        if member in all_members:
            flash('The member already exists', 'info')
        elif party in all_parties:
            flash('The party already exists', 'info')
        elif logo in all_symbols:
            flash('The logo is already taken', 'info')
        else:
            try:
                sql = "INSERT INTO nominee (member_name, party_name, symbol_name) VALUES (%s, %s, %s)"
                cur = mydb.cursor()
                cur.execute(sql, (member, party, logo))
                mydb.commit()
                cur.close()
                flash('Successfully registered a new nominee', 'success')
                return redirect(url_for('admin'))
            except Exception as e:
                flash('Database error while adding nominee: ' + str(e), 'danger')
                return redirect(url_for('add_nominee'))

    return render_template('nominee.html', admin=session.get('IsAdmin', False))

@app.route('/registration', methods=['POST','GET'])
def registration():
    if request.method=='POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        state = request.form['state']
        d_name = request.form['d_name']

        middle_name = request.form['middle_name']
        aadhar_id = request.form['aadhar_id']
        voter_id = request.form['voter_id']
        pno = request.form['pno']
        age = int(request.form['age'])
        email = request.form['email']
        voters=pd.read_sql_query('SELECT * FROM voters', mydb)
        all_aadhar_ids=voters.aadhar_id.values
        all_voter_ids=voters.voter_id.values
        if age >= 18:
            if (aadhar_id in all_aadhar_ids) or (voter_id in all_voter_ids):
                flash(r'Already Registered as a Voter')
            else:
                # Auto-verify on registration in this simplified edition.
                sql = 'INSERT INTO voters (first_name, middle_name, last_name, aadhar_id, voter_id, email,pno,state,d_name, verified) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)'
                cur=mydb.cursor()
                cur.execute(sql, (first_name, middle_name, last_name, aadhar_id, voter_id, email, pno, state, d_name, 'yes'))
                mydb.commit()
                cur.close()
                session['aadhar']=aadhar_id
                session['status']='yes'
                session['email']=email
                flash('Registration successful — you are verified and can vote now.', 'success')
                # Directly send the user to voting interface
                return redirect(url_for('voting'))
        else:
            flash("if age less than 18 than not eligible for voting","info")
    return render_template('voter_reg.html')


@app.route('/login_voter', methods=['POST','GET'])
def login_voter():
    """Simple voter login by Aadhar ID so returning users can vote.
    If the aadhar exists and is verified in the DB, set session and go to voting.
    """
    if request.method == 'POST':
        aadhar = str(request.form.get('aadhar', '')).strip()
        if not aadhar:
            flash('Please enter your Aadhar number', 'warning')
            return redirect(url_for('home'))
        try:
            s = "select * from voters where aadhar_id=%s"
            df = pd.read_sql_query(s, mydb, params=(aadhar,))
            if df.empty:
                flash('Aadhar number not found. Please register first.', 'warning')
                return redirect(url_for('registration'))
            # Check verification status (column may exist)
            verified = 'yes'
            if 'verified' in df.columns:
                verified = str(df.iloc[0][df.columns.get_loc('verified')])
            if verified.lower() == 'yes':
                session['aadhar'] = aadhar
                session['status'] = 'yes'
                session['email'] = df.iloc[0][df.columns.get_loc('email')] if 'email' in df.columns else None
                flash('Login successful — you can vote now.', 'success')
                return redirect(url_for('voting'))
            else:
                flash('Your account is not verified. Please contact admin or re-register.', 'warning')
                return redirect(url_for('registration'))
        except Exception as e:
            flash('Database error: ' + str(e), 'danger')
            return redirect(url_for('home'))
    # GET -> show a simple login form (we keep the form on home page; this route handles posts)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('aadhar', None)
    session.pop('status', None)
    session.pop('select_aadhar', None)
    session.pop('email', None)
    flash('Logged out', 'info')
    return redirect(url_for('home'))

@app.route('/verify', methods=['POST','GET'])
def verify():
    # Verification step removed: registration auto-verifies the voter.
    if session.get('status') == 'yes':
        flash('Your account is verified. You can vote now.', 'info')
        return redirect(url_for('voting'))
    else:
        # If somehow a user visits /verify without being registered, redirect them
        flash('Verification is automatic on registration. Please register first.', 'warning')
        return redirect(url_for('registration'))
    # no template - verification is automatic and handled via redirects

@app.route('/capture_images', methods=['POST','GET'])
def capture_images():
    # Face capture/enrollment has been removed in this edition.
    flash('Face capture is disabled. Please register and verify to vote.', 'info')
    return redirect(url_for('voting'))

# Face-recognition, image processing and training functionality were removed
# in this simplified edition. The train and capture endpoints are no-ops and
# redirect users to the admin/dashboard or voting pages as appropriate.
@app.route('/train', methods=['POST','GET'])
def train():
    flash('Model training is disabled in this edition.', 'info')
    return redirect(url_for('admin'))
@app.route('/update')
def update():
    return render_template('update.html')
@app.route('/updateback', methods=['POST','GET'])
def updateback():
    if request.method=='POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        aadhar_id = request.form['aadhar_id']
        voter_id = request.form['voter_id']
        email = request.form['email']
        pno = request.form['pno']
        age = int(request.form['age'])
        voters=pd.read_sql_query('SELECT * FROM voters', mydb)
        all_aadhar_ids=voters.aadhar_id.values
        if age >= 18:
            if (aadhar_id in all_aadhar_ids):
                sql="UPDATE VOTERS SET first_name=%s, middle_name=%s, last_name=%s, voter_id=%s, email=%s,pno=%s, verified=%s where aadhar_id=%s"
                cur=mydb.cursor()
                cur.execute(sql, (first_name, middle_name, last_name, voter_id, email,pno, 'no', aadhar_id))
                mydb.commit()
                cur.close()
                session['aadhar']=aadhar_id
                session['status']='no'
                session['email']=email
                flash(r'Database Updated Successfully','Primary')
                return redirect(url_for('verify'))
            else:
                flash(f"Aadhar: {aadhar_id} doesn't exists in the database for updation", 'warning')
        else:
            flash("age should be 18 or greater than 18 is eligible", "info")
    return render_template('update.html')

@app.route('/voting', methods=['POST','GET'])
def voting():
    # Ensure the voter has enrolled (registered) first
    if not session.get('aadhar'):
        flash('Please enroll/register before voting.', 'warning')
        return redirect(url_for('registration'))
    # Read nominees so we can show them directly on the voting page
    df_nom = pd.read_sql_query('select * from nominee', mydb)
    noms = []
    if not df_nom.empty:
        for _, row in df_nom.iterrows():
            noms.append({
                'symbol': row.get('symbol_name'),
                'member': row.get('member_name'),
                'party': row.get('party_name')
            })
    noms = sorted(noms, key=lambda x: (x.get('member') or '').lower())

    # If the voter is not verified yet, send them to verification on POST
    if request.method == 'POST':
        if session.get('status') != 'yes':
            flash('Please verify your account before voting.', 'warning')
            return redirect(url_for('verify'))
        # Verified: allow voting by forwarding to select_candidate (which handles insertion)
        session['select_aadhar'] = session.get('aadhar')
        return redirect(url_for('select_candidate'))

    # GET -> show voting page with all nominees listed so voter can pick one
    return render_template('voting.html', noms=noms)

@app.route('/select_candidate', methods=['POST','GET'])
def select_candidate():
    #extract all nominees
    # prefer the aadhar set by voting flow, fall back to session aadhar
    aadhar = session.get('select_aadhar') or session.get('aadhar')
    print(f'select_candidate: method={request.method}, aadhar={aadhar}')
    if not aadhar:
        flash("Please register/login to vote", "warning")
        return redirect(url_for('registration'))
    # Read nominees and build a list of dicts with symbol, member and party
    df_nom = pd.read_sql_query('select * from nominee', mydb)
    noms = []
    if not df_nom.empty:
        for _, row in df_nom.iterrows():
            noms.append({
                'symbol': row.get('symbol_name'),
                'member': row.get('member_name'),
                'party': row.get('party_name')
            })
    # sort nominees by member name for consistent ordering
    noms = sorted(noms, key=lambda x: (x.get('member') or '').lower())
    sq = "select * from vote"
    g = pd.read_sql_query(sq, mydb)
    all_adhar = g['aadhar'].values
    if aadhar in all_adhar:
        flash("You already voted", "warning")
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            # Store the chosen vote in session as a pending action and redirect to OTP verification
            vote = request.form.get('test')
            print(f'POST to select_candidate: vote={vote}')
            if not vote:
                flash('No candidate selected', 'warning')
                return redirect(url_for('select_candidate'))
            session['pending_vote'] = vote
            session['otp_verified'] = False  # Reset OTP verification
            print(f'Redirecting to send_otp with vote={vote}')
            return redirect(url_for('send_otp'))
    return render_template('select_candidate.html', noms=noms)

@app.route('/voting_res')
def voting_res():
    try:
        # Fetch all votes
        votes = pd.read_sql_query('select * from vote', mydb)
        # Fetch all nominees
        df_nom = pd.read_sql_query('select * from nominee', mydb)
        
        nominees = []
        if not df_nom.empty:
            for _, row in df_nom.iterrows():
                nominees.append({
                    'symbol': row.get('symbol_name'),
                    'member': row.get('member_name'),
                    'party': row.get('party_name')
                })
        
        # Compute vote counts per nominee
        results = []
        if not votes.empty:
            vote_counts = votes['vote'].value_counts().to_dict()
        else:
            vote_counts = {}
        
        for nom in nominees:
            sym = nom['symbol']
            count = vote_counts.get(sym, 0)
            results.append({
                'symbol': sym,
                'member': nom['member'],
                'party': nom['party'],
                'count': int(count)
            })
        
        # Sort by vote count (descending) for ranking
        results = sorted(results, key=lambda x: x['count'], reverse=True)
        
        return render_template('voting_res.html', results=results)
    except Exception as e:
        flash('Error loading results: ' + str(e), 'danger')
        return redirect(url_for('home'))


# Helper function to generate 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# Helper function to send OTP via SMS (using fast2sms API)
def send_otp_sms(phone, otp, name):
    try:
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        message = f'Hi {name}, Your OTP for voting verification is: {otp}. Valid for 10 minutes. Please do not share this OTP.'
        data = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": phone,
        }
        headers = {
            "authorization": "UwmaiQR5OoA6lSTz93nP0tDxsFEhI7VJrfKkvYjbM2C14Wde8g9lvA2Ghq5VNCjrZ4THWkF1KOwp3Bxd",
            "Content-Type": "application/json"
        }
        requests.post(url, headers=headers, json=data, timeout=5)
        return True
    except Exception as e:
        print('OTP SMS send failed:', e)
        return False


@app.route('/send_otp', methods=['POST', 'GET'])
def send_otp():
    """Send OTP to voter's phone for verification"""
    aadhar = session.get('aadhar')
    if not aadhar:
        flash('Please login first', 'warning')
        return redirect(url_for('voter_reg'))
    
    try:
        # Get voter details
        s = "select * from voters where aadhar_id=%s"
        df = pd.read_sql_query(s, mydb, params=(aadhar,))
        
        if df.empty:
            flash('Voter information not found', 'warning')
            return redirect(url_for('voting'))
        
        # Extract phone and name using column names (safer than index-based access)
        row = df.iloc[0]
        phone = ''
        name = 'User'
        
        if 'first_name' in df.columns and pd.notna(row.get('first_name')):
            name = str(row.get('first_name'))
        if 'pno' in df.columns and pd.notna(row.get('pno')):
            phone = str(row.get('pno')).strip()
        
        # Generate and store OTP
        otp = generate_otp()
        session['voting_otp'] = otp
        session['otp_time'] = time.time()
        session['otp_attempts'] = 0
        
        print(f'Generated OTP: {otp} for aadhar: {aadhar}, phone: {phone}')
        
        # Try to send SMS (non-blocking)
        sms_sent = False
        if phone and len(phone) >= 10:
            sms_sent = send_otp_sms(phone, otp, name)
            print(f'SMS send result: {sms_sent}')
        
        # Always flash the OTP for local testing/debugging
        flash(f'🔐 YOUR OTP: {otp}', 'success')
        
        if sms_sent:
            flash(f'✓ OTP also sent to your phone {phone[-4:]}', 'info')
        else:
            if not phone:
                flash(f'⚠️ No phone number on file. Update profile to enable SMS delivery.', 'warning')
            else:
                flash(f'⚠️ SMS delivery failed. Use the OTP above to continue.', 'warning')
        
        return redirect(url_for('verify_otp'))
    except Exception as e:
        print('Error in send_otp:', e)
        flash('Error processing request. Please try again.', 'danger')
        return redirect(url_for('voting'))


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """Verify OTP entered by voter"""
    aadhar = session.get('aadhar')
    if not aadhar:
        flash('Please login first', 'warning')
        return redirect(url_for('voter_reg'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        stored_otp = session.get('voting_otp')
        otp_time = session.get('otp_time', 0)
        otp_attempts = session.get('otp_attempts', 0)
        
        # Check if OTP has expired (10 minutes = 600 seconds)
        if time.time() - otp_time > 600:
            session.pop('voting_otp', None)
            flash('OTP expired. Please request a new one.', 'warning')
            return redirect(url_for('voting'))
        
        # Check max attempts (3 attempts)
        if otp_attempts >= 3:
            session.pop('voting_otp', None)
            flash('Maximum OTP attempts exceeded. Please request a new one.', 'danger')
            return redirect(url_for('voting'))
        
        # Verify OTP
        if entered_otp == stored_otp:
            # OTP verified successfully
            session['otp_verified'] = True
            session.pop('voting_otp', None)
            session.pop('otp_time', None)
            session.pop('otp_attempts', None)
            flash('OTP verified successfully!', 'success')
            return redirect(url_for('confirm_vote'))
        else:
            # Increment attempts
            session['otp_attempts'] = otp_attempts + 1
            remaining = 3 - session['otp_attempts']
            if remaining > 0:
                flash(f'Invalid OTP. {remaining} attempts remaining.', 'warning')
            else:
                flash('Maximum attempts exceeded. Please request a new OTP.', 'danger')
                session.pop('voting_otp', None)
            return redirect(url_for('verify_otp'))
    
    return render_template('verify_otp.html')


@app.route('/confirm_vote', methods=['GET', 'POST'])
def confirm_vote():
    # Require login
    if 'aadhar' not in session:
        flash('Please login to vote', 'warning')
        return redirect(url_for('voter_reg'))

    aadhar = session['aadhar']
    
    # Check if OTP has been verified
    if not session.get('otp_verified'):
        flash('Please verify with OTP before confirming your vote', 'warning')
        return redirect(url_for('send_otp'))

    # Prevent double voting
    cur = mydb.cursor()
    cur.execute("SELECT aadhar FROM vote WHERE aadhar=%s", (aadhar,))
    already = cur.fetchone()
    cur.close()
    if already:
        flash('You have already voted', 'warning')
        return redirect(url_for('home'))

    pending = session.get('pending_vote')
    if not pending:
        flash('No candidate selected to confirm', 'warning')
        return redirect(url_for('voting'))

    # On POST, finalize the vote
    if request.method == 'POST':
        vote = pending
        try:
            cur = mydb.cursor()
            cur.execute("INSERT INTO vote (vote, aadhar) VALUES (%s, %s)", (vote, aadhar))
            mydb.commit()
            cur.close()
        except Exception as e:
            print('DB insert failed:', e)
            flash('Failed to record vote. Please try again.', 'danger')
            return redirect(url_for('voting'))

        # Optional: attempt SMS send (non-blocking)
        try:
            s = "select * from voters where aadhar_id=%s"
            c = pd.read_sql_query(s, mydb, params=(aadhar,))
            pno = str(c.values[0][7]) if c.shape[0] > 0 else ''
            name = str(c.values[0][1]) if c.shape[0] > 0 else ''
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            url = "https://www.fast2sms.com/dev/bulkV2"
            message = f'Hi {name} You voted successfully at {timeStamp} on {date}.'
            data1 = {
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": pno,
            }
            headers = {
                "authorization": "UwmaiQR5OoA6lSTz93nP0tDxsFEhI7VJrfKkvYjbM2C14Wde8g9lvA2Ghq5VNCjrZ4THWkF1KOwp3Bxd",
                "Content-Type": "application/json"
            }
            requests.post(url, headers=headers, json=data1, timeout=5)
        except Exception as e:
            print('fast2sms send failed (non-blocking):', e)

        # Clear pending vote
        session.pop('pending_vote', None)
        flash('Voted Successfully', 'success')
        return redirect(url_for('home'))

    # For GET, show confirmation page with pending candidate details
    # Fetch nominee details for display
    cur = mydb.cursor()
    cur.execute("SELECT symbol_name, member_name, party_name FROM nominee WHERE symbol_name=%s", (pending,))
    row = cur.fetchone()
    cur.close()
    nominee = None
    if row:
        nominee = {'symbol': row[0], 'member': row[1], 'party': row[2]}

    return render_template('confirm_vote.html', nominee=nominee)

if __name__=='__main__':
    app.run(debug=True)

