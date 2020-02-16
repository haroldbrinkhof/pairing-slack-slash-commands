import os
import re
import dotenv
from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
from psycopg2 import sql

app = Flask(__name__)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']

conn = psycopg2.connect(host='localhost',database=os.environ['DBNAME'],user=os.environ['USERNAME'],password=os.environ['PASSWORD'])
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor);

def performQuery(sqlText, params):
    try:
        cur.execute(sqlText,params)
    except Exception as e:
        print(e)
        conn.rollback()

    else:
        conn.commit()

@app.route("/")
def hello():
    return "<html><head><title>Pairing webservice for slack</title></head><body>Nothing interesting to see here. :-/</body></html>"

@app.route('/perform/pairing', methods=['POST'])
def pairing():
    """ without options passed in 'text' this will return the current list of people available for pairing in this channel
        with options the function will add the user to the list of persons available for pairing (options: yes/on)
        or will remove the user from aforementioned list (options: no/off) """

    if request.form['token'] == verification_token:
        text = "" if 'text' not in request.form else request.form['text']
        channel_name = "" if 'channel_name' not in request.form else request.form['channel_name']
        channel_id = "" if 'channel_id' not in request.form else request.form['channel_id']
        user_name = "" if 'user_name' not in request.form else request.form['user_name']
        user_id = "" if 'user_id' not in request.form else request.form['user_id']
        

        if len(text) == 0:
            # we return a list of the users available for pairing
            performQuery("""SELECT * FROM availability 
                                            WHERE still_available = TRUE AND offered_on = CURRENT_DATE 
                                            AND channel_id = %s""",(channel_id,))
            persons = ''
            rows = cur.fetchall()
            for row in rows:
                persons += '. ' + row['person_name'] + "\n"
            
            if len(rows) == 0:
                persons = '_nobody is available for pairing_ :disappointed:'

            payload = {'type':'mrkdwn','response_type':'ephemeral','text':'Available for pairing in ' + channel_name + "\n" + persons}

        elif text == 'yes' or text == 'on':
            # we mark this person as being available for pairing in this channel
            # set still_available on true again where a conflict has occurrec: UPSERT
            performQuery("""INSERT INTO availability (channel_id,channel_name,person_id,person_name) 
                                    VALUES (%s,%s,%s,%s) 
                                    ON CONFLICT (channel_id, person_id, offered_on) DO UPDATE SET still_available = TRUE""",
                                    (channel_id,channel_name,
                                    user_id, user_name))
            payload = {'response_type':'ephemeral', 'text' : 'You have been registered as available for pairing in ' + channel_name}
        elif text == 'no' or text == 'off':
            # we remove this person of the list of available people to pair with for this channel
            # we don't care to;limit it to the current day since we don't care about previous data here
            performQuery("""UPDATE availability SET still_available = FALSE 
                                    WHERE  channel_id = %s AND person_id = %s""",
                                    (channel_id,user_id))
            payload = {'response_type':'ephemeral', 'text':'You have been unregistered as available for pairing in ' + channel_name}
        else:
            payload = {'response_type': 'ephemeral','text':'unknown option: ' + text + display_name}

    else:
        payload = {'response_type':'ephemeral','text':'token authorization failed'};
        
    return jsonify(payload)


@app.route('/perform/pairing-statistics', methods=['POST'])
def statistics():
    """this function will return statistical data about the pairings this week"""

    payload = {'response_type':'ephemeral','type':'mrkdwn','text':'command not yet implemented.'}
    return jsonify(payload)

@app.route('/perform/pairing-with', methods=['POST'])
def pairingWith():
    """marks a user as being paired with someone else. Purely for statistical purposes."""

    text = "" if 'text' not in request.form else request.form['text']
    channel_name = "" if 'channel_name' not in request.form else request.form['channel_name']
    channel_id = "" if 'channel_id' not in request.form else request.form['channel_id']
    user_name = "" if 'user_name' not in request.form else request.form['user_name']
    user_id = "" if 'user_id' not in request.form else request.form['user_id']

    if 'text' in request.form and len(request.form['text']) > 0:
        pattern = re.compile('^<@[^ ]+>$') # apparantly still follows <@userid|username>  slack api is truly horrible
        if pattern.match(request.form['text']) != None: # make sure that what we got passed was a username
            performQuery("INSERT INTO pairings (person_id, pairs_with) VALUES(%s,%s)",(user_id,text));
            payload = {'response_type':'ephemeral','type':'mrkdwn','text':'you are registered as pairing with' + request.form['text']}
        else:
            payload = {'response_type':'ephemeral','type':'mrkdwn','text':'Unknown command option: ' + request.form['text']}
    else:
        payload = {'response_type':'ephemeral','type':'mrkdwn','text':'command not yet implemented.'}
    return jsonify(payload)

@app.route('/perform/pairing-end', methods=['POST'])
def pairingEnd():
    """marks all current pairings as ended for this user"""

    text = "" if 'text' not in request.form else request.form['text']
    channel_name = "" if 'channel_name' not in request.form else request.form['channel_name']
    channel_id = "" if 'channel_id' not in request.form else request.form['channel_id']
    user_name = "" if 'user_name' not in request.form else request.form['user_name']
    user_id = "" if 'user_id' not in request.form else request.form['user_id']

    performQuery("UPDATE pairings SET ending = now() WHERE person_id = %s AND starting = ending;",(user_id,))
    payload = {'response_type':'ephemeral','type':'mrkdwn','text':'You finished pairing'}
    return jsonify(payload)



if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
    if conn is not None:
        cur.close()
        conn.close()

