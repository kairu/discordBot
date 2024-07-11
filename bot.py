# import discord
# from discord.ext import commands
# import mysql.connector
# import re
# from datetime import datetime

#MaraiDB Connection
# MYDB = mysql.connector.connect(
#     host="YourIP",
#     user="Username",
#     password="Password",
#     database="DatabaseName"
# )

# Create a cursor obj for DB
# dbCursor = MYDB.cursor()

# Bot Token

# # Discord Bot Intents
# intents = discord.Intents.default()
# intents.messages = True
# intents.message_content = True

# # Init the Discord Client
# bot = discord.Client(intents=intents)

# @bot.event
# async def on_ready():
#     print('We have logged in as {0.user}'.format(bot))

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if isinstance(message.channel, discord.channel.DMChannel):
#         if message.content.startswith('!register'):     
#             # Check if user is registered first
#             sql = "SELECT * FROM user WHERE discord_id = %s"
#             # Discord ID
#             val = message.author.id
#             dbCursor.execute(sql, val)
#             result = dbCursor.fetchone()

#             if result:
#                 # If registered Inform the user
#                 await message.author.send('You have already registered.')
#                 return

#             try:
#                 # Prompt the user for username
#                 await message.author.send('Input Username (must be between 4-32 characters, alphanumeric and underscore only):')
#                 username = await checkUser(await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(USERNAME_REGEX, m.content), timeout=60))

#                 # Password
#                 await message.author.send('Input Password (must be at least 8 character, at least 1 uppercase letter, 1 special character and no spaces):')
#                 password = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(PASSWORD_REGEX, m.content), timeout=60)

#                 # Email
#                 await message.author.send('Input a Valid Email:')
#                 email = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(EMAIL_REGEX, m.content), timeout=60)

#             except asyncio.TimeoutError:
#                 await message.author.send('Registration timed out. Please try again')
#                 return
            
#             # Get the register time and Discord ID
#             register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             discord_id = message.author.id

#             # Insert the user into the database
#             sql = "INSERT INTO registered (username, password, email, time, discord_id) VALUES (%s, %s, %s, %s, %s)"
#             val = (username.content, password.content, email.content, register_time, discord_id)
#             dbCursor.execute(sql, val)
#             MYDB.commit()

#             # Send a confirmation message to the user
#             await message.author.send('You have been registered! You can now login to the game!')

#  # Check username if its not taken
# async def checkUser(username):
#     # Check if the username is taken
#     sql = "SELECT * FROM registered WHERE username = %s"
#     val = username.content
#     dbCursor.execute(sql, val)
#     result = dbCursor.fetchone()

#     if result:
#         # If taken inform the user
#         await message.author.send('This username has already been taken. Please choose a different one:')
#         try:
#             new_username = await client.wait_for('message', check=lambda m:m.author == message.author and not m.content.isspace() and re.match(USERNAME_REGEX, m.content), timeout=60)
#             return await checkUser(new_username.content)
#         except asyncio.TimeoutError:
#             await message.author.send('Registration timed out. Please try again')
#             return
#     else:
#         return username.content

# bot.run(TOKEN)


import discord
from discord.ext import commands
from discord import ui
import re
# import mysql.connector

# # MariaDB Connection
# MYDB = mysql.connector.connect(
#     host="YourIP",
#     user="Username",
#     password="Password",
#     database="DatabaseName"
# )

# # Create a cursor obj for DB
# dbCursor = MYDB.cursor()

TOKEN = ''

# Registration REGEX
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{4,32}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")
EMAIL_REGEX = re.compile(r"^[\w-]+@([\w-]+\.)+[\w-]{2,4}$")

class Registration(ui.Modal, title='Register to Chaos'):
    Username = ui.TextInput(label='Username', style=discord.TextStyle.short, placeholder='Username', required=True, min_length=4, max_length=32)
    Password = ui.TextInput(label='Password', style=discord.TextStyle.short, placeholder='Password', required=True, min_length=8)
    Email = ui.TextInput(label='E-Mail', style=discord.TextStyle.short, placeholder='Email', required=True, min_length=4)

    async def on_submit(self, interaction: discord.Interaction):
        errors = await self.validate_input()
        if errors:
            response = '\n\n'.join(errors)
            await interaction.response.send_message(response, ephemeral=True);
        else:
            await interaction.response.send_message(f'Registration Complete!', ephemeral=True)

    async def validate_input(self):
        errors = []
        if not USERNAME_REGEX.match(self.Username.value) and not self.Username.value.isspace():
            errors.append('Username is Invalid! Make sure it is at minimum of 4 characters, has no spaces and a maximum 32 and can only accept alphanumeric and Underscore(_).')
        if not PASSWORD_REGEX.match(self.Password.value) and not self.Password.value.isspace():
            errors.append('Password Invalid! Make sure it is at minimum of 8 characters, has no spaces and provide at least 1 Uppercase and 1 Special character(@$!%*#?&).')
        if not EMAIL_REGEX.match(self.Email.value) and not self.Email.value.isspace():
            errors.append('Email Invalid! Make sure it is a valid E-Mail address.')

        return errors


class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)
    
    async def on_ready(self):
        print('We have logged in as ' + self.user.name)
        synced = await self.tree.sync()

client = Client()

@client.tree.command(name='register')
async def modal(interaction: discord.Interaction):
    # Check if user is registered first
    sql = "SELECT * FROM user WHERE discord_id = %s"
    # Discord ID
    val = interaction.user.id
    dbCursor.execute(sql, val)
    result = dbCursor.fetchone()

    if result:
        # If registered Inform the user
        await interaction.response.send_message(f'You have already been registered.',ephemeral=True)
    else:
        await interaction.response.send_modal(Registration())

client.run(TOKEN)



