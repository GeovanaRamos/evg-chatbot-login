# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk import Tracker
from rasa_core.events import SlotSet
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT

from typing import Dict, Text, Any, List, Union, Optional
import pymysql
import re

class UserForm(FormAction):

    def name(self):
        return "user_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name", "password", "email"]

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"name": self.from_entity(entity="name", intent="inform_name"),
                "password": self.from_entity(entity="password", intent="inform_password"),
                "email": self.from_entity(entity="email",intent="inform_email")}

    # @staticmethod
    # def is_match(regex, string):
        
    #     if re.match(regex, string):
    #         return True
    #     else:
    #         return False

    # def validate_name(self,
    #                      value: Text,
    #                      dispatcher: CollectingDispatcher,
    #                      tracker: Tracker,
    #                      domain: Dict[Text, Any]) -> Optional[Text]:
        
    #     #regex = r'^([A-Za-z]+\s[A-Za-z]+)+$'
    #     #a = self.is_match(regex, value)
    #     #print(a, string)

    #     if self.is_match(regex, value):
    #         return value
    #     else:
    #         dispatcher.utter_message('Você não digitou um nome completo')
    #         return None

    # def validate_email(self,
    #                         value: Text,
    #                         dispatcher: CollectingDispatcher,
    #                         tracker: Tracker,
    #                         domain: Dict[Text, Any]) -> Optional[Text]:
    #     """Validate num_people value."""
    #     regex = r'[a-z0-9]+[_\-\.\'a-z0-9]*[a-z0-9]+@\w+\.com\.*\w*'
        
    #     if is_match(regex, value):
    #         return value
    #     else:
    #         dispatcher.utter_message('Você não digitou um email válido')
    #         return None
    
    # def validate_password(self,
    #                         value: Text,
    #                         dispatcher: CollectingDispatcher,
    #                         tracker: Tracker,
    #                         domain: Dict[Text, Any]) -> Optional[Text]:
    #     """Validate num_people value."""
    #     regex = r'^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$'
        
    #     if is_match(regex, value):
    #         return value
    #     else:
    #         dispatcher.utter_message('Você não digitou umaa senha válida')
    #         return None


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
            # results = cursor.fetchall()
            
            # # catch first row
            # person = results[0]
            
            # # catch row data/columns
            # name = person[1]
            # password = person[2]
        except pymysql.Error as exc:
            print("error inserting...\n {}".format(exc))
        finally:
            db.close()

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)

        return []
    
