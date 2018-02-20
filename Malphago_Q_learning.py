'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified :	2018-02-16 16:42
 * Filename :		Malphago_Q_learning.py
 * Description : 
     '''''''''''''''''

from flask import Flask, request, session, render_template, jsonify
from flask.ext.session import Session

app = Flask(__name__)
app.config.from_pyfile('config.py')
Session(app)

import numpy as np
from models.model import mysql, write_db, get_history, get_init_Q


init_state = 9 # init state is the last state
alpha = 0.5
gamma = 0.5
epsilon = 0.2

def init_context():
    init_Q = get_init_Q()
    session['Q_function'] = init_Q
    session['my_choice'] = np.argmax(init_Q[init_state])
    session['curr_state'] = init_state
    session['stats'] = [0,0,0]
    return

def get_context():
    return session['Q_function'], session['my_choice'], session['curr_state'], session['stats']

def get_reward(choice):
    my_choice = session['my_choice']
    if (my_choice == choice): # tie
        r = 0
        session['stats'][1] += 1
    elif ((choice - my_choice) % 3 == 1): # user wins
        r = -1
        session['stats'][0] += 1
    else: # user loses
        r = 1
        session['stats'][2] += 1
    return r


@app.route('/preload', methods=['POST'])
def preload():
    if 'curr_state' not in session:
        init_context()
    wins, ties, losses = session['stats']
    curr_state = session['curr_state']
    my_choice = session['my_choice']
    return jsonify({'wins': wins, 'ties': ties, 'losses': losses, 'state': curr_state, 'my_choice': my_choice})

@app.route('/update_state', methods=['GET', 'POST'])
def update_state():
    if 'curr_state' not in session:
        init_context()
    Q, my_choice, curr_state, _ = get_context()
    # update the Q function
    choice = int(request.form['choice'])
    write_db(request.cookies['session'], choice, my_choice, curr_state)
    r = get_reward(choice)
    next_state = choice + my_choice*3
    update_value = alpha * (r + gamma * max(Q[next_state]) - Q[curr_state][my_choice])
    session['Q_function'][curr_state][my_choice] += update_value
    # return new choice, eplison greedy
    if np.random.rand() < epsilon:
        session['my_choice'] = np.random.randint(3)
    else:
        session['my_choice'] = np.argmax(session['Q_function'][next_state])
    session['curr_state'] = next_state
    print get_context()
    return str(session['my_choice'])

@app.route('/Malphago')
def Malphago():
    n_rows, wins, ties, losses = get_history()
    params = {
            'n_rows': n_rows,
            'wins': wins,
            'ties': ties,
            'losses': losses,
            'win_per': '{:.0%}'.format(1. * wins / n_rows),
            'tie_per': '{:.0%}'.format(1. * ties / n_rows),
            'loss_per': '{:.0%}'.format(1. * losses / n_rows),
        }   
    return render_template('Malphago.html', **params);

@app.route('/DeepMalphago')
def DeepMalphago():
    return render_template('DeepMalphago.html');

@app.route('/')
def index():
    return str(get_init_Q())

if __name__ == '__main__':
    mysql.init_app(app)
    app.run()
