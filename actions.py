from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from textinput import SampleTextAssistant
from difflib import SequenceMatcher

import os
import venmo
import json
import requests
import collections
import pickle
import datetime

from Spotify import SpotifyAgent
from Google import GoogleAssistant

# contact map
people = {
    'Ryan Ma': 6266230819,
    'Ryan Lieu': 2068835878,
}

conversation_history = collections.deque([], maxlen=3)
google_assistant = GoogleAssistant()
spotify = SpotifyAgent()

# venmo helper functions
def execute_venmo_request(phone_number, amount):
    request_body = 'venmo charge {} {} "you deserve it"'.format(phone_number, amount)
    os.system(request_body)

def execute_venmo_pay(phone_number, amount):
    payment_body = 'venmo pay {} {} "you deserve it"'.format(phone_number, amount)
    os.system(payment_body)

# ACTION CLASSES 
class ActionVenmoRequest(Action):
    
    def name(self) -> Text:
        return "action_venmo_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            # gather data
            person_name = tracker.get_slot("person")
            dollar_amount = tracker.get_slot("dollar_amount")
            msg = "REQUEST PERSON: " + person_name + ", DOLLAR_AMOUNT: " + dollar_amount
            
            # check to see if person exists
            if person_name not in people:
                dispatcher.utter_message("Sorry, I'm not sure who this is :/")
        
            # execute request
            execute_venmo_request(people[person_name], dollar_amount)
            dispatcher.utter_message(msg)


class ActionVenmoPay(Action):

    def name(self) -> Text:
        return "action_venmo_pay"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            # gather data
            person_name = tracker.get_slot("person")
            dollar_amount = tracker.get_slot("dollar_amount")
            msg = "PAY PERSON: " + person_name + ", DOLLAR_AMOUNT: " + dollar_amount

            # check to see if person exists
            if person_name not in people:
                dispatcher.utter_message("Sorry, I'm not sure who this is :/")

            # execute payment
            execute_venmo_pay(people[person_name], dollar_amount)
            dispatcher.utter_message(msg)


class ActionOpenGoogleChannel(Action):

    def name(self) -> Text:
        return "action_ask_google"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = tracker.get_slot("query")
        response = google_assistant.ask_assistant_query(query)
        dispatcher.utter_message(response)


class ActionConversation(Action):

    def name(self) -> Text:
        return "action_conversation"
    
    def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        # update conversation history
        conversation_history.append(tracker.latest_message['text'])

        print("TRACKER EVENTS HERE: ", tracker.events)

        # conversation model api request
        url = "http://localhost:8080/" + "cakechat_api/v1/actions/get_response"
        r = requests.post(url, json={'context': list(conversation_history), 'emotion': 'anger'})

        # return conversation model response
        conversation_resp = r.text.split(":")[1][1:-3]

        conversation_history.append(conversation_resp)
        print("CONVERSATION HISTORY: ", conversation_history)

        dispatcher.utter_message(conversation_resp)


class ActionUpdateYourself(Action):

    def name(self) -> Text:
        return "action_update_yourself"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("SELF UPDATES TRIGGERED")
        # os.system("cd ~")
        # os.system("cd /Users/Vaibhav/Documents/SideProjects/friday")
        # os.system("git pull")

        os.system("rasa train")


class ActionPauseSpotify(Action):

    def name(self) -> Text:
        return "action_pause_spotify"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spotify.pause()


class ActionPlaySpotify(Action):

    def name(self) -> Text:
        return "action_play_spotify"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spotify.play()

class ActionPlayPlaylistSpotify(Action):

    def name(self) -> Text:
        return "action_play_playlist_spotify"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        playlist_name = tracker.get_slot("music_thing")
        played = spotify.play_playlist(playlist_name)

        if not played:
            msg = "I couldn't find the playlist you gave me...try again?"
            dispatcher.utter_message(msg)


class ActionPlayArtistSpotify(Action):

    def name(self) -> Text:
        return "action_play_artist_spotify"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            artist = tracker.get_slot("artist")
            played = spotify.play_artist(artist)

            if not played:
                msg = "I couldn't find the artist you wanted :/"
                dispatcher.utter_message(msg)

class ActionRecordSpotifySession(Action):

    def name(self) -> Text:
        return "action_record_spotify_session"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            msg = "Got it. Recording tonight's session"
            spotify.record_spotify_session()

            # thread should be adding songs to a playlist until thread is killed

            dispatcher.utter_message(msg)

class ActionStopRecordingSpotifySession(Action):
    
    def name(self) -> Text:
        return "action_stop_recording_spotify_session"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            msg = "Got it. Stopping tonight's Spotify session"
            dispatcher.utter_message(msg)
            spotify.stop_recording_spotify_session()
