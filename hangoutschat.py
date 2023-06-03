import logging
from time import sleep
from errbot.backends.base import RoomError, Identifier, Person, RoomOccupant, Stream, ONLINE, Room
from errbot.core import ErrBot


from google.cloud import pubsub_v1
import json
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build, build_from_document
import sys

from markdownconverter import hangoutschat_markdown_converter

# Can't use __name__ because of Yapsy
log = logging.getLogger('errbot.backends.hangoutschat')

class HangoutsChatIdentifier(Identifier):
    def __init__(self, id):
        self._id = str(id)

    @property
    def id(self):
        return self._id

    def __unicode__(self):
        return str(self._id)

    def __eq__(self, other):
        return self._id == other.id

    __str__ = __unicode__


# `HangoutsChatPerson` is used for both 1-1 PMs and Group PMs.
class HangoutsChatPerson(HangoutsChatIdentifier, Person):
    def __init__(self, id, full_name, email,space_name):
        super().__init__(id)
        self._full_name = full_name
        self._email = email
        self._space_name = space_name

    @property
    def person(self):
        return self._id

    @property
    def fullname(self):
        return self._full_name

    @property
    def nick(self):
        return None

    @property
    def email(self):
        return self._email

    @property
    def client(self):
        return 'Hangouts Chat'

    @property
    def aclattr(self):
        return self._email

    @property
    def spacename(self):
        return self._space_name


class HangoutsChatBackend(ErrBot):
    running = True

    def __init__(self, config):
        super().__init__(config)

        self.bot_identifier = HangoutsChatPerson(id='botty',
                full_name='Botty McBotface',
                email='botty', space_name='')

        self.identity = config.BOT_IDENTITY
        for key in ('project_id', 'subscription_name', 'credentials_path'):
            if key not in self.identity:
                log.fatal(
                    "You need to supply the key `{}` for me to use.".format(key)
                )
                sys.exit(1)

        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(self.identity['project_id'], self.identity['subscription_name'])

        self.md = hangoutschat_markdown_converter()

    def serve_forever(self):
        self.connect()  # be sure we are "connected" before the first command
        self.connect_callback()  # notify that the connection occured
        try:
            while self.running:
                log.info("Alive!")
                sleep(10)

        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            log.debug("Trigger disconnect callback")
            self.disconnect_callback()
            log.debug("Trigger shutdown")
            self.shutdown()

    def connect(self):
        def callback(message):
            try:
                self.handle_message(message)
            except:
                e = sys.exc_info()
                log.info("Error: {}".format(e))
        log.info('Connecting')
        self.subscription = self.subscriber.subscribe(self.subscription_path, callback=callback)
        log.info('Listening for messages on {}'.format(self.subscription_path))

    def handle_message(self, message):
        print('Received message: ')
        log.info('Received message: {}'.format(message.data))

        event_data = json.loads(message.data)
        space_name = event_data['space']['name']
        text = event_data['message']['text']

        # If the bot was added or removed, we don't need to return a response.
        if event_data['type'] == 'ADDED_TO_SPACE':
            log.info('Bot added to space {}'.format(space_name))
            message.ack()
            return
        if event_data['type'] == 'REMOVED_FROM_SPACE':
            log.info('Bot removed rom space {}'.format(space_name))
            message.ack()
            return
        
        # Check if the space type is ROOM
        if event_data['space']['type'] == 'ROOM':
            # Remove @ mentions from the text
            text = ' '.join(word for word in text.split() if not word.startswith('@'))

        # message_instance = self.build_message(event_data['message']['text'])
        message_instance = self.build_message(text)

        sender = event_data['message']['sender']
        message_instance.to = self.bot_identifier
        message_instance.frm = HangoutsChatPerson(
                id=sender['name'],
                full_name=sender['displayName'],
                email=sender['email'],
                space_name=space_name)

        log.info("Mesage: {} {}!".format(event_data['message']['text'], message_instance));
        self.callback_message(message_instance)
        message.ack()

    def send_message(self, msg):
        super().send_message(msg)
        log.info("Send: {}, {}!".format(msg, msg.to))
        """Sends a response back to the Hangouts Chat room using the asynchronous API.

        Args:
          response: the response payload
          space_name: The URL of the Hangouts Chat room

        """
        response = { 'text': self.md.convert(msg.body) }

        scopes = ['https://www.googleapis.com/auth/chat.bot']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.identity['credentials_path'], scopes)
        http_auth = credentials.authorize(Http())

        chat = build('chat', 'v1', http=http_auth)
        chat.spaces().messages().create(
            parent=msg.to.spacename,
            body=response).execute()

    def build_identifier(self, strrep):
        return HangoutsChatPerson(strrep)

    def shutdown(self):
        if self.running:
            self.running = False
            super().shutdown()  # only once (hackish)

    def change_presence(self, status: str = ONLINE, message: str = ''):
        log.info("prefix_groupchat_reply: {}!".format((status, message)))

    def build_reply(self, msg, text=None, private=False, threaded=False):
        log.info("build_reply: {}!".format((msg, text, private, threaded, msg.to.fullname, msg.frm.fullname)))
        response = self.build_message(text)
        response.frm = msg.to
        response.to = msg.frm
        return response

    def prefix_groupchat_reply(self, message, identifier):
        log.info("prefix_groupchat_reply: {}!".format((message, identifier)))

    def query_room(self, room):
        log.info("query_room: {}!".format((room)))

    def rooms(self):
        log.info("rooms:!")

    @property
    def mode(self):
        return 'null'
