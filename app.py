from flask import Flask, g, render_template, request, session, redirect, url_for,flash
from flask_socketio import SocketIO, join_room
import copy
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", password="password", database='chatapp', port=3306)

app = Flask(__name__, template_folder='templates')
app.secret_key = "somesecretkeythatishouldknow"
socketio = SocketIO(app)

users = []


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home page.html")


@app.route('/signup', methods=['GET', 'POST'])
def sign():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        conform = request.form['conform']
        if password == conform:
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO login(fname ,lname , mobile, email, password) VALUES(%s, %s, %s, %s, %s)",
                             (fname, lname, mobile, email, password))
            mydb.commit()
            session['fname'] = fname
            session['lname'] = lname
            session['mobile'] = mobile
            session['email'] = email
            session['password'] = password

            return redirect(url_for('login'))
        else:
            flash('Something went wrong,Try again!')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message=''
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        scursor = mydb.cursor(buffered=True)
        scursor.execute(
            "SELECT  password, email,fname FROM login WHERE email='" + email + "' AND password='" + password + "'")
        data = scursor.fetchone()
        non = copy.copy(data)
        if non is None:
            message='Incorrect username/password'
            return render_template('log.html',message=message)
        else:
            flash('login successful..!!')
            return render_template('x.html')

    return render_template('log.html')
@ app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('c.html', username=username, room=room)
    else:
        return redirect(url_for('home'))


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room{}: {}".format(data['username'], data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)


if __name__ == '__main__':
    socketio.run(app, debug=True)
