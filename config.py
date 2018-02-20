'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified : 2018-02-19 16:33
 * Filename : config.py
 * Description : 
'''''''''''''''''

# general settings
DEBUG = True;

# session config
SECRET_KEY = 'Malphago secret key'
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False

# database
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_PORT = 3306
MYSQL_DB = 'Malphago'
