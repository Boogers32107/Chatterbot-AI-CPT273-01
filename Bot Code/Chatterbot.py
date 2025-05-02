import discord
from discord.ext import commands
import aiohttp
import html
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Add your bot token here
TOKEN = 'Bot_Token'

# Intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Train ChatterBot
chatbot = ChatBot('DiscordBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train('chatterbot.corpus.english')

current_trivia_question = None
current_trivia_answer = None

# Bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Event: Respond to messages
@bot.event
async def on_message(message):
    global current_trivia_question, current_trivia_answer

    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Handle commands
    if message.content.lower().startswith('!'):
        if message.content.lower() == '!joke':
            joke = await fetch_joke()
            await message.channel.send(joke)
        elif message.content.lower() == '!trivia':
            trivia, answer = await fetch_trivia()
            current_trivia_question = trivia
            current_trivia_answer = answer
            await message.channel.send(trivia)
        elif message.content.lower() in ['!true', '!false']:
            if current_trivia_question:
                # Sets case to lower and removes '!' for comparison
                user_answer = message.content.lower().replace('!', '')  # Removes the '!'
                if user_answer == current_trivia_answer.lower():
                    await message.channel.send("Correct! 🎉")
                else:
                    await message.channel.send(f"Wrong! The correct answer was {current_trivia_answer}.")
                # Reset trivia Question and Answer
                current_trivia_question = None
                current_trivia_answer = None
            else:
                await message.channel.send("No trivia question is active. Use `!trivia` to start one.")
        else:
            # Use ChatterBot for general conversation
            response = chatbot.get_response(message.content)
            await message.channel.send(str(response))

    # Process commands if any
    await bot.process_commands(message)

# Fetch a random joke from the Joke API
async def fetch_joke():
    url = "https://v2.jokeapi.dev/joke/Any"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['type'] == 'single':
                    return data['joke']
                elif data['type'] == 'twopart':
                    return f"{data['setup']} - {data['delivery']}"
            return "Sorry, I couldn't fetch a joke at the moment."

# Fetch a trivia question from Open Trivia DB
async def fetch_trivia():
    url = "https://opentdb.com/api.php?amount=1&difficulty=easy&type=boolean"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                question = html.unescape(data['results'][0]['question']) 
                correct_answer = html.unescape(data['results'][0]['correct_answer'])  
                return f"Trivia: {question} (!True/!False)", correct_answer
            return "Sorry, I couldn't fetch trivia at the moment.", None

# Run the bot
bot.run(TOKEN)