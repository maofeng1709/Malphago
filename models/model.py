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


def write_db(session_id, user_choice, my_choice, curr_state):
    conn = db.engine.connect()
    conn.execute('''INSERT INTO replay (session_id, user_choice, my_choice, curr_state) VALUES (%s, %s, %s, %s)''', (session_id, user_choice, my_choice, curr_state))
    conn.close()
    return 

def get_history():
    n_rows = get_n_rows()
    stats = get_stats()
    wins, ties, losses= 0, 0, 0
    for diff, cnt in stats:
        if diff == 0:
            ties += cnt
        elif diff in [-2, 1]:
            losses += cnt
        else:
            wins += cnt
    return n_rows, wins, ties, losses

def get_n_rows():
    conn = db.engine.connect()
    res = conn.execute('''select count(*) from replay''')
    conn.close()
    return res.fetchone()[0]

def get_stats():
    conn = db.engine.connect()
    res = conn.execute('''select (user_choice - my_choice) %% 3, count(*) from replay group by (user_choice - my_choice) %% 3''')
    conn.close()
    return res.fetchall()


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
