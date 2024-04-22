from typing import Any, Text, Dict, List, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import pytz
from app import app, UserLocation
from flask_login import current_user
from timezonefinder import TimezoneFinder

class ActionFetchTime(Action):
    def name(self) -> Text:
        return "get_date_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user = current_user
        if user and hasattr(user, 'user_id'):
            latitude, longitude = self.get_user_location(user)
            if latitude is not None and longitude is not None:
                time = self.fetch_local_time(latitude, longitude)
                dispatcher.utter_message(f"The current time is: {time}")
            else:
                dispatcher.utter_message("User location not found.")
        else:
            dispatcher.utter_message("User not authenticated.")
        return []

    def get_user_location(self, user: Any) -> Tuple[float, float]:
        if user and hasattr(user, 'id'):
            user_location = UserLocation.query.filter_by(user=user.id).first()
            if user_location:
                return user_location.latitude, user_location.longitude
        return None, None

    def fetch_local_time(self, latitude: float, longitude: float) -> str:
        utc_time = datetime.now(pytz.utc)
        time_zone = self.get_time_zone(latitude, longitude)
        local_time = utc_time.astimezone(pytz.timezone(time_zone))
        formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S %Z")

        return formatted_time

    def get_time_zone(self, latitude: float, longitude: float) -> str:
        tf = TimezoneFinder()
        time_zone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if time_zone_str:
            return time_zone_str
        else:
            return "UTC"
