#!/usr/bin/python3 

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon import functions, types
from telethon import errors
import telethon.sync
import os


# Remember to use your own values from my.telegram.org[api_id,api_hash,string_session]!
api_id = os.environ.get("APP_ID", 6)

api_hash = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

string = os.environ.get("STRING_SESSION", None)

client = TelegramClient(StringSession(string), api_id, api_hash)
whitelist = set()
myIDXYZ_COOKY = None
onHold = False  # Managing bot Live/Dead

# Refresh contact list


async def refresh_contacts():

    global whitelist

    result = await client(functions.contacts.GetContactsRequest(
        hash=0
    ))

    for i in range(len(result.contacts)):

        whitelist.add(result.contacts[i].user_id)

    return 0


async def manual():

    await client.send_message('me', '**Usage :** \n'

                              '```.start``` or ```.restart``` -> Restart the bot [Default - on start]\n\n'

                              '```.stop``` or ```.hold``` -> Stops the bot [Use ```.start``` or ```.restart``` to enable]\n\n'

                              '```.ap``` or ```.approve```-> Adds the user in whitelist when you reply\n\n'

                              '```.dis``` or ```.disapprove``` -> Removes the user from whitelist when you reply\n\n'

                              '```.re``` or ```.refresh``` -> Refresh the contacts to the bot\n\n'

                              '```.man``` or ```.manual``` or ```.h``` or ```.help``` -> For manual page\n\n'

                              '**Note : **\n'

                              '1. approve or disapprove can be used in groups and channels. Remaining in private\n'

                              '2. Users in whitelist can\'t be banned automatically')

    return 0

# Starting function


async def main():

    global whitelist
    global myIDXYZ_COOKY

    myIDXYZ_COOKY = await client.get_peer_id('me')  # User INT ID

    whitelist.add(myIDXYZ_COOKY)

    await refresh_contacts()

    async for dialog in client.iter_dialogs():

        whitelist.add(dialog.id)

    await manual()


# Handling events
@client.on(events.NewMessage)
async def my_event_handler(event):

    global onHold

    raw_text = event.raw_text

    if not onHold:

        global whitelist

        sender_id = event.sender_id

        is_reply_condition = event.is_reply and sender_id == myIDXYZ_COOKY and event.is_private == False

        if is_reply_condition and raw_text in ['.ap', '.approve']:

            replied = await event.get_reply_message()
            whitelist.add(replied.from_id)
            await event.delete()

        elif is_reply_condition and raw_text in ['.dis', '.disapprove']:

            replied = await event.get_reply_message()
            whitelist.discard(replied.from_id)
            await event.delete()

        elif event.is_private:

            chat_id = event.chat_id

            if sender_id == myIDXYZ_COOKY:

                whitelist.add(chat_id)

            elif chat_id not in whitelist:

                await client.get_dialogs()
                await client(functions.messages.ReportSpamRequest(
                    peer=chat_id
                ))
                await client(functions.contacts.BlockRequest(id=chat_id))
                await client.delete_dialog(chat_id)

            if raw_text in ['.re', '.refresh']:

                await refresh_contacts()
                await event.delete()

            if raw_text in ['.h', '.help', '.man', '.manual']:

                await manual()
                await event.delete()

            if raw_text in ['.stop', '.hold']:

                onHold = True

                await client.send_message('me', 'Stopped!')

    elif onHold and raw_text in ['.start', '.restart']:

        onHold = False
        await client.send_message('me', 'Bot Started!')

# main function
with client:
    client.loop.run_until_complete(main())

# event initialization
client.start()
client.run_until_disconnected()
