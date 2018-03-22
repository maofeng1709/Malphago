'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified : 2018-02-20 09:41
 * Filename : model.py
 * Description : 
'''''''''''''''''


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#class Replay(db.Model):
#    session_id = db.Column(db.String(50))
#    user_choice = db.Column(db.Integer)
#    my_choice = db.Column(db.Integer)
#    reg_date = db.Column(db.DateTime)
#    curr_state = db.Column(db.Integer)
#    replay_id = db.Column(db.Integer, primary_key=True)
#    def __repr__(self):
#        return '<Replay %d>' % self.replay_id


def write_db(session_id, user_choice, my_choice, curr_state, deep = False):
    conn = db.engine.connect()
    table = 'deep_replay' if deep else 'replay' 
    query = '''INSERT INTO %s (session_id, user_choice, my_choice, curr_state) VALUES ('%s', %s, %s, %s)''' % (table, session_id, user_choice, my_choice, curr_state)
    conn.execute(query)
    conn.close()
    return 

def get_history(deep = False):
    n_rows = get_n_rows(deep)
    stats = get_stats(deep)
    wins, ties, losses= 0, 0, 0
    for diff, cnt in stats:
        if diff == 0:
            ties += cnt
        elif diff in [-2, 1]:
            losses += cnt
        else:
            wins += cnt
    return n_rows, wins, ties, losses

def get_n_rows(deep = False):
    conn = db.engine.connect()
    table = 'deep_replay' if deep else 'replay'
    query = '''select count(*) from %s''' % table
    res = conn.execute(query)
    conn.close()
    return res.fetchone()[0]

def get_stats(deep = False):
    conn = db.engine.connect()
    table = 'deep_replay' if deep else 'replay'
    query = 'select (user_choice - my_choice) %% 3, count(*) from ' + table + ' group by (user_choice - my_choice) %% 3'
    res = conn.execute(query)
    conn.close()
    return res.fetchall()


def get_init_deep_Q():
    return deep_Q

def deep_Q():
    return 1

def get_init_Q():
    conn = db.engine.connect()
    res = conn.execute('''select curr_state, user_choice , count(*) from replay group by curr_state, user_choice''').fetchall()
    conn.close()
    
    init_Q = {i: [0,0,0] for i in range(10)}
    
    for state, choice, cnt in res:
        init_Q[state][choice] = cnt
    
    for state in init_Q:
        vec = init_Q[state]
        s = float(sum(vec))
        if s < 10:
            init_Q[state] = [0,0,0]
        else:
            new_vec = [ (vec[(i-1)%3] - vec[(i+1)%3]) / s  for i in range(3)]
            init_Q[state] = new_vec
    return init_Q


