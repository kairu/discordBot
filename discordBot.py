import discord
import mysql.connector
import re
from datetime import datetime

# Set up the MariaDB database connection
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword",
  database="yourdatabase"
)

# Create a cursor object to interact with the database
mycursor = mydb.cursor()

# Initialize the Discord client
client = discord.Client()

# Regular expressions for checking username, password, and email format
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,32}$"
PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
EMAIL_REGEX = r"^[\w-]+@([\w-]+\.)+[\w-]{2,4}$"

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.channel.DMChannel):
        if message.content.startswith('!register'):
            # Check if the user is already registered
            sql = "SELECT * FROM users WHERE discord_id = %s"
            val = (message.author.id,)
            mycursor.execute(sql, val)
            result = mycursor.fetchone()

            if result:
                # If the user is already registered, send a message to inform them
                await message.author.send('You are already registered.')
                return

            # Prompt the user to input their username
            await message.author.send('Input Username (must be between 3-32 characters, alphanumeric and underscore only):')
            try:
                username = await client.wait_for('message', check=lambda m: m.author == message.author and not m.content.isspace() and re.match(USERNAME_REGEX, m.content), timeout=60)
            except asyncio.TimeoutError:
                await message.author.send('Registration timed out. Please try again later.')
                return

            # Prompt the user to input their password
            await message.author.send('Input Password (must be at least 8 characters, at least 1 uppercase letter, 1 special character and no spaces):')
            try:
                password = await client.wait_for('message', check=lambda m: m.author == message.author and not m.content.isspace() and re.match(PASSWORD_REGEX, m.content), timeout=60)
            except asyncio.TimeoutError:
                await message.author.send('Registration timed out. Please try again later.')
                return

            # Prompt the user to input their email
            await message.author.send('Input Email:')
            try:
                email = await client.wait_for('message', check=lambda m: m.author == message.author and not m.content.isspace() and re.match(EMAIL_REGEX, m.content), timeout=60)
            except asyncio.TimeoutError:
                await message.author.send('Registration timed out. Please try again later.')
                return

            # Get the register time and Discord ID
            register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            discord_id = message.author.id

            # Insert the user's information into the database
            sql = "INSERT INTO users (username, password, email, time, discord_id) VALUES (%s, %s, %s, %s, %s)"
            val = (username.content, password.content, email.content, register_time, discord_id)
            mycursor.execute(sql, val)
            mydb.commit()

            # Send a confirmation message to the user
            await message.author.send('You have been registered.')