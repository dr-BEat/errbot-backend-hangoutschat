# errbot-backend-hangoutschat

*This is a Google Hangouts Chat backend for [Errbot](http://errbot.io/).*

Current State
-----

This is a work in progress, so probably not really useful for production.

TODOs:
- [x] 1 to 1 Chat
- [ ] Enable reply on same thread in a room
- [ ] Actually investigate and enable Errbot room functionality
- [ ] Code cleanup

Setup
-----

1. [Install errbot](http://errbot.io/en/latest/user_guide/setup.html)
   and follow to instructions to setup a `config.py`.

2. Clone this repository somewhere convenient.

3. Install the requirements listed in `requirements.txt`.

4. In Google Hangouts Chat, create a bot that will represent ErrBot. If you need help with this step,
   check out [this](https://developers.google.com/hangouts/chat/how-tos/pub-sub) guide on Hangouts Chat bots based on Google Cloud Pub/Sub.

5. Edit your ErrBot's `config.py`. Use the following template for a minimal configuration:

   ```python
   import logging

   BACKEND = 'Hangoutschat'

   BOT_EXTRA_BACKEND_DIR = r'<path/to/errbot-backend-hangoutschat>'
   BOT_DATA_DIR = r'<path/to/your/errbot/data/directory>'
   BOT_EXTRA_PLUGIN_DIR = r'<path/to/your/errbot/plugin/directory>'

   BOT_LOG_FILE = r'<path/to/your/errbot/logfile.log>'
   BOT_LOG_LEVEL = logging.INFO

   BOT_IDENTITY = {  # Fill this with the corresponding values in your bot's `.zuliprc`
      'project_id': '<projectid>',
      'subscription_name': '<subscriptionname>',
      'credentials_path': '<path/to/your/googleserviceaccount.json>'
   }

   BOT_ADMINS = ('<your@email.address>',)
   CHATROOM_PRESENCE = ()
   ```

   Sections you need to edit are marked with `<>`.

6. [Start ErrBot](http://errbot.io/en/latest/user_guide/setup.html#starting-the-daemon).
