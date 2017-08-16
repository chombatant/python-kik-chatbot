import os 
import sys
import json

from flask import Flask, request, Response
import requests

from datetime import datetime

# http://patorjk.com/software/taag/#p=display&f=Banner&t=Connecting
# ===========================================================================================

page_access_token = os.environ['FACEBOOK_PAGE_ACCESS_TOKEN']
verify_token      = os.environ['FACEBOOK_VERIFY_TOKEN']

app = Flask(__name__)

# ===========================================================================================

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == verify_token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    if False: # Explore the data at hand...
                        (w1, w2) = (12, 36)
                        print " {:{w1}}| {:{w1}}| {:{w2}}| {:{w1}}".format(
                            "Key", "Subkey", "Value", "Type", w1=w1, w2=w2)
                        for key in messaging_event.keys():
                            if type(messaging_event[key]).__name__ != "dict":
                                print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                    key, 
                                    "", 
                                    messaging_event[key], 
                                    type(messaging_event[key]).__name__, 
                                    w1=w1, 
                                    w2=w2)
                            else:
                                for subkey in messaging_event[key].keys():
                                    print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                        key,
                                        subkey,
                                        messaging_event[key][subkey],
                                        type(messaging_event[key][subkey]).__name__,
                                        w1=w1,
                                        w2=w2)
                        user_information = get_user_information( messaging_event["sender"]["id"])
                        for key in user_information.keys():
                            print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                "user", 
                                key, 
                                user_information[key], 
                                type(user_information[key]).__name__, 
                                w1=w1, 
                                w2=w2)                            

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    timestamp = messaging_event["timestamp"]

                    user = get_user_information( sender_id)

                    timezone_offset = user["timezone"]
                    utc_hour = datetime.utcfromtimestamp( timestamp).hour
                    answer = "Your current time is... " + str(utc_hour + timezone_offset)

                    send_message(sender_id, answer)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return Response(status=200)



def send_message(recipient_id, message_text):

    print "Sending message..."

    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


@app.route('/', methods=['GET'])
def get_user_information( recipient_id):
    query_string = ('https://graph.facebook.com/v2.6/' 
        + recipient_id
        + "?fields=first_name,last_name,profile_pic,locale,timezone,gender"
        + "&access_token="
        + page_access_token) 
    return json.loads( requests.get( query_string).content)

# ===========================================================================================


 #     #                       #                                                               
 ##   ##   ##   # #    #      # #   #####  #####  #      #  ####    ##   ##### #  ####  #    # 
 # # # #  #  #  # ##   #     #   #  #    # #    # #      # #    #  #  #    #   # #    # ##   # 
 #  #  # #    # # # #  #    #     # #    # #    # #      # #      #    #   #   # #    # # #  # 
 #     # ###### # #  # #    ####### #####  #####  #      # #      ######   #   # #    # #  # # 
 #     # #    # # #   ##    #     # #      #      #      # #    # #    #   #   # #    # #   ## 
 #     # #    # # #    #    #     # #      #      ###### #  ####  #    #   #   #  ####  #    #                                                                                             

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print "Starting the app..." 
    port = int( os.environ.get('PORT', 5000))
    app.run( host='0.0.0.0', port=port)
