#!/usr/bin/env python
# coding: utf-8

import json
import os
import re
import shutil
import sys
import time
from datetime import datetime

from discord.ext import commands
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, WebDriverException  # noqa
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

load_dotenv()

HELPER_TOKEN = os.environ['HELPER_TOKEN']  # Your Discord user token

CHANNEL_LINK = 'https://discord.com/channels/1002292111942635562/1002292809014980738'  # noqa

CHROMEDRIVER_EXEC = shutil.which('chromedriver')
if not CHROMEDRIVER_EXEC:
    if not os.getenv('CHROMEDRIVER_EXEC'):
        sys.exit(
            'Could not find chromedriver in your path. Export it as an '
            'environment variable: `CHROMEDRIVER_EXEC=/path/to/chromedriver`!')
    else:
        CHROMEDRIVER_EXEC = os.environ['CHROMEDRIVER_EXEC']

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--mute-audio')
options.add_argument('--start-maximized')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

if os.getenv('CHROME_BIN'):
    options.binary_location = os.getenv('CHROME_BIN')

service = Service(CHROMEDRIVER_EXEC)
try:
    driver = webdriver.Chrome(options=options, service=service)
except WebDriverException:
    if os.getenv('CHROME_BIN'):
        options.binary_location = os.getenv('CHROME_BIN')
        driver = webdriver.Chrome(options=options, service=service)
    else:
        sys.exit('Could not find Chrome binary. Export it as an environment '
                 'variable: `CHROME_BIN=/path/to/Chrome`!')

driver.get('https://discord.com/login')
driver.execute_script("let token =\"" + HELPER_TOKEN + """\";
            function login(token) {
            setInterval(() => {
                  document.body.appendChild(
                  document.createElement `iframe`
                  ).contentWindow.localStorage.token = `"${token}"`
                }, 50);
                setTimeout(() => {
                  location.reload();
                }, 2500);
             }
            login(token);""")

time.sleep(8)
driver.get(CHANNEL_LINK)
time.sleep(5)
elms = driver.find_elements(By.TAG_NAME, 'li')

try:
    inbox_button = driver.find_element(
        By.XPATH,
        '/html/body/div[1]/div[2]/div/div[1]/div/div[2]/div/div[1]/div/div/'
        'div[3]/section/div[2]/div[6]').click()
except NoSuchElementException:
    elms = driver.find_elements(By.TAG_NAME, 'div')
    inbox_button = [
        e for e in elms if e.get_attribute('aria-label') == 'Inbox'
    ][0].click()

time.sleep(2)

inbox = driver.find_element(
    By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div/div/div/div[2]/div[1]')

inbox.find_element(
    By.XPATH,
    '/html/body/div[1]/div[2]/div/div[3]/div/div/div/div[1]/div[2]/div').click(
    )

inbox_filter = inbox.find_element(
    By.XPATH, '/html/body/div[1]/div[2]/div/div[3]/div[2]')

include_everyone = inbox_filter.find_element(By.ID, 'mentions-filter-Everyone')
if include_everyone.get_attribute('aria-checked') == 'true':
    include_everyone.click()
time.sleep(1)

include_all_servers = inbox_filter.find_element(By.ID,
                                                'mentions-filter-All Servers')
if include_all_servers.get_attribute('aria-checked') == 'true':
    include_all_servers.click()
time.sleep(1)

inbox_messages = []
for e in inbox.find_elements(By.TAG_NAME, 'div'):
    try:
        if e.get_attribute('role') == 'article':
            inbox_messages.append(e)
    except StaleElementReferenceException:
        continue

output = []
for message in inbox_messages:
    image_container = message.find_elements(By.TAG_NAME, 'div')
    if 'DreamBotMothership' not in message.text:
        continue
    for e in image_container:
        try:
            url = e.find_element(By.TAG_NAME, 'a').get_attribute('href')
            filler = 'Message could not be loaded.\n'
            output.append([message.text.replace(filler, ''), url])
        except NoSuchElementException:
            continue

data = []
for response, url in output:
    out = response.split('\n')
    now = datetime.now()
    try:
        timestamp = datetime.strptime(' '.join(out[2].split(' ')[2:]),
                                      '%I:%M %p').replace(year=now.year,
                                                          month=now.month,
                                                          day=now.day)
    except ValueError:
        timestamp = datetime.strptime(out[2], '%m/%d/%Y')
    took = re.search(r'\d+.\d+s', out[3])[0]
    prompt = '!dream '.join(out[3].split('!dream')[1:]).strip()
    commands = out[5:]
    d = {
        'timestamp': str(timestamp),
        'took': took,
        'prompt': prompt,
        'commands': commands,
        'url': url
    }
    data.append(d)

# Export as JSON
with open('data.json', 'w') as j:
    json.dump(data, j, indent=4)

driver.quit()
