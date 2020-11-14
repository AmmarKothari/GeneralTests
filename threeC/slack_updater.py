import time
from typing import Any, Dict

import pdb
import slack

ERROR_UPDATE = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": (
            "There was an issue uploading data to the google sheet! :face_with_symbols_on_mouth:"
        ),
    },
}

SUCCESS_UPDATE = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ("Succesfully uploaded data after failed attempt! :white_check_mark:"),
    },
}


class SlackUpdater:
    def __init__(self, token: str):
        self.token = token
        self.slack_web_client = slack.WebClient(self.token)
        # self.channel = "general"
        self.channel = self._get_user_id_from_name("ammar.kothari")
        self.username = "threeclogupdates"
        self.icon_emoji = ":robot_face:"

    def send_error_message(self, error_msg: str = "") -> None:
        # Should probably check if it failed here, but just gonna keep living my life
        response = self.slack_web_client.chat_postMessage(
            **self.get_error_message_payload(error_msg)
        )

    def send_success_message(self) -> None:
        # Should probably check if it failed here, but just gonna keep living my life
        response = self.slack_web_client.chat_postMessage(
            **self.get_success_message_payload()
        )

    def _get_user_id_from_name(self, name: str) -> str:
        response = self.slack_web_client.users_list()
        members = response.data["members"]
        for member in members:
            if member["name"] == name:
                return member["id"]
        raise Exception("No member by that name.")

    def _get_message_payload(self, block: Dict[str:Any]) -> Dict[str, Any]:
        return {
            "ts": time.time(),
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [block],
        }

    def get_error_message_payload(self, error_msg: str) -> Dict[str, Any]:
        message_payload = self._get_message_payload(ERROR_UPDATE)
        if error_msg:
            message_payload["blocks"][0]["text"]["text"] = message_payload["blocks"][0][
                "text"
            ]["text"] + "\n Error message: {}".format(error_msg)
        return message_payload

    def get_success_message_payload(self) -> Dict[str, Any]:
        return self._get_message_payload(SUCCESS_UPDATE)
