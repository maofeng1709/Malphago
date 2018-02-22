'''''''''''''''''
 * Author : FENG Mao 
 * Email : maofeng.fr@gmail.com
 * Last modified : 2018-02-19 16:33
 * Filename : config.py
 * Description : 
     '''''''''''''''''
import os

# general settings
DEBUG = True;

# session config
SECRET_KEY = 'Malphago secret key'
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False

# database
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_TRACK_MODIFICATIONS = False


