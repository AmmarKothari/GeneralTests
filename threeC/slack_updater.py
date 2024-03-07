import time
from typing import Any, Dict
import copy

import slack


STATUS_UPDATE = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": (),
    },
}

ERROR_UPDATE = copy.deepcopy(STATUS_UPDATE)
ERROR_UPDATE["text"][
    "text"
] = "There was an issue uploading data to the google sheet! :face_with_symbols_on_mouth:"

SUCCESS_UPDATE = copy.deepcopy(STATUS_UPDATE)
SUCCESS_UPDATE["text"][
    "text"
] = "Succesfully uploaded data after failed attempt! :white_check_mark:"


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

    def send_status_message(self, message) -> None:
        response = self.slack_web_client.chat_postMessage(
            **self.get_status_message_payload(message)
        )

    def _get_user_id_from_name(self, name: str) -> str:
        response = self.slack_web_client.users_list()
        members = response.data["members"]
        for member in members:
            if member["name"] == name:
                return member["id"]
        raise Exception("No member by that name.")

    def _get_message_payload(self, block: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ts": time.time(),
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [block],
        }

    def get_error_message_payload(self, error_msg: str) -> Dict[str, Any]:
        error_payload = copy.deepcopy(ERROR_UPDATE)
        if error_msg:
            error_payload["text"]["text"] = (
                error_payload["text"]["text"] + f"\n Error message: {error_msg}"
            )
        return self._get_message_payload(error_payload)

    def get_success_message_payload(self) -> Dict[str, Any]:
        return self._get_message_payload(SUCCESS_UPDATE)

    def get_status_message_payload(self, msg) -> Dict[str, Any]:
        status_payload = copy.deepcopy(STATUS_UPDATE)
        status_payload["text"]["text"] = msg
        return self._get_message_payload(status_payload)
