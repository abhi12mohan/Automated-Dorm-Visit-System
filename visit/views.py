from visit import *
from dateutil.parser import parse as parse_date
from aes_encryption import AesEncryption
from Crypto.Cipher import AES
import base64
import binascii




@app.route('/')
def index():
    aes = AesEncryption()
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        kerberos = request.form['kerberos']
        student_id = request.form['student_id']
        dorm = request.form['dorm']

        insert_into_database(firstname, lastname, kerberos, student_id, dorm)

        # Putting yourself on your guest list
        host_kerb = request.form['kerberos']
        host = check_login(host_kerb)[0]
        insert_into_connections(host, host)
        #
        return redirect(url_for('index'))


    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = check_login(request.form['kerberos'])
        if(str(user[4]) == request.form['student_id']):
            session['logged_in'] = True
            session['kerberos'] = request.form['kerberos']
            return redirect(url_for('dashboard'))
        else:
            return 'Incorrect information.'

    return render_template('login.html')
@app.route('/dashboard')
@login_required
def dashboard():
    guest_list = []
    your_kerberos = session['kerberos']
    get_guests_of_user(your_kerberos, guest_list)




    return render_template('dashboard.html', guest_list=guest_list)

@app.route('/guest-list-entry', methods=['GET', 'POST'])
@login_required
def guest_list_entry():
    your_kerberos = session['kerberos']

    if request.method == 'POST':
        friend_kerberos = request.form['friend_kerberos']
        you = check_login(your_kerberos)[0]
        them = check_login(friend_kerberos)[0]
        insert_into_connections(you, them)

        return redirect(url_for('dashboard'))

    return render_template('guest_entry.html')

@app.route('/edit-information', methods=['GET', 'POST'])
@login_required
def edit_information():

    your_kerberos = session['kerberos']


    if request.method == 'POST':
        dorm = request.form['dorm']

        update_dorm_info(your_kerberos, dorm)

        return redirect(url_for('dashboard'))




    you = fetch_user_by_kerb(your_kerberos)


    dorm = you[5]

    return render_template('edit_information.html', dorm=dorm)



@app.route('/access', methods=['GET', 'POST'])
def access():


    if request.method == 'POST':
        key = bytes('abcdefghijklmnop').encode('utf-8')

        cipher = AES.new(key, AES.MODE_ECB)
        # ciphertext = "MESSAGE TO DEBUG****************"
        #Thi

        ciphertext = request.form.get('studentID') #cipher.encrypt(b'Tech tutorials x')
        # msg = bytes(ciphertext, encoding = 'utf-8') #converts mg to Byte type
        #print(str(msg))

        # print(binascii.unhexlify(mg))

        decipher = AES.new(key, AES.MODE_ECB)
        # print(binascii.hexlify(decipher.decrypt(msg)))

        decrypted = decipher.decrypt(binascii.unhexlify(ciphertext)).decode("utf-8")

        #Taking off padding
        while decrypted[-1] == '?':
            decrypted = decrypted[:-1]


        studentID = decrypted
        dorm = request.form.get('dorm')



        requesting_student = fetch_user_by_sid(decrypted)

        if not requesting_student:
            return 'Not a valid student in the database'
        requesting_student_id = requesting_student[0]
        insert_into_attempts(studentID, requesting_student[1], requesting_student[2], requesting_student[3])

        conns = []
        get_conns_of_user(requesting_student_id, conns)
        granted_access = False
        for c in conns:
            if fetch_user_by_id(c[1])[5] == dorm:
                granted_access = True


        return str(granted_access)


@app.route('/delete/<guest_id>', methods=['GET', 'POST'])
@login_required
def delete_guest(guest_id):
    your_kerberos = session['kerberos']
    user = fetch_user_by_kerb(your_kerberos)
    your_id = user[0]

    remove_a_guest(your_id, guest_id)

    return redirect(url_for('dashboard'))




@app.route('/guest-worker', methods=['GET', 'POST'])
@login_required
def guest_worker():
    atts = []
    get_all_attempts(atts)

    recent_entries = []
    now = datetime.now()
    for k in atts:
        dt = parse_date(k[5])
        print(dt)
        if(dt <= now + timedelta(minutes=10)):
            recent_entries.append(k)






    return render_template('guest_worker.html', recent_entries=recent_entries)



@app.route('/all-attempts')
def get_attempts():
    atts = []
    get_all_attempts(atts)
    return str(atts)

@app.route('/all')
def get_all():
    studs = []
    lookup_database(studs)
    return str(studs)

@app.route('/all-connections')
def get_all_connections():
    conns = []
    lookup_connections(conns)
    return str(conns)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))
