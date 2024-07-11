import discord
from discord.ext import commands
from discord import ui
import re
import mysql.connector
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Registration REGEX
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{4,32}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")
EMAIL_REGEX = re.compile(r"^[\w-]+@([\w-]+\.)+[\w-]{2,4}$")

#DB Creds
HOST=os.getenv('DB_HOST')
PORT=os.getenv('DB_PORT')
URL= f'http://{HOST}:{PORT}/'

class Registration(ui.Modal, title='Register to Chaos'):
    Username = ui.TextInput(label='Username', style=discord.TextStyle.short, placeholder='Username', required=True, min_length=4, max_length=23)
    Password = ui.TextInput(label='Password', style=discord.TextStyle.short, placeholder='Password', required=True, min_length=8, max_length=32)
    Email = ui.TextInput(label='E-Mail', style=discord.TextStyle.short, placeholder='Email', required=True, min_length=4, max_length=39)

    async def on_submit(self, interaction: discord.Interaction):
        errors = await self.validate_input()
        if errors:
            response = '\n\n'.join(errors)
            await interaction.response.send_message(response, ephemeral=True);
        else:
            data= {
                'username': self.Username.value,
                'password': self.Password.value,
                'email': self.Email.value,
                'discord_id': interaction.user.id
            }
            result = requests.post(URL+f'register/', json=data)
            user_data = result.json()
            if result.status_code == 201:
                await interaction.response.send_message(f'{user_data["username"]}', ephemeral=True)
            elif result.status_code == 404:
                await interaction.response.send_message(f'{user_data["error"]}', ephemeral=True)
            else:
                await interaction.response.send_message(f'{user_data["error"]}', ephemeral=True)

    async def validate_input(self):
        errors = []
        if not USERNAME_REGEX.match(self.Username.value) and not self.Username.value.isspace():
            errors.append('Username is Invalid! Make sure it is at minimum of 4 characters, has no spaces and a maximum 32 and can only accept alphanumeric and Underscore(_).')
        if not PASSWORD_REGEX.match(self.Password.value) and not self.Password.value.isspace():
            errors.append('Password Invalid! Make sure it is at minimum of 8 characters, has no spaces and provide at least 1 Uppercase and 1 Special character(@$!%*#?&).')
        if not EMAIL_REGEX.match(self.Email.value) and not self.Email.value.isspace():
            errors.append('Email Invalid! Make sure it is a valid E-Mail address.')
        if errors:
            errors.append('Please use /register again.')

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
    _discord_id = interaction.user.id
    result = requests.get(URL+f'user/{_discord_id}')

    if result.status_code == 200:
        # If registered Inform the user
        user_data = result.json()
        await interaction.response.send_message(f'You have already been registered. Your username is {user_data["username"]}.',ephemeral=True)
    else:
        await interaction.response.send_modal(Registration())

token = os.getenv('TOKEN')
client.run(token)



