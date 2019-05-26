# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk import Tracker
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT, ActionExecutionRejection

from typing import Dict, Text, Any, List, Union, Optional
import pymysql
import re

class UserForm(FormAction):

    def name(self):
        return "user_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name", "email", "password"]

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"name": self.from_text(),
                "email": self.from_text(),
                "password": self.from_text()}
    
    def validate_name(self,
                            value: Text,
                            dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate name value."""

        if value is not None:
            dispatcher.utter_message("Olá, " + value)
            return value
        else:
            dispatcher.utter_message("Erro")
            # validation failed, set slot to None
            return None

    def validate_email(self,
                            value: Text,
                            dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate email value."""

        if value is not None:
            return value
        else:
            dispatcher.utter_message("Erro")
            # validation failed, set slot to None
            return None

    def validate_password(self,
                            value: Text,
                            dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate password value."""

        if value is not None:
            return value
        else:
            dispatcher.utter_message("Erro")
            # validation failed, set slot to None
            return None
    


    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        
        db = pymysql.connect('localhost', 'rasauser', 'rasapassword', 'rasa')
        cursor = db.cursor()

        name = tracker.get_slot('name')
        email = tracker.get_slot('email')
        password = tracker.get_slot('password')

        sql = f" INSERT INTO PERSON VALUES (NULL, '{name}', '{email}', '{password}')" 

        try:
            cursor.execute(sql)
            db.commit()
        except pymysql.Error as exc:
            print("error inserting...\n {}".format(exc))
        finally:
            db.close()

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)

        return []
    
class RetrievePassword(Action):
    def name(self):
        return "action_retrieve_password"

    def run(self, dispatcher, tracker, domain):
        headers = {"Content-Type": "application/json"}
        tracker_state = tracker.current_state()
        message = tracker.latest_message.get('text')

        dispatcher.utter_message(f"Pesquisando senha de {message}.")

        db = pymysql.connect('localhost', 'rasauser', 'rasapassword', 'rasa')
        cursor = db.cursor()

        sql = f" SELECT * FROM PERSON WHERE email =  '{message}'"

        try:
            cursor.execute(sql)
         
            results = cursor.fetchall()
            
            if results:
                # catch first row
                person = results[0]
            
                # catch row data/columns
                name = person[1]
                password = person[3]
                dispatcher.utter_message(f"Olá {name}. Sua senha é: {password}.")
            else:
                dispatcher.utter_message("Desculpe, não encontrei esse email na minha base.")
            
        except pymysql.Error as exc:
            print("error searching...\n {}".format(exc))
        finally:
            db.close()

class ResetForm(Action):
    def name(self):
        return "action_reset_form"

    def run(self, dispatcher, tracker, domain):
        return_slots = []
        for slot in tracker.slots:
                return_slots.append(SlotSet(slot, None))
        return return_slots
            




