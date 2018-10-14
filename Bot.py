from discord.ext.commands import Bot
from discord import Game
import json
import asyncio
import requests
import sys

BOT_PREFIX = "?"
TOKEN = ""  # Insert Bottoken here
# Load User.json with all the Discord IDs and the associated TaskHero API Keys
with open("User.json", 'r') as f:
    userdata = json.load(f)
client = Bot(command_prefix=BOT_PREFIX)


# When the Bot starts up, it's Gaming status is set to "Playing along"
@client.event
async def on_ready():
    await client.change_presence(game=Game(name="along"))
    print("Logged in as " + client.user.name)


# Little ASCII Animation on new member join
@client.event
async def on_member_join(member):
    general = client.get_channel('462620066274607105')  # Hardcoded Channel IP of the General Channel
    my_message = await client.send_message(general,
                                           "```        _\n        (_)\n        |=|\n        |=|\n    /|__|_|__|\n   (    ( )    )\n    \|\/\\\"/\/|/\n      |  Y  |\n      |  |  |\n      |  |  |\n     _|  |  |\n  __/ |  |  |\\\n /  \ |  |  |  \\\n    __|  |  |   |\n /\/  |  |  |   |\\\n  <   +\ |  |\ />  \\\n   >   + \  | LJ    |\n         + \|+  \  < \\\n   (O)      +    |    )\n    |             \  /\ \n  ( | )   (o)      \/  )\n _\\|//__( | )______)_/ \n         \\|//```"
                                           "\nFight monsters (and your own procrastination)")
    await asyncio.sleep(4)
    await client.delete_message(my_message)
    my_message = await client.send_message(general,
                                           " ```   ,-----------.\n   (_\           \\\n      |           |\n      |           |\n      |           |\n      |           |\n     _|           |\n    (_/_____(*)___/\n             \\\n              ))\n              ^\"\)```"
                                           "\nTravel with friends (and find new companions)")
    await asyncio.sleep(4)
    await client.delete_message(my_message)
    my_message = await client.send_message(general,
                                           "``` ____________________\n|                    |\n|                    |\n|                    |\n|  _______ _    _    |\n| |__   __| |  | |   |\n|    | |  | |__| |   | \n|    | |  |  __  |   |\n|    | |  | |  | |   |\n|    |_|  |_|  |_|   |    \n|                    |  \n:                    :  \n \                  /     \n  \                /  \n   \              /   \n    `\          /' \n      `-. __ .-` ```"
                                           "Protect the world of task hero")
    await asyncio.sleep(4)
    await client.delete_message(my_message)
    await asyncio.sleep(1)
    await client.send_message(general,
                              member.mention + " welcome to TaskHero's Discord (Please use ?signin)")


@client.command(name='signin',
                description="Connects your Discord Profile with TaskHero via a PM",
                brief="Identify yourself, Hero!",
                aliases=['login'],
                pass_context=True)
async def signin(context):
    # Check if Discord User ID is already in User.json
    if userdata is not None:
        for userdict in userdata:
            if userdict['id'] == context.message.author.id:
                await client.send_message(context.message.author, "You already are signed in. "
                                                                  "If you want to change your API Key, "
                                                                  "please type ?signout amd than ?signin again.")

                return 0
    await client.send_message(context.message.author, 'Please insert your API key here. '
                                                      '\nYou can find it in the Options on theTaskHero Website. '
                                                      '\nPlease send it here '
                                                      'and NOT via the server chat to keep your data safe.'
                                                      '\nPlease make sure its the right one, '
                                                      'as at the moment there is no way to change it.')
    message = await client.wait_for_message(author=context.message.author)
    # Check if insert API Key has UUID length
    if len(message.content) is not 36:
        await client.send_message(context.message.author, "This is an invalid key. "
                                                          "\nPlease use ?signin again and insert a valid key.")
        return 0
    # Check if API Key is already in User.json
    for userdict in userdata:
        if userdict['key'] == message.content:
            await client.send_message(context.message.author, "This API Key is already in usage. "
                                                              "\nIf this really is your key, please contact lys.")
            return 0
    info = {'id': context.message.author.id, 'key': message.content}
    userdata.append(info)
    # Writes new API Key and Discord UserID into User.json
    with open("User.json", 'w') as n:
        json.dump(userdata, n)
    await client.send_message(context.message.author,
                              "Your API key (" + message.content + ") is now associated with your discord account.")
    await client.send_message(context.message.channel,
                              context.message.author.mention + ' now joined the taskforce :grin:')


@client.command(name='signout',
                description="Deletes the connection between your TaskHero Account and your Discord. "
                            "PLEASE USE WITH CAUTION!",
                brief="Goodbye, Hero!",
                aliases=['logout'],
                pass_context=True)
async def signout(context):
    for userdict in userdata:
        if userdict['id'] == context.message.author.id:
            await client.send_message(context.message.channel, "Are you sure you want to leave :cry:  ? Y/N"
                                                               "\n(This doesn't delete your TaskHero Account "
                                                               "and you can reconnect it via ?signin.)")
            message = await client.wait_for_message(author=context.message.author)
            answer = message.content.lower()
            if str(answer) == "y":
                await client.send_message(context.message.channel, context.message.author.mention +
                                          ' now left the task force :disappointed_relieved:')
                userdata.remove(userdict)
                with open("User.json", 'w') as nf:
                    json.dump(userdata, nf)
                return 0
            else:
                await client.send_message(context.message.channel, "Alright, you will continue being signed in.")
                return 0

        else:
            await client.send_message(context.message.author, " You aren't signed in!")
            return 0


# For checking if the Discord UserID is associated with a th api id in the file
def checkin(uid):
    if userdata is not None:
        for userdict in userdata:
            if userdict['id'] == uid:
                return userdict['key']

        return 0


# Get list of all tasks with id, name and checked status
def alltasks(uid):
    reqlist = requests.get('https://www.taskheroics.com/api/tasks?APIKey=' + uid)
    tasks = reqlist.json().get('tasks')
    templist = []
    for task in tasks:
        if task['isCleared'] is False and task['tutorialTask'] is False or task['tutorialTask'] is None:
            taskinfos = {'id': task['_id'], 'text': task['text'], 'checked': task['schedule']['checked']}
            templist.append(taskinfos)
    return templist


@client.command(name='new',
                description="Creates a task",
                brief="Thought of another task to do?",
                aliases=['n', 'add'],
                pass_context=True)
async def tasknew(context, title):
    notes = None
    date = None
    # Login Check
    if checkin(context.message.author.id) is not 0:
        tempkey = checkin(context.message.author.id)
    else:
        await client.send_message(context.message.channel, 'You have to be logged in to use this function.')
        return 0
    await client.send_message(context.message.channel, "Do you want do add notes and/or a date  ? Y/N")
    message = await client.wait_for_message(author=context.message.author)
    answer = message.content.lower()
    if str(answer) == "y":
        await client.send_message(context.message.channel, "Please Enter note, if you dont want one, enter skip")
        message = await client.wait_for_message(author=context.message.author)
        answer = message.content.lower()
        if answer == "skip":
            pass
        else:
            notes = message.content
        await client.send_message(context.message.channel, "Please Enter Date, if you dont want one, enter just letters, or bang your hand on the keyboard, that should work too")
        message = await client.wait_for_message(author=context.message.author)
        answer = message.content.lower()
        if answer is "":
            pass
    # Request
    plnewtask = {'APIKey': tempkey, 'title': title, 'notes': notes, 'dueDate': date}
    headers = {'content-type': 'application/json'}
    reqnewtask = requests.post('https://www.taskheroics.com/api/tasks', data=json.dumps(plnewtask), headers=headers)
    task = reqnewtask.json()['task']
    send = ""
    send += "Name: *"+task['text']+"*\n"
    if task['notes'] != '':
        send += "Text: *" + task['notes'] + "*\n"
    if task['schedule']['scheduledAt'] is False:
        send += "Due Date: *" + task['schedule']['scheduledAt'][0]['dueDate'] + "*\n"

    await client.send_message(context.message.channel, 'Created new tasks with following specs:\n'+send)


@client.command(name='check',
                description="Checks/Unchecks a task",
                brief="You really did it, quick, get your reward",
                aliases=['c', 'tick'],
                pass_context=True)
async def taskcheck(context, tasknumber):
    # Login Check
    if checkin(context.message.author.id) is not 0:
        tempkey = checkin(context.message.author.id)
    else:
        await client.send_message(context.message.channel, 'You have to be logged in to use this function.')
        return 0

    # Is the tasknumber on the list?
    templist = alltasks(tempkey)
    if tasknumber.isdigit() and int(tasknumber)-1 > len(templist):
        await client.send_message(context.message.channel, 'Number is out of range. Please use ?list. ')
    elif tasknumber.isdigit():
        pass
    else:
        await client.send_message(context.message.channel, 'THIS IS NO NUMBER!!! I QUIT!')

    # Is task already checked -> uncheck
    # Vice versa
    if templist[int(tasknumber)-1]['checked'] is False:
        completed = "true"
    else:
        completed = "false"

    # REQUEST
    plcheck = {'APIKey': tempkey, 'id': templist[int(tasknumber)-1]['id'], 'completed': completed}
    headers = {'content-type': 'application/json'}
    reqcheck = requests.post('https://www.taskheroics.com/api/tasks/complete', data=json.dumps(plcheck), headers=headers)

    # Check if call succeeded and post results
    success = reqcheck.json()['success']
    loot = reqcheck.json()['loot']
    if success is False:
        await client.send_message(context.message.channel, "An error occurred")
        return 0
    else:
        if completed is "true":
            await client.send_message(context.message.channel, "You checked \""+templist[int(tasknumber)-1]['text']+"\"")
        elif completed is "false":
            await client.send_message(context.message.channel, "You unchecked \"" + templist[int(tasknumber)-1]['text']+"\"")
        if loot is not None:
            exp = loot['xpGained']
            mana = loot['manaGained']
            gold = loot['goldGained']
            await client.send_message(context.message.channel, "You gained "+str(exp)+" XP, "+str(mana)+" Mana and "+str(gold)+" Gold.")


@client.command(name='list',
                description="Shows a list of all of your tasks",
                brief="A scroll full of tasks that lie ahead",
                aliases=['ls'],
                pass_context=True)
async def tasklist(context):
    if checkin(context.message.author.id) is not 0:
        tempkey = checkin(context.message.author.id)
    else:
        await client.send_message(context.message.channel, 'You have to be logged in to use this function.')
        return 0
    templist = alltasks(tempkey)
    printtasks = ""
    counter = 1
    k = 0
    for item in templist:
        print(k)
        k += 1
        if item['checked']:
            printtasks += ":white_check_mark: "
        else:
            printtasks += ":x: "
        printtasks += "**" + str(counter) + "**. "
        printtasks += item['text'] + "\n"
        counter += 1
    await client.send_message(context.message.channel, '**These are the Tasks you seeked**\n' + printtasks +
                              '\nWrite the number of the task behind ?info, if you want to know more about it. \n'
                              'Or write the number of the task behind ?check, to check or uncheck it.')


@client.command(name='info',
                description="Shows information about one task",
                brief="This is your Mission (please enter number from ?list)",
                aliases=['i'],
                pass_context=True)
async def taskinfo(context, tasknumber):
    if checkin(context.message.author.id) is not 0:
        key = checkin(context.message.author.id)
    else:
        await client.send_message(context.message.channel, 'You have to be logged in to use this function.')
        return 0
    templist = alltasks(key)
    tid = templist[int(tasknumber)-1]['id']
    reqinfo = requests.get('https://www.taskheroics.com/api/tasks/'+tid+"?APIKey="+key)
    task = reqinfo.json().get('task')
    taskinfos = ""
    if task['schedule']['checked'] is False:
        taskinfos += ":x: "
    else:
        taskinfos += ":white_check_mark: "

    taskinfos += "**" + task['text'] + "**\n"
    if task['notes'] is not '' or ' ':
        taskinfos += "*" + task['notes'] + "*\n"
    checklist = task['checklist']
    print(taskinfos)

    for item in checklist:
        print(k)

        if item['content'] == "":
            pass
        elif item['checked'] is False:
            taskinfos += "    - :x: "+item['content']+"\n"
        else:
            taskinfos += "    - :white_check_mark: "+item['content']+"\n"
        print(taskinfos)
    print(taskinfos)
    await client.send_message(context.message.channel, taskinfos)


@client.command(name='delete',
                description="Deletes Bots messages in the channel from where its called",
                brief="The advice of the past will go away.",
                aliases=['del', 'clear'],
                pass_context=True)
async def delete(context):
    msgs = []
    async for msg in client.logs_from(context.message.channel):
        if str(context.message.channel.type) == "text":
            if msg.author == client.user or msg.content[:1] is "?":
                msgs.append(msg)
        elif str(context.message.channel.type) == "private":
            if msg.author == client.user:
                msgs.append(msg)
    if msgs is not None:
        for msg in msgs:
            await client.delete_message(msg)


@client.command(name='close',
                description="Disconnects the bot.",
                brief="Sends me sleeping",
                aliases=['exit', 'esc'],
                pass_context=True
                )
async def close(context):
    await client.send_message(context.message.channel, 'Good Bye! :hand_splayed: ')
    client.close()
    sys.exit()


client.run(TOKEN)
