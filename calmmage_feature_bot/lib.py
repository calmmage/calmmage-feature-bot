from typing import List
from dataclasses import dataclass
from bot_lib import App, Handler, HandlerDisplayMode
from calmlib.utils.common import is_subsequence
from textwrap import dedent
from aiogram.types import Message


@dataclass
class FeatureDescription:
    """Dataclass for storing information about features of the calmmage bot-lib

    Attributes:
        name (str): Name of the feature
        description (str): Description of the feature
        command (str): Command to invoke the feature
        project (str): Link to the project where the feature is used and showcased more

    Example:
        name: str = "Whisper Plugin"
        description: str = "The whisper plugin enables parsing of the audio messages into text"
        command: str = "/showcase_whisper"
        project: str = "t.me/calmmage_whisper_bot"
    """

    name: str
    description: str
    command: str
    project: str

    def __str__(self):
        return f"{self.name}: {self.description} ({self.command})"

    def _validate(self):
        assert self.name, "Name is required"
        assert self.description, "Description is required"
        assert self.command.startswith("/"), "Command must start with /"
        # check project is a proper URL
        assert self.project.startswith("http"), "Project must be a valid URL"


class ShowcaseApp(App):
    features = [
        FeatureDescription(
            name="Whisper",
            description="The whisper plugin enables parsing of the audio messages into text",
            command="/showcase_whisper",
            project="t.me/calmmage_whisper_bot",
        ),
        FeatureDescription(
            name="Dummy",
            description="The dummy plugin is a placeholder for testing purposes",
            command="/showcase_dummy",
            project="t.me/calmmage_dummy_bot",
        ),
    ]

    # def __init__(self, features: List[FeatureDescription], plugins=None):
    def __init__(self, plugins=None):
        # self.features = features
        self._features_dict = {
            feature.name.lower(): feature for feature in self.features
        }
        super().__init__(plugins=plugins)

        # todo: build embeddings for searching the ... features
        # alternative: ask chatgpt to do the search for us

    help_message = dedent(
        """
        Showcase bot features the commands demonstrating the features of the calmmage bot-lib.
        """
    )

    def get_help_message(self):
        message = super().get_help_message()
        message += "\n"
        message += self.get_info_message()
        return message

    def get_info_message(self):
        res = "Features:\n"
        for feature in self.features:
            description_first_line = feature.description.strip().split("\n")[0]
            res += f"{feature.command}: {description_first_line}\n"
        return res

    def get_start_message(self):
        message = dedent(
            """
            Hello! I am a showcase bot for the calmmage bot-lib. 
            I can show you commands based on the features of the bot-lib.
            """
        )
        message += "\n"
        message += self.get_info_message()
        return message

    # region Feature search
    def find_feature(self, feature: str, threshold=0.3) -> str:
        """
        Do a fuzzy embed search for the feature
        Returns a list of possible features that could match the result
         above the threshold probability
        """
        if feature in self._features_dict:
            return feature
        features = self._find_matching_features(feature, threshold)
        if len(features) == 0:
            raise ValueError(f"Feature {feature} not found")
        if len(features) > 1:
            raise ValueError(f"Multiple features found: {features}")
        return features[0]

    def _find_matching_features(self, feature: str, threshold=0.3) -> List[str]:
        """
        Do a fuzzy embed search for the feature
        Returns a list of possible features that could match the result
         above the threshold probability
        """
        # for now let's just do
        #  a) key is_substring of the name
        #  b) key in in the description
        results = []
        feature = feature.lower()
        for feature_name, feature_desc in self._features_dict.items():
            if (
                is_subsequence(feature, feature_name.lower())
                or feature in feature_desc.description.lower()
            ):
                results.append(feature_name)
        # todo: replace with proper fancy embedding search
        return results

    # endregion

    def get_feature(self, feature: str):
        """
        Get a feature by exact key
        """
        if feature not in self._features_dict:
            feature = self.find_feature(feature)
        return self._features_dict[feature]

    def describe_feature(self, feature: str):
        """
        describe a feature by exact key
        """
        if feature not in self._features_dict:
            feature = self.find_feature(feature)
        feature_description = self._features_dict[feature]
        message = dedent(
            """{name}
    
        Description
            {description}
        Showcase commands
            {command}
        Project
            {project}
        """
        )
        return message.format(
            name=feature_description.name,
            description=feature_description.description,
            command=feature_description.command,
            project=feature_description.project,
        )

    def dummy_feature(self, **kwargs):
        return f"Dummy feature. Got kwargs: {kwargs}"


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
