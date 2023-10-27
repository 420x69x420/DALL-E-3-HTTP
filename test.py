import datetime
import io
import json
import random
import re
import time

from aiohttp import ClientSession

timeout = 600_000
def read_json_file(filename="cookies_U_owners.json"):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def write_json_file(data, filename="cookies_U_owners.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def add_entry(entry):
    data = read_json_file()
    data.append(entry)
    write_json_file(data)


def search_entry(u_value):
    data = read_json_file()
    for entry in data:
        if entry["_U"] == u_value:
            return entry
    return None


def add_blocked_timestamp(u_value):
    """Add a timestamp to the 'blocked' key of a specified entry."""
    data = read_json_file()
    current_timestamp = datetime.datetime.now().isoformat()

    for entry in data:
        if entry["_U"] == u_value:
            if "blocked" not in entry:
                entry["blocked"] = []
            entry["blocked"].append(current_timestamp)
            write_json_file(data)
            return True
    return False
def is_entry_locked(u_value):
    """Check if the specified entry is blocked (within 12 hours of any 'blocked' timestamp)."""
    data = read_json_file()
    current_time = datetime.datetime.now()

    for entry in data:
        if entry["_U"] == u_value:
            if "locked" in entry:
                return True
    return False

def is_entry_blocked(u_value):
    """Check if the specified entry is blocked (within 12 hours of any 'blocked' timestamp)."""
    data = read_json_file()
    current_time = datetime.datetime.now()

    for entry in data:
        if entry["_U"] == u_value:
            if "blocked" in entry:
                for timestamp in entry["blocked"]:
                    time_blocked = datetime.datetime.fromisoformat(timestamp)
                    difference = current_time - time_blocked
                    if difference.total_seconds() <= 43_200:  # 12 hours in seconds
                        return True
    return False

def get_random_non_blocked_entry():
    """Return a random non-blocked _U value, or None if all are blocked."""
    data = read_json_file()

    non_blocked_entries = [entry["_U"] for entry in data if not is_entry_blocked(entry["_U"])]

    return random.choice(non_blocked_entries) if non_blocked_entries else None

import asyncio

async def get_token_count(_U, subdomain):
    init_referrer = f"https://{subdomain}.bing.com/images/create?FORM=GENEXP"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
        "Referer": init_referrer,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
    }

    cookies = {
        "_U": _U,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://{subdomain}.bing.com/images/create", headers=headers,
                               cookies=cookies) as response:

            headers = response.headers
            content_raw = await response.read()

            if isinstance(content_raw, bytes):
                content = content_raw.decode('utf-8')
            print("HEADERS2")
            print(headers)
            print("CONTENT2")
            print(content)

            def extract_numeric_value(text):
                prefix = 'data-tb="'
                suffix = '"'

                start = text.find(prefix)
                if start == -1:
                    return None
                start += len(prefix)
                end = text.find(suffix, start)
                if end == -1:
                    return None
                return int(text[start:end])

            token_count = extract_numeric_value(content)
            print(f"found token count: {token_count}")
            return token_count

def append_string_to_file(input_string):
    with open("images_discord.txt.txt", "a", encoding='utf-8') as file:
        file.write('\n' + input_string)

def get_random_subdomain():
    possibilities = ["www", "www2"]
    return random.choice(possibilities)
async def make_images(prompt, message):
    _U = get_random_non_blocked_entry()
    print(f"Test1: cookie _U:{_U}")
    if _U is None:
        return None, None
    print(f"test23: prompt: {prompt}")
    subdomain = get_random_subdomain()
    async with aiohttp.ClientSession() as session:
        def current_milliseconds() -> int:
            # Get the current time in seconds since the epoch and convert it to milliseconds
            return int(time.time() * 1000)
        def extract_ig_value(content):
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            pattern = r'&amp;IG=([A-Z0-9]+)&amp;'
            match = re.search(pattern, content)
            if match:
                return match.group(1)
            return None
        init_referrer = f"https://{subdomain}.bing.com/images/create?FORM=GENEXP"


        def detect_error_pattern(text):
            """
            Detects error pattern in the provided text.

            Args:
            - text (str): The text to be scanned.

            Returns:
            - str: 'block' if blocked content, 'limited' if rate limited, or None if no pattern detected.
            """
            # Regular expression patterns

            if '''<div id="girer" class="block_icon" dq-err="''' in text and '''alt="You can&#39;t submit any more prompts"''' in text:
                return "RATE_LIMITED"
            elif '''<div id="girer" class="block_icon" dq-err="''' in text and '''alt="Content warning"''' in text:
                return "UNSAFE_PROMPT"
            else:
                return None



        token = await get_token_count(_U, subdomain)
        if token == 0:
            rt = "3"
            use_tokens = "No"
            speed = "slow"
        else:
            rt = "4"
            use_tokens = "Yes"
            speed = "fast"
        await message.channel.send(f'{message.author.mention} Requesting image, plz wait (use token={use_tokens}, {speed} generation speed)...')

        async with session.post(
                f"https://{subdomain}.bing.com/images/create",
                params={"q": prompt, "rt": rt, "FORM": "GENCRE"},
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Referer": init_referrer,
                    "Cookie": f"_U={_U};",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    #"Sec-Fetch-Site": "same-origin",
                    #"Sec-Fetch-User": "?1",
                    "Host": f"{subdomain}.bing.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Origin": f"https://{subdomain}.bing.com",
                    "DNT": "1",
                    #"Content-Length": "15",
                    #"Content-Type": "application/x-www-form-urlencoded",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "TE": "trailers",
                },
                data={"q": prompt, "qs": "ds"},
        ) as resp:
            headers = resp.headers
            content_raw = await resp.read()

        def extract_content(text: str) -> list:
            # Update the regular expressions to include underscores
            pattern1 = r';OIG\.([a-zA-Z0-9._]+)&quot;'
            pattern2 = r'https://th\.bing\.com/th/id/OIG\.([a-zA-Z0-9._]+)\?'
            pattern3 = r'OIG\.([a-zA-Z0-9._]+)\?'
            pattern4 = r'"OIG\.([a-zA-Z0-9._]+)"'
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            # Search for the patterns in the text
            matches1 = re.findall(pattern1, text)
            matches2 = re.findall(pattern2, text)
            matches3 = re.findall(pattern3, text)
            matches4 = re.findall(pattern4, text)
            # Combine and deduplicate the matches
            ids = list(set(matches1 + matches2 + matches3 + matches4))

            return ids


        from typing import Optional, Union, Dict

        def extract_id(text):
            prefix = "/images/create/async/results/"
            suffix = "?q="

            start = text.find(prefix)
            if start == -1:
                print(f"Not found prefix in initial POST (search for eventID): {prefix}")
                return None
            start += len(prefix)
            end = text.find(suffix, start)
            if end == -1:
                print(f"FOUND prefix: {prefix} BUT NOT FOUND SUFFIX (search for eventID): {suffix}")
                return None
            return text[start:end]

        print("HEADERS- FIRST")
        print(headers)
        print("CONTENT- FIRST")
        print(content_raw)
        if isinstance(content_raw, bytes):
            content = content_raw.decode('utf-8')

        event_id = extract_id(content)
        if event_id is None:
            potential_error = detect_error_pattern(content)
            if potential_error is not None:
                print(f'FOUND FUCKY WUCKY: {potential_error}')
                return _U, potential_error
            if 'in-2zU3AJUdkgFe7ZKv19yPBHVs.png' in content or 'TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg' in content:
                bad_prompt_url = 'https://r.bing.com/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png'
                print(f"BAD PROMPT:{bad_prompt_url}")
                return _U, bad_prompt_url
            return _U, "NO_VALID_EVENT_ID"

        print(f"event_id FOUND: {event_id}")
        print("Test2")
        # set_id = extract_id_from_content(content)
        # print(f"set_id: {set_id}")
        IG_value = extract_ig_value(content)
        print(f"Test4: IG={IG_value}")



        global timeout
        timeout_temp = current_milliseconds() + timeout
        while current_milliseconds() < timeout_temp:

            params = (
                ('q', prompt),
                ('IG', IG_value),
                ('IID', 'images.as'),
            )

            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "DNT": "1",
                "Referer": init_referrer,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
            }

            cookies = {
                "_U": _U,
            }
            async with session.get(
                    f"https://{subdomain}.bing.com/images/create/async/results/{event_id}",
                    params=params, headers=headers, cookies=cookies) as resp:
                headers = resp.headers
                content = await resp.read()


            print("test15")
            print("HEADERS")
            print(headers)
            print("CONTENT")
            print(content)
            bad_prompt_url = ""
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            if 'in-2zU3AJUdkgFe7ZKv19yPBHVs.png' in content or 'TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg' in content:
                bad_prompt_url = 'https://r.bing.com/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png'
            if bad_prompt_url:
                print(f"BAD PROMPT:{bad_prompt_url}")
                return _U, bad_prompt_url
            URLz = extract_content(content)
            if len(URLz) > 0:
                print('FOUND URLZ (content)!!!')
                print(URLz)
                formatted_URLz = []
                append_string_to_file(f"PROMPT: {prompt}")
                for URL in URLz:
                    print(f'formatting URL:{URL}')
                    formatted = "https://th.bing.com/th/id/OIG."+URL
                    print(f'formated URL:{formatted}')
                    append_string_to_file(formatted)
                    formatted_URLz.append(formatted)
                return _U, formatted_URLz
            time.sleep(2)
            timeout_left = timeout_temp - current_milliseconds()
            print(f"timeout left: {timeout_left}")
    return _U, None

import sys

import discord as discord

TOKEN = ""
def read_credentials(filename="credentials.txt"):
    global TOKEN
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith("DALLE3_DISCORD_TOKEN"):
                TOKEN = line.split("=")[1].strip().strip('"')
        if not TOKEN:
            raise ValueError("Incomplete credentials. Please check your credentials.txt file.")
    except Exception as e:
        print(f"Error reading credentials: {str(e)}")
        sys.exit(1)
read_credentials()
print(f"TOKEN:{TOKEN}")

intents = discord.Intents.none()
intents.messages = True
intents.message_content = True
import discord
from discord.ext import commands

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

import aiohttp

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to download image from {url} with status {resp.status}")
                return None
            res = await resp.read()
            print(f"Downloaded data from {url}: {res[:100]}...")  # Print first 100 bytes
            if isinstance(res, int):
                print(f"Unexpected int result from url {url}: {res}")
                return None
            return res
requests_in_flight = 0
@bot.event
async def on_message(message):
    global requests_in_flight
    if message.author == bot.user:
        return

    if (123123123 == message.channel.id) and message.content.lower().startswith('>dalle3 '):
        # Extract the next 480 characters or less as the prompt
        full_prompt = message.content[len('>dalle3 '):]
        if not full_prompt:
            await message.channel.send(f'Received empty prompt!')
        elif len(full_prompt) > 480:
            prompt = full_prompt[:480]
            last_20_char = prompt[-30:]
            await message.channel.send(f'Sorry your prompt is too long, max 480 char, cutoff at: ```{last_20_char}```proceeding with cutoff prompt...')
        else:
            prompt = full_prompt
        async with message.channel.typing():
            print(f'REQUESTS IN FLIGHT (prior to check):{requests_in_flight}')
            # Check if there's already a request in flight
            if requests_in_flight > 5:
                return await message.channel.send(f'{message.author.mention} busy ok wait for me 2 finish pl0x ty <3')
            requests_in_flight += 1
            _U, urls = None, None
            try:
                _U, urls = await make_images(prompt, message)
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                requests_in_flight -= 1
            if _U is None:
                return await message.channel.send(
                    f'{message.author.mention} Oops all out of cookies to use to request generations! 420x69x420 needs to make more accounts, or you can kindly donate your _U cookie, or wait 24 hours for token refresh :-)')
            if urls is None:
                if "RATE_LIMITED" in urls or "ACC_LOCKED" in urls:
                    add_blocked_timestamp(_U)
                    owner = search_entry(_U)['owner']
                    return await message.channel.send(
                        content=f'Owner: {owner} has been timed out temporarily due to unknown error in HTTP request process. Please retry your prompt.')

            if isinstance(urls, str):
                print(urls)
                if "NO_VALID_EVENT_ID" in urls:
                    return await message.channel.send(content=f'{message.author.mention} Something wrong with my own generation request process, blame 420x69x420...')
                if "UNSAFE_PROMPT" in urls:
                    files = [discord.File("IMAGE_BLOCKED.jpg")]
                    return await message.channel.send(content=f'{message.author.mention}', files=files)
                if "RATE_LIMITED" in urls or "ACC_LOCKED" in urls:
                    add_blocked_timestamp(_U)
                    owner = search_entry(_U)['owner']
                    return await message.channel.send(content=f'Owner: {owner} has been timed out temporarily. Please retry your prompt.')
                images_data = [await download_image(urls)]
            else:
                print([type(data) for data in urls])
                images_data = await asyncio.gather(*(download_image(url) for url in urls if url is not None))
            images_data = [data for data in images_data if data is not None]
            files = []
            for i, data in enumerate(images_data):
                if isinstance(data, bytes):
                    file = discord.File(io.BytesIO(data), filename=f"image{i}.jpg")
                    files.append(file)
                else:
                    print(f"Warning: Expecting bytes, got {type(data)} at index {i}")
            await message.channel.send(f'{message.author.mention}', files=files)


# Run the bot
bot.run(TOKEN)