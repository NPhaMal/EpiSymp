from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3, spacy, random, string, os, pickle, smtplib, json
import matplotlib.pyplot as plt
from spacy.tokens import DocBin #,Doc, Span, Token
from io import BytesIO
from collections import Counter
from datetime import datetime
import pandas as pd
import geopandas as gd
from spellchecker import SpellChecker
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#import pybase64

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set your own secret key

def send_email(message):
    sender_email = 'phamal17@gmail.com'
    receiver_email = 'n02017446w@students.nust.ac.zw'
    subject = 'EpiSymp: Outbreak Prediction'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'phamal17@gmail.com'
    smtp_password = 'euoo dgue krzs lfwf'
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add message body
    msg.attach(MIMEText(message, 'plain'))

    # Create SMTP session
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start TLS for security
        server.starttls()
        # Login to SMTP server
        server.login(smtp_username, smtp_password)
        # Send email
        server.send_message(msg)

def generate_random_integer_code():
    return random.randint(1000, 9999)

def generate_random_string_code(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def sess_gen():
    # Generate random integer code
    random_integer_code = generate_random_integer_code()

    # Generate random string code
    random_string_code = generate_random_string_code(4)

    x = random_string_code + str(random_integer_code) 

    return x

def gdf_to_geojson(df, properties=None):
    print(df)
    for column in df.select_dtypes(include=['datetime', 'datetimetz']):
        df[column] = df[column].astype(str)
    geojson = json.loads(df.to_json())
    if properties:
        for feature in geojson['features']:
            feature['properties'] = {prop: feature['properties'][prop] for prop in properties}
    return geojson

def get_df(x,y):
    # Read Shapefile
    shapefile_path = "./zwe_admbnda_adm3_zimstat_ocha_20180911/zwe_admbnda_adm3_zimstat_ocha_20180911.shp"
    gdf = gd.read_file(shapefile_path)

    # Filter Harare shape data
    B_wards = gdf[gdf['ADM1_EN'] == 'Bulawayo']
    B_wards = B_wards.sort_values(by='ADM3_EN', ascending=True)
    B_wards = B_wards.rename(columns={'ADM3_EN': 'Wards'})

    start_date = datetime.today().date()

    # Generate a date range for the last seven days
    date_range = pd.date_range(end=start_date, periods=y, freq='D')

    # Create an empty DataFrame
    df = pd.DataFrame()

    ward = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    wards = []

    for i in ward:
        wards.append(str(i))

    df['Wards'] = wards
    df['Number_of_Diagnosed'] = None

    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        df = df.fillna(0)
        c.execute("SELECT Suburb FROM Survey WHERE Disease=? AND Date=?", (x, date_str,))
        b = c.fetchall()
        d = tuple_convert(b)
        z = []
        for k in b:
            j = k[0]
            z.append(j)
        for l in d:
            c.execute("SELECT Ward FROM Suburb_list WHERE Suburb=?", (l,))
            ward_surb = c.fetchone()
            df.loc[df['Wards'] == str(ward_surb[0]), 'Number_of_Diagnosed'] += Counter(z)[l]

    conn.commit()
    conn.close()

    # Merge Data
    merged_data = B_wards.merge(df, on='Wards')

    return merged_data

# For simplicity, we'll use a hardcoded username and password. In a real app, use a database.
valid_username = "admin"
valid_password = "admin"
s1 = []
#testcode = 'fail'

def create_app():
    """
    Create the Flask app.

    Returns:
        Flask: The Flask app instance.
    """
    return app


@app.route('/', methods=['GET', 'POST'])
def index():
    session['test']= sess_gen()
    return render_template('index.html')

def save_to_database(ward):
    # Database connection
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute("SELECT Suburb FROM Suburb_list WHERE ID=?", (ward,))
    ward_v = c.fetchone()

    # Insert session ward into database
    if 'test' in session:
        y = session['test']
    c.execute('INSERT INTO Session (Suburb, Session) VALUES (?, ?)', (ward_v[0], y,))
    
    # Close database connection
    conn.commit()
    conn.close()

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.get_json()
    ward = data['ward']
    save_to_database(ward)
    return 'worked'

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']
    response = get_chatbot_response(user_message)
    return jsonify({'message': response})

def get_chatbot_response(message):
    # AI chatbot logic
    symptom = message.lower()
    sess = session['test']
    if symptom == 'hello':
        return f'Hi there!'
    elif symptom == 'how are you?':
        return 'I am doing well, thank you. How are you feeling'
    else:
        #print(sess)
        return symptom_checker(symptom, sess)
    
def analyze_and_fix_spelling(paragraph):
    # Initialize the spell checker
    spell = SpellChecker()

    # Tokenize the paragraph into individual words
    words = paragraph.split()

    # List to store corrected words
    corrected_words = []

    # Iterate over each word in the paragraph
    for word in words:
        # Check if the word is misspelled
        if not spell.correction(word.lower()) == word.lower():
            # Correct the spelling of the word
            corrected_word = spell.correction(word)
            corrected_words.append(corrected_word)
        else:
            # Word is correctly spelled, no correction needed
            corrected_words.append(word)

    # Join the corrected words back into a paragraph
    corrected_paragraph = ' '.join(corrected_words)

    return corrected_paragraph

def symptom_checker(symptom, sess):
    symptom_c = analyze_and_fix_spelling(symptom)

    # Load the existing model
    new_model = spacy.load("./new_model/ouput/model-best")
    doc = new_model(symptom_c)

    # identify symptoms from text to list
    symptoms = []
    for ent in doc.ents:
        if ent.label_ == "SYMPTOM":
            symptoms.append(ent.text)

    # Database connection
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    # Query database for the condition associated with the symptom
    conditions = []
    cond_list = []
    z = 1
    symptom_txt = ''
    sert = 'INSERT INTO Survey (Session, Disease, Suburb, Date, Symptoms) VALUES (?, ?, ?, ?, ?)'
    sorry = "I'm sorry, I couldn't determine the condition based on the symptoms,"
    if symptoms:
        for a in symptoms:
            symptom_txt = symptom_txt + a
            for i in range(1, 18, 1):
                c.execute(f'SELECT Disease FROM Symptom_data WHERE Symptom_{i}=?', (a,))
                d = c.fetchall()
                e = tuple_convert(d)
                conditions.append(e)
        for i in conditions:
            for h in i:
                if h:
                    cond_list.append(h)

        if cond_list:
            count_cond = Counter(cond_list)
            max_freq = max(count_cond.values())
            modes = [num for num, freq in count_cond.items() if freq == max_freq]
            sev_peak = 11
            for dis in modes:
                c.execute('SELECT Severity FROM Diseases WHERE Disease=?', (dis,))
                sev_amt = c.fetchone()[0]
                if sev_amt < sev_peak:
                    result = dis
                sev_peak = sev_amt
        else:
            result = False
    else:
        result = False

    c.execute('SELECT Suburb FROM Session WHERE Session=?', (sess,))
    ward = c.fetchone()

    #c.execute('SELECT Hospital FROM Health_centre WHERE Suburb=?', (ward[0],))
    #hosp = c.fetchone()
    recom = f"Please visit Mpilo Central Hospital for a checkup"
    timestamp = datetime.now().strftime('%Y-%m-%d')
    symp_text = ''
    for sym in symptoms:
        if symp_text:
            symp_text += f', {sym}'
        else:
            symp_text += sym

    if result and symptoms:
        c.execute(sert, (sess, result, ward[0], timestamp, symp_text,))
        if "Unindentified" in result:
            answer = f"{sorry} {symptom_txt}. {recom}. Are you feeling any other symptoms?"
        else:
            answer = f"Based on your symptoms, {symptom_txt}, it appears that you potentially have {result}. You can open the Education Tab for more Information on the disease. {recom}. Are you feeling any other symptoms?"
    elif symptoms:
        dis_code = f"Unindentified{sess}"
        dis_info = "Unknown Disease, Inforamtion is yet to be updated"
        c.execute(sert, (sess, dis_code, ward[0], timestamp, symp_text,))
        c.execute('INSERT INTO Symptom_data (Disease) VALUES (?)', (dis_code,))
        c.execute('INSERT INTO Diseases (Disease, Information, Severity) VALUES (?, ?, ?)', (dis_code, dis_info, 10))
        c.execute('INSERT INTO Disease_diag (Code, Symptoms) VALUES (?, ?)', (dis_code, symp_text,))
        for l in symptoms:
            c.execute(f'UPDATE Symptom_data SET Symptom_{z}=? Where Disease=?', (l, dis_code,))
            z += 1
        answer = f"{sorry} {symptom_txt}, {recom}. Are you feeling any other symptoms?"
    else:
        answer = f"{sorry} May you please rephrase your symptoms to simpler words."

    # Close database connection
    conn.commit()
    conn.close()

    return answer

@app.route('/search')
def search():
    query = request.args.get('q')

    # Perform search logic here
    results = [get_row_as_dict('Diseases', query)]
    return jsonify(results)
    
def get_row_as_dict(table_name, row_id):
    conn = sqlite3.connect('symptoms.db')
    cursor = conn.cursor()

    # Assuming the table has columns 'id', 'name', 'description'
    cursor.execute(f"SELECT * FROM {table_name} WHERE Disease=?", (row_id,))
    row = cursor.fetchone()

    if row:
        columns = [description[0] for description in cursor.description]
        row_dict = dict(zip(columns, row))
    else:
        row_dict = {'Disease': f'{row_id}', 'Information': 'No results Found', 'Severity': 0}

    conn.close()
    
    return row_dict
    
@app.route('/start', methods=['GET', 'POST'])
def start():
    """
    Render the login page.

    Returns:
        render_template: Rendered login.html template.
    """
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    log_id = authenticate(username,password)
    
    if log_id:
        session['user'] = username
        return redirect(url_for('predict'))
    else:
        flash('Login failed. Please check your username and password.', 'danger')
        return redirect(url_for('start'))
    
def authenticate(x,y):
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Username FROM Users")
    users_user = tup_to_list(c.fetchall())

    c.execute("SELECT Password FROM Users")
    users_pass = tup_to_list(c.fetchall())

    conn.commit
    conn.close

    if x in users_user and y in users_pass:
        correct = True
    else:
        correct = False

    return correct
    
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    condition, users = dash_stats()
    data = data_graph(condition)
    ldata = line_graph('Common Cold')
    df = stat_table()
    stable_html = new_symptom_table().to_html(index=False, classes="table")
    table_html = df.to_html(index=False, classes="table")
    out_state, memo = outbreak_pred()
    if out_state:
        alert_note = f"Potential outbreaks: {out_state['Disease']}"
    else:
        alert_note = "No Potential Outbreaks Detected"

    r_diag = diag()
    dataf = get_df(condition, 30)
    geodata = gdf_to_geojson(dataf, properties= None)  # specify relevant properties
    return render_template('predict.html', condition=condition, data=data, ldata=ldata, users=users, stable_html=stable_html, table_html=table_html, alert_note=alert_note, r_diag=r_diag, geodata=geodata)

@app.route('/statsearch', methods=['GET', 'POST'])
def statsearch():
    # Get the search query from the form
    search_query = request.args.get('q')

    avail, query = db_check(search_query)

    if avail:
        # Return the data as JSON response
        dataf = get_df(query, 60)
        mapdata = gdf_to_geojson(dataf, properties= None)  # specify relevant properties
        graph_data = data_graph(query)
        l_graph = line_graph(query)
        table_data = search_table(query)[['Disease', 'Infected', 'Suburb_Most_Infected', 'Number_Infected_in_Suburb']].to_dict(orient='records')
        response = {
            'reply': 1,
            'map_data': mapdata,
            'graph_title': query,
            'chart_data': graph_data,
            'line_data': l_graph,
            'table_data': table_data
        }
    else:
        response = {
            'reply': 0
        }

    return jsonify(response)

@app.route('/run', methods=['GET', 'POST'])
def run():
    pred_data= []
    memo = "No Potential Outbreaks"
    if pred_data:
        data = f"Potential outbreaks: {pred_data['Disease']}"
    else:
        data = "No Potential Outbreaks Detected"

    send_email(memo)

    return jsonify(data)

@app.route('/report', methods=['GET', 'POST'])
def report():
    #report_val = request.get_json()
    disease = request.form['disreport']
    d_rae = int(request.form['dayreport'])
    x = disease
    rep_dataf = get_df(x, d_rae)
    rep_map = gdf_to_geojson(rep_dataf, properties= None)  # specify relevant properties
    table_data = suburb_tab_report(x,d_rae)[['Suburb', 'Number_Infected']].to_dict(orient='records')
    date_data = day_tab_report(x,d_rae)[['Day', 'Number_Infected']].to_dict(orient='records')
    sub_graph = data_graph_report(x,d_rae)
    week_graph = line_graph_report(x,d_rae)
    data = {
            'reply': 1,
            'graphTitle': x,
            'tableData': table_data,
            'dateTable': date_data,
            'barData': sub_graph,
            'lineData': week_graph,
            'repMap': rep_map
        }
    return render_template('report.html', disease=disease, data=data)

def suburb_tab_report(condition, drange):
    s_list = []
    sub_list = []
    num_infect = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    start_date = datetime.today().date()
    date_range = pd.date_range(end=start_date, periods=drange, freq='D')
    for date in date_range:
        x = date.strftime('%Y-%m-%d')
        c.execute('SELECT Suburb FROM Survey WHERE Disease=? AND Date=?', (condition, x,))
        s_data = tup_to_list(c.fetchall())
        for k in s_data:
            s_list.append(k)

    conn.commit()
    conn.close()

    sub_count = Counter(s_list)
    for i in s_list:
        if i not in sub_list:
            sub_list.append(i)
    
    for j in sub_list:
        num_infect.append(sub_count[j])

    sub_table = {
        'Suburb': sub_list,
        'Number_Infected': num_infect
    }

    df = pd.DataFrame(sub_table)
    return df

def day_tab_report(condition, d_range):
    s_list = []
    tab_dates = []
    date_count = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    start_date = datetime.today().date()
    date_range = pd.date_range(end=start_date, periods=d_range, freq='D')
    for date in date_range:
        x = date.strftime('%Y-%m-%d')
        c.execute('SELECT Session FROM Survey WHERE Disease=? AND Date=?', (condition, x,))
        s_data = tup_to_list(c.fetchall())
        tab_dates.append(x)
        date_count.append(len(s_data))

    conn.commit()
    conn.close()

    date_table = {
        'Day': tab_dates,
        'Number_Infected': date_count
    }

    df = pd.DataFrame(date_table)
    return df

def data_graph_report(condition, d_range):
    g_list = []
    sub_list = []
    n_infect = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    start_date = datetime.today().date()
    date_range = pd.date_range(end=start_date, periods=d_range, freq='D')
    for date in date_range:
        x = date.strftime('%Y-%m-%d')
        c.execute("SELECT Suburb FROM Survey WHERE Disease=? AND Date=?", (condition, x,))
        g = tup_to_list(c.fetchall())
        for l in g:
            g_list.append(l)

    conn.commit()
    conn.close()
    g_count = Counter(g_list)
    for i in g_list:
        if i not in sub_list:
            sub_list.append(i)

    for j in sub_list:
        n_infect.append(g_count[j])

    v = len(sub_list)
    gdata = []
    for i in range(v):
        gdata.append((sub_list[i],n_infect[i]))
    
    return gdata

def line_graph_report(disease, d_range):
    ldata = []
    start_date = datetime.today().date()
    date_range = pd.date_range(end=start_date, periods=d_range, freq='D')
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    for date in date_range:
        x = date.strftime('%Y-%m-%d')
        c.execute("SELECT Disease FROM Survey WHERE Date=?", (x,))
        dlist = tup_to_list(c.fetchall())
        count_dlist = Counter(dlist)
        y = count_dlist[disease]
        ldata.append((x,y))
    
    conn.commit()
    conn.close()
    return ldata

@app.route('/diag')
def diag():
    data = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute('SELECT Code FROM Disease_diag')
    d_codes = tup_to_list(c.fetchall())
    if d_codes:
        d_symptoms = []
        d_id = []

        for i in d_codes:
            c.execute('SELECT Symptoms FROM Disease_diag WHERE Code=?', (i,))
            d_symptoms.append(c.fetchone()[0])
            c.execute('SELECT ID FROM Disease_diag WHERE Code=?', (i,))
            d_id.append(c.fetchone()[0])

        num_v = len(d_codes)

        for i in range(num_v):
            symp_data = {'Identifier': d_id[i], 'Code' : d_codes[i] , 'Symptoms' : d_symptoms[i]}
            data.append(symp_data)

    else:
        data.append({'Identifier': 0, 'Code': 'No Unindentified Diseases'})

    conn.commit()
    conn.close()
    return jsonify(data)

@app.route('/symp', methods=['GET', 'POST'])
def symp():
    val = request.get_json()
    Diagnose = val['Diagnose']
    identifier = val['Code']
    print(identifier, Diagnose)   
    doct = 'Larry Stone'
    data = []
    # Update record
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute('SELECT Code FROM Disease_diag WHERE ID=?', (identifier,))
    Code =c.fetchone()[0]

    c.execute('SELECT Code FROM Diagnosis')
    diag_codes = tup_to_list(c.fetchall())

    

    c.execute('SELECT Symptoms FROM Disease_diag WHERE Code=?', (Code,))
    d_symptom =c.fetchone()[0]

    data = []
    symp_data = {'Code' : Code , 'Symptoms' : d_symptom}
    data.append(symp_data)
    
    if Code in diag_codes:
        conn.close()
        return redirect(url_for('diag'))

    c.execute('INSERT INTO Diagnosis (Code, Disease, Symptoms, Doctor) VALUES (?,?,?,?)', (Code, Diagnose, d_symptom, doct,))

    c.execute('DELETE FROM Disease_diag WHERE Code=?', (Code,))

    conn.commit()
    conn.close()

    # Render the edit form with the existing record values
    return redirect(url_for('diag'))

@app.route('/review', methods=['GET', 'POST'])
def review():
    revdata = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute('SELECT Code FROM Diagnosis')
    d_codes = tup_to_list(c.fetchall())
    if d_codes:
        d_symptoms = []
        d_id = []
        d_dis = []

        for i in d_codes:
            c.execute('SELECT Symptoms FROM Diagnosis WHERE Code=?', (i,))
            d_symptoms.append(c.fetchone()[0])
            c.execute('SELECT ID FROM Diagnosis WHERE Code=?', (i,))
            d_id.append(c.fetchone()[0])
            c.execute('SELECT Disease FROM Diagnosis WHERE Code=?', (i,))
            d_dis.append(c.fetchone()[0])

        num_v = len(d_codes)

        for i in range(num_v):
            symp_data = {'Identifier': d_id[i], 'Code' : d_codes[i] , 'Symptoms' : d_symptoms[i], 'Disease': d_dis}
            revdata.append(symp_data)

    else:
        revdata.append({'Identifier': 0, 'Code': 'No New Diagnosed Diseases'})

    conn.commit()
    conn.close()
    return jsonify(revdata)

@app.route('/approve', methods=['GET', 'POST'])
def approve():
    diag_json = request.get_json()
    dis_diag = diag_json['Diagnosis']
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute('SELECT Code FROM Diagnosis WHERE Disease=?', (dis_diag,))
    diag_code = c.fetchone()[0]

    conn.commit()
    conn.close()
    return redirect(url_for('review'))

@app.route('/deny', methods=['GET', 'POST'])
def deny():
    diag_json = request.get_json()
    dis_diag = diag_json['Code']
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()

    c.execute('SELECT Code FROM Diagnosis WHERE ID=?', (dis_diag,))
    diag_code = c.fetchone()[0]
    c.execute('SELECT Symptoms FROM Diagnosis WHERE ID=?', (dis_diag,))
    diag_symp = c.fetchone()[0]

    c.execute('INSERT INTO Disease_diag (Code, Symptoms) VALUES (?,?)', (diag_code, diag_symp,))

    c.execute('DELETE FROM Diagnosis WHERE Code=?', (diag_code,))

    conn.commit()
    conn.close()
    return redirect(url_for('review'))
    

def line_graph(disease):
    ldata = []
    start_date = datetime.today().date()
    date_range = pd.date_range(end=start_date, periods=7, freq='D')
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    for date in date_range:
        x = date.strftime('%Y-%m-%d')
        c.execute("SELECT Disease FROM Survey WHERE Date=?", (x,))
        dlist = tup_to_list(c.fetchall())
        count_dlist = Counter(dlist)
        y = count_dlist[disease]
        ldata.append((x,y))
    
    conn.commit()
    conn.close()
    return ldata

def data_graph(b):
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Suburb FROM Survey WHERE Disease=?", (b,))
    g = c.fetchall()
    conn.close()
    x = tuple_convert(g)
    y = []
    cnt = 0 

    for i in x:
        for j in g:
            k = j[0]
            if i == k:
                cnt +=1
        y.append(cnt)
        cnt = 0

    v = len(x)
    gdata = []
    for i in range(v):
        gdata.append((x[i],y[i]))
    
    return gdata

def tuple_convert(s):
    s5 = []
    for i in s:
        j = i[0]
        if j not in s5:
            s5.append(j)
    
    return s5

def tup_to_list(s):
    s5 = []
    for i in s:
        j = i[0]
        s5.append(j)

    return s5

def find_most_frequent(lst):
    # Count the occurrences of each element in the list
    counter = Counter(lst)
    
    # Find the most common element(s) and their count(s)
    most_common = counter.most_common(1)
    
    # Extract the most common element and its count
    most_frequent_value, frequency = most_common[0]
    
    return most_frequent_value, frequency

def dash_stats():
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Disease FROM Survey")
    data = c.fetchall()
    conn.close()
    x = tup_to_list(data)
    
    y, z = find_most_frequent(x)
    num_cnt = len(x)
    perc = int(z/num_cnt*100)
    dstats = [f'{num_cnt}', f'{perc}%']
    print(dstats)
    return y, dstats

def stat_table():
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Disease FROM Survey")
    data = c.fetchall()
    t = []
    v = []
    x = tup_to_list(data)
    y = []
    w = Counter(x)
    u = tuple_convert(data)
    for i in u:
        y.append(w[i])
        c.execute("SELECT Suburb FROM Survey WHERE Disease=?", (i,))
        wdata = c.fetchall()
        z = tup_to_list(wdata)
        surb, surb_amt = find_most_frequent(z)
        v.append(surb)
        t.append(surb_amt)
        #print(z)
    
    conn.commit()
    conn.close()
    tdata = {
        "Disease": u,
        "Infected": y,
        "Suburb Most Infected": v,
        "Number Suburb Infected": t
    }

    df = pd.DataFrame(tdata)
    stt = df.sort_values(by='Infected', ascending=False)
    stats_table = stt.head(3)
    return stats_table

def new_symptom_table():
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Disease FROM Survey")
    sdata = c.fetchall()
    sx = tup_to_list(sdata)
    w = Counter(sx)
    dis_list = tuple_convert(sdata)
    dname = []
    dinfect =[]
    dsymp = []

    for i in dis_list:
        if "Unindentified" in i:
            dname.append(i)
            dinfect.append(w[i])
            c.execute("SELECT Symptoms FROM Survey WHERE Disease=?", (i,))
            dsymp.append(c.fetchone()[0])
    
    conn.commit()
    conn.close()
    stdata = {
        "Disease Code": dname,
        "Infected": dinfect,
        "Symptoms": dsymp,
    }

    df = pd.DataFrame(stdata)
    return df

def search_table(x):
    u = []
    z = []
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Disease FROM Survey")
    data = c.fetchall()
    for i in data:
        j = i[0]
        u.append(j)
    
    t = Counter(u)[x]
    c.execute("SELECT Suburb FROM Survey WHERE Disease=?", (x,))
    wdata = c.fetchall()
    for k in wdata:
        j = k[0]
        z.append(j)
    surb, surb_amt = find_most_frequent(z)

    conn.commit()
    conn.close()
    tdata = {
        "Disease": [x],
        "Infected": [t],
        "Suburb_Most_Infected": [surb],
        "Number_Infected_in_Suburb": [surb_amt]
    }
    df = pd.DataFrame(tdata)
    return df

def model_table(x):
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    start_date = datetime.today().date()

    # Generate a date range for the last seven days
    date_range = pd.date_range(end=start_date, periods=7, freq='D')

    # Create an empty DataFrame
    df = pd.DataFrame()

    df['Ward'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

    # Add the date columns to the DataFrame
    for date in date_range:
        df[date.strftime('%Y-%m-%d')] = None
        date_str = date.strftime('%Y-%m-%d')
        df = df.fillna(0)
        c.execute("SELECT Suburb FROM Survey WHERE Disease=? AND Date=?", (x, date_str,))
        b = c.fetchall()
        d = tuple_convert(b)
        z = []
        for k in b:
            j = k[0]
            z.append(j)
        for l in d:
            c.execute("SELECT Ward FROM Suburb_list WHERE Suburb=?", (l,))
            ward_surb = c.fetchone()
            df.loc[df['Ward'] == ward_surb, date_str] += Counter(z)[l]
    
    df['Day 8'] = None
    df = df.fillna(0)
    df.columns = ['Ward', 'Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8']
    conn.commit()
    conn.close()

    return df

def outbreak_pred():
    #create empty outbreak dictionary
    new_row = []

    # Load the trained model from the saved file
    pred_model = pickle.load(open('trained_model.pkl', 'rb'))

    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute("SELECT Disease FROM Survey")
    a = c.fetchall()
    disease_list = tuple_convert(a)
    severity = []
    for dis in disease_list:
        c.execute("SELECT Severity FROM Diseases WHERE Disease=?", (dis,))
        sev = c.fetchone()
        if sev:
            severity.append(sev[0])

    for i in disease_list:
        if i:
            outbreak_df = model_table(i)
            index = disease_list.index(i)
            X_pred = outbreak_df.drop(['Ward', 'Day 8'], axis=1)
            pred_array = pred_model.predict(X_pred)
            perc_thresh = 10 - severity[index]
            pstn = 1
            for pred in pred_array:
                if pstn <= 29:
                    c.execute("SELECT population FROM population WHERE ward=?", (pstn,))
                    pop_value = c.fetchone()
                    thresh_value = (perc_thresh/100)*pop_value[0]
                    pstn += 1
                    if pred > thresh_value:
                        c.execute("SELECT Suburb FROM Suburb_list WHERE Ward=?", (pstn - 1,))
                        subs = tup_to_list(c.fetchall())
                        subb, subb_amt = find_most_frequent(subs)
                        new_row = {'Disease': i , 'Suburb': subb}

    conn.commit()
    conn.close()

    if new_row:
        message = f"Potential outbreaks: {new_row['Disease']}"
    else:
        message = "No Potential Outbreaks"
    return new_row, message

def db_check(search):
    conn = sqlite3.connect('symptoms.db')
    c = conn.cursor()
    c.execute('SELECT Session FROM Survey WHERE Disease=?', (search,))
    search_results = tup_to_list(c.fetchall())

    if len(search_results) > 0:
        avail = True
        c.execute('SELECT Disease FROM Survey WHERE Session=?', (search_results[0],))
        query = c.fetchone()[0]
    else:
        avail = False
        query = None

    conn.commit()
    conn.close()

    return avail, query
        

if __name__ == '__main__':
    app.run(debug=True)