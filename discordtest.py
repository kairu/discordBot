import discord
import mysql.connector
import re
from datetime import datetime

# Registration REGEX
USERNAME_REGEX = r"^[a-zA-Z0-9_]{4,32}$"
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
EMAIL_REGEX = r"^[\w-]+@([\w-]+\.)+[\w-]{2,4}$"

#MaraiDB Connection
MYDB = mysql.connector.connect(
    host="YourIP",
    user="Username",
    password="Password",
    database="DatabaseName"
)

# Create a cursor obj for DB
dbCursor = MYDB.cursor()

# Bot Token
TOKEN = ''

# Discord Bot Intents
intents = discord.Intents.default()
intents.messages = True
# intents.message_content = True

# Init the Discord Client
bot = discord.Client()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.channel.DMChannel):
        if message.content.startswith('!register'):
            # Check if user is registered first
            sql = "SELECT * FROM user WHERE discord_id = %s"
            # Discord ID
            val = message.author.id
            dbCursor.execute(sql, val)
            result = dbCursor.fetchone()

            if result:
                # If registered Inform the user
                await message.author.send('You have already registered.')
                return

            try:
                # Prompt the user for username
                await message.author.send('Input Username (must be between 4-32 characters, alphanumeric and underscore only):')
                username = await checkUser(await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(USERNAME_REGEX, m.content), timeout=60))

                # Password
                await message.author.send('Input Password (must be at least 8 character, at least 1 uppercase letter, 1 special character and no spaces):')
                password = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(PASSWORD_REGEX, m.content), timeout=60)

                # Email
                await message.author.send('Input a Valid Email:')
                email = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(EMAIL_REGEX, m.content), timeout=60)

            except asyncio.TimeoutError:
                await message.author.send('Registration timed out. Please try again')
                return
            
            # Get the register time and Discord ID
            register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            discord_id = message.author.id

            # Insert the user into the database
            sql = "INSERT INTO registered (username, password, email, time, discord_id) VALUES (%s, %s, %s, %s, %s)"
            val = (username.content, password.content, email.content, register_time, discord_id)
            dbCursor.execute(sql, val)
            MYDB.commit()

            # Send a confirmation message to the user
            await message.author.send('You have been registered! You can now login to the game!')

 # Check username if its not taken
async def checkUser(username):
    # Check if the username is taken
    sql = "SELECT * FROM registered WHERE username = %s"
    val = username.content
    dbCursor.execute(sql, val)
    result = dbCursor.fetchone()

    if result:
        # If taken inform the user
        await message.author.send('This username has already been taken. Please choose a different one:')
        try:
            new_username = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(USERNAME_REGEX, m.content), timeout=60)
            return await checkUser(new_username.content)
        except asyncio.TimeoutError:
            await message.author.send('Registration timed out. Please try again')
            return
    else:
        return username.content
