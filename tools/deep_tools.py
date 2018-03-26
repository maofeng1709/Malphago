'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified : 2018-03-19 17:35
 * Filename : deep_tools.py
 * Description : 
     '''''''''''''''''



import tensorflow as tf
import collections
from tools.global_vars import comm_vars, deep_vars

input_dim, hidden_dim, output_dim, learning_rate = deep_vars.input_dim, deep_vars.hidden_dim, deep_vars.output_dim, deep_vars.learning_rate

sess = tf.Session()
X = tf.placeholder(tf.float32, shape=[None, input_dim])

def get_tf_variables(params, sess): #get W1 b1 W2 b2 for each Q
    variables = []

    if not params: # first time to initialze params randomly
        for i in range(3):
            W1 = tf.Variable(tf.random_normal([input_dim,hidden_dim]))
            b1 = tf.Variable(tf.random_normal([hidden_dim]))
            W2 = tf.Variable(tf.random_normal([hidden_dim,output_dim]))
            b2 = tf.Variable(tf.random_normal([output_dim]))
            for v in [W1, b1, W2, b2]:
                sess.run(v.initializer)
            variables.append([W1, b1, W2, b2])

    else:
        for param in params:
            W1 = tf.Variable(param['W1'])
            b1 = tf.Variable(param['b1'])
            W2 = tf.Variable(param['W2'])
            b2 = tf.Variable(param['b2'])
            for v in [W1, b1, W2, b2]:
                sess.run(v.initializer)
            variables.append([W1, b1, W2, b2])

    return variables

def update_params_from_variables(params, tf_variables, sess):
    for i, variable in enumerate(tf_variables):
        param = params[i]
        param['W1'] = sess.run(variable[0])
        param['b1'] = sess.run(variable[1])
        param['W2'] = sess.run(variable[2])
        param['b2'] = sess.run(variable[3])

    return

                   
def deep_Q(X, tf_variable):
    W1, b1, W2, b2 = tf_variable
    hidden = tf.tanh(tf.matmul(X, W1) + b1)
    y_pred = tf.sigmoid(tf.matmul(hidden, W2) + b2)
    return y_pred

def get_init_deep_Q(init_Q, X, tf_variables, sess):
    init_deep_Q = [deep_Q(X, tf_variables[0]), deep_Q(X, tf_variables[1]), deep_Q(X, tf_variables[2])] # differnet Q for each option rock, paper sicissors

    data_X = state_to_input(init_Q.keys())
    for i, Q in enumerate(init_deep_Q):
        data_y = [val[i] for key, val in init_Q.iteritems()]
        train_deep_Q(Q, X, data_X, data_y, 1000, sess)

    return init_deep_Q
                        

def train_deep_Q(Q, X, data_X, data_y, n_epochs, sess):
    y = tf.placeholder(tf.float32)
    loss = tf.losses.mean_squared_error(y, Q)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    train = optimizer.minimize(loss)

    for i in range(n_epochs):
        sess.run(train, {X: data_X, y: data_y})

    return 

def state_to_input(states):
    if not isinstance(states, collections.Iterable):
        states = [states]
    n_states = len(states)
    input_data = [[0]*input_dim for i in range(n_states)]
    for i, state in enumerate(states):
        if state == comm_vars.init_state:
            input_data[i][-1] = 1
        else:
            my_choice, user_choice = state / 3, state % 3
            input_data[i][user_choice] = 1
            input_data[i][3 + my_choice] = 1

    return input_data
    
