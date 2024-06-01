from aiogram import types
from aiogram.types import Message

from bot_lib import Handler, HandlerDisplayMode
from calmmage_feature_bot.app import ShowcaseApp


class ShowcaseHandler(Handler):
    name = "showcase"
    display_mode = HandlerDisplayMode.FULL
    has_chat_handler = True
    commands = {
        "start_handler": "start",
        "help_handler": "help",
        "showcase_handler": "showcase",
        "showcase_whisper_handler": "showcase_whisper",
        "showcase_dummy_handler": "showcase_dummy",
    }

    def __init__(self, config=None):
        super().__init__(config)
        self._handlers = None

    @property
    def handlers(self):
        if self._handlers is None:
            self._handlers = {
                command: getattr(self, func_name)
                for func_name, command in self.commands.items()
            }
        return self._handlers

    """
    /start  
        “Hello” + info (get_info)
    /help
        Info (get_info)
    /showcase … (str) → fancy embed search
    /showcase_whisper -> run the corresponding command
    … other /shocase_... commands
    /describe … (str) → fancy embed search
     → (like a help-command - listing all the commands)
    
    
    /describe_…
    generate automatically based on FeatureDescriptions list
    """

    # region basic handlers - info and help
    async def start_handler(self, message, app: ShowcaseApp):
        response_text = app.get_start_message()
        await self.reply_safe(response_text, message)

    async def help_handler(self, message, app: ShowcaseApp):
        response_text = app.get_help_message()
        await self.reply_safe(response_text, message)

    async def chat_handler(self, message: Message, app: ShowcaseApp):
        """
        Handle messages in the chat
        """
        # idea 1: send "info" with the list of all features
        # todo: add a middleware that counts how many messages ago was the ... last info message
        help_triggered = None
        if True:
            await self.help_handler(message, app)
            help_triggered = True

        if False:
            # text = self.get_message_text(message)
            # if help_triggered:
            #     text += "\n\n[System] Help message was sent to the user"
            await self.showcase_gpt_chat_handler(message, app)

        # idea 2: chat with gpt - regularly

        # how to decide?
        # option 1: if text is gibberish - send info (remind how to use the bot)
        # option 2: If the last message was a long time ago - send info
        # option 3: If the last message was a chat - always continue chatting
        #  But what if user asks for help in the chat? - detect somehow and send help
        #  Hack: Do both! Chat and help
        # raise NotImplementedError("Not implemented yet")

    # endregion

    # region Core - showcase handlers & demo
    async def showcase_handler(self, message, app: ShowcaseApp):
        message_text = await self.get_message_text(message)
        message_text = self.strip_command(message_text)
        # if showcase command has no input - show a list of all commands for all features
        # if showcase command has input - do a fuzzy search for the feature and then run corresponding command

        if not message_text:
            message_text = app.get_info_message()
            await self.reply_safe(message_text, message)
        else:
            feature_desc = app.get_feature(message_text)
            # call the command for the feature
            command = feature_desc.command.lstrip("/")
            await self.handlers[command](message, app)

    async def showcase_dummy_handler(self, message: Message, app: ShowcaseApp):
        # run the corresponding command for the dummy feature
        await self.func_handler(app.dummy_feature, message)

    async def describe_handler(self, message, app: ShowcaseApp):
        message_text = await self.get_message_text(message)
        message_text = self.strip_command(message_text)
        # if showcase command has no input - show a list of all commands for all features
        # if showcase command has input - do a fuzzy search for the feature and then run corresponding command

        if not message_text:
            message_text = (
                "Use '/describe <feature>' to get more information about the feature"
            )
            message_text += "\nAvailable features:\n"
            for feature in app.features:
                description_first_line = feature.description.strip().split("\n")[0]
                message_text += f"{feature.name}: {description_first_line}\n"
            await self.reply_safe(message_text, message)
        else:
            feature_key = app.find_feature(message_text)
            message_text = app.describe_feature(feature_key)
            await self.reply_safe(message_text, message)

    # todo: describe_dummy etc.. ?

    # endregion

    # ----------------------------------------

    # region Feature 1 - Whisper
    async def showcase_whisper_handler(self, message, app: ShowcaseApp):
        # run the corresponding command for the whisper feature
        pass

    # endregion

    # region Feature 2 - Chat with GPT (via openai API)

    async def showcase_gpt_chat_handler(self, message: Message, app: App):
        """
        Chat with GPT
        """
        raise NotImplementedError("Not implemented yet")

    # endregion

    # region Feature 3 - Chat with GPT via Langchain plugin

    # endregion

    async def view_timezone_handler(self, message: Message, app: ShowcaseApp):
        """Dummy handler to view the user's timezone"""
        user_id = message.from_user.id
        timezone = app.get_user_timezone(user_id)
        await self.reply_safe(f"Your timezone is {timezone}", message)

    # todo: catch "missing timezone data" error
    #  globally via aiogram middlewares or something
    #  and ask user to provide timezone
    # todo:
    async def handle_timzeone_error(self, message: Message, app: App):
        # todo: add transparency - error and which function caused it
        reason = "You have not provided your timezone yet. Please provide it"
        await self._request_location(message, app, reason)

    # todo: save location to the ... user database
    # todo: register this ... on the startup initialization
    # @dp.message_handler(content_types=["location"])
    async def handle_location(self, message: types.Message):
        lat = message.location.latitude
        lon = message.location.longitude
        reply = "latitude:  {}\nlongitude: {}".format(lat, lon)
        await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())

    @staticmethod
    def _get_share_location_keyboard():
        button = types.KeyboardButton(text="Share Location", request_location=True)
        keyboard = types.ReplyKeyboardMarkup(keyboard=[[button]])
        return keyboard

    # todo: add a timeout for the location request
    # todo: allow user to 1) give current time 2) set timezone 3) set location
    async def _request_location(self, message: types.Message, app: App, reason=None):
        reply = "Click on the the button below to share your location"
        await message.answer(reply, reply_markup=self._get_share_location_keyboard())

    # region new features - 1 Jun 2024

    # endregion new features - 1 Jun 2024
