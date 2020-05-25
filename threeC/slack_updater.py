import time
import slack

ERROR_UPDATE = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ("There was an issue uploading data to the google sheet! :face_with_symbols_on_mouth:")
    }
}


class SlackUpdater:
    def __init__(self, token):
        self.token = token
        self.channel = "general"
        self.username = "threeclogupdates"
        self.icon_emoji = ":robot_face:"
        self.slack_web_client = slack.WebClient(self.token)

    def send_error_message(self):
        # Should probably check if it failed here, but just gonna keep living my life
        response = self.slack_web_client.chat_postMessage(**self.get_error_message_payload())


    def get_error_message_payload(self):
        return {
            "ts": time.time(),
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                ERROR_UPDATE
            ],
        }
