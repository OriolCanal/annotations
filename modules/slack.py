from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_slack(message: str):
    client = WebClient(token="xoxb-5028238476320-5001657632341-yddZjBNRkBEZkoKp0I6dLSHh")

    try:
        response = client.chat_postMessage(
            channel="#annotations",
            text=message
        )
        print("message sent: ", response["ts"])
        return (0)

    except SlackApiError as e:
        print("Error sending message: {}".format(e))
        return (1)
