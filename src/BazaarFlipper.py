import requests
import pandas as pd
import time
from datetime import datetime
import random
from email.message import EmailMessage
import ssl
import smtplib
from csv import writer
from dotenv import dotenv_values

DOTENV_FILE_PATH = r".config\email_credentials.env"
CONFIG = dotenv_values(DOTENV_FILE_PATH)

WAIT_TIME = 600
TARGET_SELL_PRICE = 8500000
TARGET_BUY_PRICE = 7100000

data = []
previous_emails_timestamps = []

def email(subject, body):
    email_sender = CONFIG['email_sender']
    email_password = CONFIG['email_password']
    email_receiver = CONFIG['email_receiver']

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

while True:
    start_time = datetime.now()
    try: 
       bazaar_dataframe = pd.DataFrame(requests.get("https://api.hypixel.net/skyblock/bazaar").json())['products']
    except:
        print("there was an exception here")
        time.sleep(random.randint(90, 120)) #the random element in here is just in case hypixel flags me as a bot for requesting in even time intervals
        continue

    # bazaar_dataframe = pd.DataFrame(requests.get("https://api.hypixel.net/skyblock/bazaar").json())['products']
    lowest_sell_order = bazaar_dataframe["BOOSTER_COOKIE"]["buy_summary"][0]["pricePerUnit"]
    print(datetime.today().strftime("%d/%m %H:%M:%S"))
    print(f"Lowest Sell Order: ${'{:,}'.format(lowest_sell_order)}\n")
    data.append([lowest_sell_order, datetime.today().strftime("%d/%m %H:%M:%S")])

    # save data in .csv file
    with open('booster_cookie_data.csv', 'a', newline = '') as f:
        writer_object = writer(f)
        writer_object.writerow(data[-1])
        f.close()

    #the below checks if the price is in the target range, and if so it sends me an email
    #it also makes sure that a maximum of one email is getting sent a day
    if lowest_sell_order > TARGET_SELL_PRICE or lowest_sell_order < TARGET_BUY_PRICE:
        if previous_emails_timestamps == [] or previous_emails_timestamps[-1] != datetime.now().strftime("%d/%m/%Y"):
            subject = 'Auction Flipper Msg'
            body = f"booster cookie price is in the target range.\nLowest Sell Order: ${'{:,}'.format(lowest_sell_order)}"
            email(subject, body)
            previous_emails_timestamps.append(datetime.now().strftime("%d/%m/%Y"))
    
    time_taken = (datetime.now() - start_time).total_seconds()
    if time_taken <= WAIT_TIME:
        time.sleep(WAIT_TIME - time_taken)