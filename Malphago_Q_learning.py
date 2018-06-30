'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified :	2018-02-16 16:42
 * Filename :		Malphago_Q_learning.py
 * Description : 
     '''''''''''''''''

from flask import Flask, request, session, render_template, jsonify
from flask_session import Session
from time import time


app = Flask(__name__)
app.config.from_pyfile('config.py')
Session(app)

import numpy as np
import tensorflow as tf
from models.model import db, write_db, get_history, get_init_Q

db.init_app(app)

from tools.global_vars import comm_vars, deep_vars
from tools.deep_tools import state_to_input, deep_Q, get_init_deep_Q, train_deep_Q, get_tf_variables, update_params_from_variables


def init_context():
    init_Q = get_init_Q()
    session['Q_function'] = init_Q
    session['curr_state'] = comm_vars.init_state
    session['my_choice'] = np.argmax(init_Q[comm_vars.init_state])
    session['stats'] = [0,0,0]
    return

def init_deep_context():
    graph = tf.Graph()
    with graph.as_default():
        with tf.Session() as sess:
            X = tf.placeholder(tf.float32, shape=(None,deep_vars.input_dim))
            tf_variables = get_tf_variables([],sess)
            deep_Qs = get_init_deep_Q(get_init_Q(), X, tf_variables, sess)
            session['deep_params'] = [{}, {}, {}]
            update_params_from_variables(session['deep_params'], tf_variables, sess)
            session['curr_deep_state'] = comm_vars.init_state
            session['my_deep_choice'] = np.argmax(sess.run(deep_Qs, {X: state_to_input(comm_vars.init_state)}))
            session['deep_stats'] = [0,0,0]
            session['replay_memory'] = []
    tf.reset_default_graph()
    return

def get_context():
    return session['Q_function'], int(session['my_choice']), int(session['curr_state'])

def get_deep_context():
    return int(session['my_deep_choice']), int(session['curr_deep_state'])

def get_reward(choice, deep=False):
    my_choice = session['my_deep_choice'] if deep else session['my_choice']
    stats = session['deep_stats'] if deep else session['stats'] 
    if (my_choice == choice): # tie
        r = 0
        stats[1] += 1
    elif ((choice - my_choice) % 3 == 1): # user wins
        r = -1
        stats[0] += 1
    else: # user loses
        r = 1
        stats[2] += 1
    return r


@app.route('/preload', methods=['POST'])
def preload():
    if int(request.form['deep']):
        if 'curr_deep_state' not in session:
            init_deep_context()
        wins, ties, losses = session['deep_stats']
        return jsonify({'wins': wins, 'ties': ties, 'losses': losses, 'state': session['curr_deep_state'], 'my_choice': session['my_deep_choice']})
    else:
        if 'curr_state' not in session:
            init_context()
        wins, ties, losses = session['stats']
        return jsonify({'wins': wins, 'ties': ties, 'losses': losses, 'state': session['curr_state'], 'my_choice': session['my_choice']})

@app.route('/restart', methods=['POST'])
def restart():
    if int(request.form['deep']):
        init_deep_context()
    else:
        init_context()
    return 'restarted'

@app.route('/update_state', methods=['GET', 'POST'])
def update_state():
    Q, my_choice, curr_state = get_context()
    # update the Q function
    choice = int(request.form['choice'])
    write_db(request.cookies['session'], choice, my_choice, curr_state)
    r = get_reward(choice)
    next_state = choice + my_choice*3
    update_value = comm_vars.alpha * (r + comm_vars.gamma * max(Q[next_state]) - Q[curr_state][my_choice])
    session['Q_function'][curr_state][my_choice] += update_value
    # return new choice, eplison greedy
    if np.random.rand() < comm_vars.epsilon:
        session['my_choice'] = np.random.randint(3)
    else:
        session['my_choice'] = np.argmax(session['Q_function'][next_state])
    session['curr_state'] = next_state
    print get_context()
    return str(session['my_choice'])

@app.route('/update_deep_state', methods=['GET', 'POST'])
def update_deep_state():
    graph = tf.Graph()
    with graph.as_default():
         with tf.Session() as sess:
            # prepare tf model for current user
            X = tf.placeholder(tf.float32, shape=(None,deep_vars.input_dim))
            tf_variables = get_tf_variables(session['deep_params'],sess)
            deep_Qs = [deep_Q(X, tf_variables[0]), deep_Q(X,tf_variables[1]), deep_Q(X, tf_variables[2])]
            # observe the user choice and get reward
            choice = int(request.form['choice'])
            my_choice, curr_state = get_deep_context()
            write_db(request.cookies['session'], choice, my_choice, curr_state, deep=True)
            r = get_reward(choice, deep=True)
            next_state = choice + my_choice*3
            session['replay_memory'].append([curr_state, my_choice, r, next_state])

            Q_vals = sess.run(deep_Qs, {X: state_to_input(next_state)})

            # update the Q function parameters
            # prepare the train data, we take into consider only the last batch_size replays
            # because we suppose that user's next choice depends on his preivous plays  
            batch_size = min(deep_vars.batch_size, len(session['replay_memory']))
            for i in range(batch_size):
                replay = session['replay_memory'][-1-i]
                data_X = state_to_input(replay[0])
                # target value of y = r(curr_state) + gamma*max(Q(next_state)_rock/paper/scissors)
                data_y = replay[2] + comm_vars.gamma * max(sess.run(deep_Qs, {X: state_to_input(replay[3])}))
                train_deep_Q(deep_Qs[replay[1]], X, data_X, data_y, 20, sess)
            update_params_from_variables(session['deep_params'], tf_variables, sess)
            # return new choice, eplison greedy
            if np.random.rand() < comm_vars.epsilon:
                session['my_deep_choice'] = np.random.randint(3)
            else:
                session['my_deep_choice'] = np.argmax(Q_vals)
            session['curr_deep_state'] = next_state
            print Q_vals, choice, my_choice, curr_state
    tf.reset_default_graph()
    return str(session['my_deep_choice'])


@app.route('/Malphago')
def Malphago():
    params = get_init_page_params()
    return render_template('Malphago.html', **params);

@app.route('/DeepMalphago')
def DeepMalphago():
    params = get_init_page_params(deep=1)
    return render_template('DeepMalphago.html', **params);

def get_init_page_params(deep = False):
    n_rows, wins, ties, losses = get_history(deep)
    n_rows = max(1, n_rows)
    params = {
            'n_rows': n_rows,
            'wins': wins,
            'ties': ties,
            'losses': losses,
            'win_per': '{:.0%}'.format(1. * wins / n_rows),
            'tie_per': '{:.0%}'.format(1. * ties / n_rows),
            'loss_per': '{:.0%}'.format(1. * losses / n_rows),
        }   
    return params


@app.route('/')
def index():
    return Malphago()
if __name__ == '__main__':
    app.run()
