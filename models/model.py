'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified : 2018-02-20 09:41
 * Filename : model.py
 * Description : 
'''''''''''''''''


from flask_mysqldb import MySQL

mysql = MySQL()

def write_db(session_id, user_choice, my_choice, curr_state):
    cur = mysql.connection.cursor()
    cur.execute('''INSERT INTO replay (session_id, user_choice, my_choice, curr_state) VALUES (%s, %s, %s, %s)''', (session_id, user_choice, my_choice, curr_state))
    res = mysql.connection.commit()
    cur.close()
    return 

def get_history():
    n_rows = get_n_rows()[0]
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
    cur = mysql.connection.cursor()
    cur.execute('''select count(*) from replay''')
    res = cur.fetchone()
    cur.close()
    return res

def get_stats():
    cur = mysql.connection.cursor()
    cur.execute('''select (user_choice - my_choice) % 3, count(*) from replay group by (user_choice - my_choice) % 3''')
    res = cur.fetchall()
    cur.close()
    return res


def get_init_Q():
    cur = mysql.connection.cursor()
    cur.execute('''select curr_state, user_choice , count(*) from replay group by curr_state, user_choice''')
    res = cur.fetchall()
    cur.close()
    
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
