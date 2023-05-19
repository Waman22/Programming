from flask import Flask,render_template, request, redirect, url_for 
import sqlite3
import random
import time

app= Flask(__name__)



@app.route("/")
def Home():
    return render_template("home.html")

@app.route("/Services")
def services():
    return render_template("services.html")

@app.route("/About")
def About():
    return render_template("about.html")


@app.route("/sign", methods = ['POST', 'GET'])
def sign():
    if request.method== 'POST':
        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        password = request.form['password']
        Date = request.form['Dob']
        email = request.form['email']
        Address = request.form['Address']
        conn = sqlite3.connect('Sensors.db')
        c = conn.cursor()# starts the connection or commincation with the database
        c.execute('SELECT * FROM Sign WHERE username = ?', (username,))
        user = c.fetchone()

        if user is  None:
                c.execute("INSERT INTO Sign(name, surname, username, password, Dob ,  email, Address) VALUES(?,?,?,?,?,?,?)",(name, surname, username, password, Date , email, Address))
                conn.commit() #saves the database
                return redirect(url_for('login2'))
        else:
            return render_template("sign.html")
    else:
        return render_template("sign.html")


@app.route("/login2", methods = ['POST', 'GET'])
def login2():
    if request.method== 'POST':
        username = request.form['username']  #request input from the html page
        password = request.form['password']
        conn = sqlite3.connect('Sensors.db')
        c = conn.cursor()
        c.execute("SELECT * FROM  Sign  WHERE username = ? AND password = ?", (username,password)) #check if a row exists where the username and password match the provided values
        user = c.fetchone()

        if user is not None:
            return redirect(url_for('index3', username=username))
        else:
            error = "Username or Password is incorrect!!, TRY Again or SIGN UP."
            return render_template("login2.html",error = error)
    else:
        return render_template("login2.html")

@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        
        conn = sqlite3.connect('Sensors.db')
        c = conn.cursor()
        c.execute("SELECT password FROM Sign WHERE username = ?", (username,))
        password = c.fetchone()

        if password is not None:
            return render_template("forgot_password.html", password=password[0])
        else:
            return redirect(url_for('sign'))
    else:
        return render_template("forgot_password.html")


# Connect to the SQLite database
conn = sqlite3.connect('Sensors.db')

# Create the regions table
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS regions (
  id INTEGER PRIMARY KEY,
  name TEXT
)''')
conn.commit()
 # Create the Time table
conn = sqlite3.connect('Sensors.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Time(
              Zone TEXT,
              timeframe TEXT,
              DateT REAL,
              liters INTEGER,
              duration INTEGER,
              valid INTEGER,
              FOREIGN KEY(Zone) REFERENCES regions(id),
              PRIMARY KEY (Zone, timeframe, DateT, region)
            )''')
conn.commit()

# Create the sensors_data table
c.execute('''CREATE TABLE IF NOT EXISTS sensors_data (
  timestamp INTEGER,
  name TEXT,
  value TEXT,
  region INTEGER,
  FOREIGN KEY(region) REFERENCES regions(id),
  PRIMARY KEY (timestamp, name, region)
)''')
conn.commit()

# Generate random sensor data and insert it into the database

def generate_sensors_data(region_id=3):
    timestamp = "%.1f" %  int(time.time())
    soil_moisture = "%.1f" % random.uniform(0.0, 1.0)
    temperature = "%.1f" % random.uniform(20.0, 30.0)
    humidity = "%.1f" % random.uniform(40.0, 60.0)
    water = "%.1f" % random.uniform(0.0, 1000.0)
    c = conn.cursor()
    c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "soil_moisture", soil_moisture, region_id))
    c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "temperature", temperature, region_id))
    c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "humidity", humidity, region_id))
    c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "water_levels", water, region_id))
    conn.commit()


# Start a separate thread to generate and insert the sensor data every minute
def background_thread():
    while True:
        generate_sensors_data()
        time.sleepO(60)

# Start the background thread on app startup
from threading import Thread
bg_thread = Thread(target=background_thread)
bg_thread.start()


@app.route('/index3/<username>', methods=['POST', 'GET'])
def index3(username):
    # Connect to the SQLite database
    conn = sqlite3.connect('Sensors.db')
    c = conn.cursor()

    # Retrieve the region parameter from the request object
    region = request.args.get('region', default=None, type=int)

    # If a region is selected, generate new sensor data and update the database
    if region is not None:
        timestamp = "%.0f" % int(time.time())
        soil_moisture = "%.1f" % random.uniform(0.0, 100)
        temperature = "%.1f" % random.uniform(20.0, 30.0)
        humidity = "%.1f" % random.uniform(40.0, 60.0)
        water = "%.1f" % random.uniform(0.0, 1000.0)
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "soil_moisture", soil_moisture, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "temperature", temperature, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "humidity", humidity, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "water_levels", water, region))
        conn.commit()

    # Query the sensor data from the database, filtered by region if specified
    if region is not None:
        c.execute("SELECT * FROM sensors_data WHERE region = ? ORDER BY timestamp DESC LIMIT 4", (region,))
    else:
        c.execute("SELECT * FROM sensors_data ORDER BY timestamp DESC LIMIT 4")
    sensor_data = c.fetchall()

    # Query the regions from the database
    c.execute("SELECT * FROM regions")
    regions = c.fetchall()

    # Close the cursor and connection
    c.close()
    conn.close()

    # Render the HTML template with the sensor data, regions, and region param
    return render_template('index3.html', username = username, sensor_data=sensor_data, regions=regions, region=region)


@app.route("/monitor/<username>", methods= ['POST', 'GET'])
def monitor(username):
        # Connect to the SQLite database
    conn = sqlite3.connect('Sensors.db')
    c = conn.cursor()

    # Retrieve the region parameter from the request object
    region = request.args.get('region', default=None, type=int)

    # If a region is selected, generate new sensor data and update the database
    if region is not None:
        timestamp = "%.0f" %  int(time.time())
        soil_moisture = "%.1f" % random.uniform(0.0, 100)
        temperature = "%.1f" % random.uniform(20.0, 30.0)
        humidity = "%.1f" % random.uniform(40.0, 60.0)
        water = "%.1f" % random.uniform(0.0, 1000.0)
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "soil_moisture", soil_moisture, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "temperature", temperature, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "humidity", humidity, region))
        c.execute("INSERT INTO sensors_data VALUES (?, ?, ?, ?)", (timestamp, "water_levels", water, region))
        conn.commit()

    # Query the sensor data from the database, filtered by region if specified
    if region is not None:
        c.execute("SELECT * FROM sensors_data WHERE region = ? ORDER BY timestamp DESC LIMIT 4", (region,))
    else:
        c.execute("SELECT * FROM sensors_data ORDER BY timestamp DESC LIMIT 4")
    sensor_data = c.fetchall()

    # Query the regions from the database
    c.execute("SELECT * FROM regions")
    regions = c.fetchall()

    # Close the cursor and connection
    c.close()
    conn.close()

    # Render the HTML template with the sensor data, regions, and region parameter
    return render_template('monitor.html', username=username, sensor_data=sensor_data, regions=regions, region=region)


@app.route("/Time/<username>", methods=['POST', 'GET'])
def Time(username):
    if request.method == 'POST':
        Zone = request.form['region_id']
        Time = request.form['timeframe']
        date = request.form['DateT']
        level = request.form['liters']
        Duration = request.form['duration']
        Days = request.form['valid']

        conn = sqlite3.connect('Sensors.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Time WHERE Zone = ? AND timeframe = ? AND DateT = ?', (Zone, Time, date))
        user = c.fetchone()

        if user is None:
            c.execute("INSERT INTO Time(Zone, timeframe, DateT, liters, duration , valid) VALUES(?,?,?,?,?,?)",(Zone, Time, date, level, Duration, Days))
            conn.commit()

            return redirect(url_for('TimeData', username = username, row=(Zone, Time, date, level, Duration, Days)))

    return render_template("Time.html", username=username)

@app.route('/TimeData/<row>/<username>')
def TimeData(row, username):
    row = tuple(row.split(','))  # returns data as tuple

    return render_template('TimeData.html', row=row, username=username)

 
if __name__ == "__main__":
    app.run(debug=True)