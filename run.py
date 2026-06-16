import logging
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.classes.AnalyticsServer import streamers
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Matrix import Matrix
from TwitchChannelPointsMiner.classes.Pushover import Pushover
from TwitchChannelPointsMiner.classes.Gotify import Gotify
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

import os
from dotenv import load_dotenv

load_dotenv() 

def str_to_attr(str_array: list) -> list:
    return [getattr(Events, ev) for ev in str_array if hasattr(Events, ev)]

login_acc = os.getenv("LOGIN")
password_acc = os.getenv("PASSWORD")

streamers_array = os.getenv("STREAMERS").split(',')

# Discord notifications
discord_notify = os.getenv("DISCORD_WEBHOOK_URL", "")
if discord_notify != "":
    events_for_notify_ds = os.getenv("EVENTS_FOR_NOTIFY_DS", "").split(',')

    if events_for_notify_ds[0] == "":
        events_for_notify_ds = ["STREAMER_ONLINE","STREAMER_OFFLINE"]
    
    events_arr_for_notify_ds = str_to_attr(events_for_notify_ds)

    discord_notify = Discord(
        webhook_api=discord_notify,
        events=events_arr_for_notify_ds
    )
else:
    discord_notify = None

# Telegram notifications
tg_chat_id = os.getenv("TG_CHAT_ID", "") # Chat ID to send messages @getmyid_bot
tg_bot_api_token = os.getenv("TG_BOT_API_TOKEN", "") # Telegram API token @BotFather
tg_notify = None
if tg_bot_api_token != "" and tg_chat_id != "":
    events_for_notify_tg = os.getenv("EVENTS_FOR_NOTIFY_TG", "").split(',')

    if events_for_notify_tg[0] == "":
        events_for_notify_tg = ["STREAMER_ONLINE", "STREAMER_OFFLINE"]

    events_array_for_notify_tg = str_to_attr(events_for_notify_tg)

    tg_notify = Telegram(
        chat_id=int(tg_chat_id),
        token=tg_bot_api_token,
        events=events_array_for_notify_tg
    )


acc = TwitchChannelPointsMiner(
    username=login_acc,
    password=password_acc,
    claim_drops_startup=False,                  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[                                  # Custom priority in this case for example:
        Priority.ORDER,
        Priority.STREAK
    ],
    enable_analytics=False,                     # Disables Analytics if False. Disabling it significantly reduces memory consumption
    disable_ssl_cert_verification=False,        # Set to True at your own risk and only to fix SSL: CERTIFICATE_VERIFY_FAILED error
    disable_at_in_nickname=False,               # Set to True if you want to check for your nickname mentions in the chat even without @ sign
    logger_settings=LoggerSettings(
        save=False,                              # If you want to save logs in a file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info
        console_username=True,                 # Adds a username to every console log line if True. Also adds it to Telegram, Discord, etc. Useful when you have several accounts
        auto_clear=True,                        # Create a file rotation handler with interval = 1D and backupCount = 7 if True (default)
        time_zone="Europe/Moscow",              # Set a specific time zone for console and file loggers. Use tz database names. Example: "America/Denver"
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=False,                             # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=False,                             # If you think that the logs are too verbose, set this to True
        colored=True,                           # If you want to print colored text
        color_palette=ColorPalette(             # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",            # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",             # Read more in README.md
            BET_wiN=Fore.MAGENTA                # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=tg_notify,
        discord=discord_notify,
        webhook=None,
        matrix=None,
        pushover=None,
        gotify=None
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,                  # If you want to Bet / Make prediction
        follow_raid=True,                       # Follow raid to obtain more points
        claim_drops=False,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        claim_moments=False,                     # If set to True, https://help.twitch.tv/s/article/moments will be claimed when available
        watch_streak=True,                      # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        community_goals=False,                  # If True, contributes the max channel points per stream to the streamers' community challenge goals
        chat=ChatPresence.ONLINE,               # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=None
    )
)

acc.mine(
    [
        Streamer(el) for el in streamers_array
    ],
    followers=False,
    followers_order=FollowersOrder.ASC
)
