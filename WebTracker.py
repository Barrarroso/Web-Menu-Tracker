import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

#TODO Refactor

#CONSTANTS
URL = "https://www.telepizza.es/productos/menus"
credentials = {}
with open('credentials.json','r') as f:
    credentials = json.load(f)
    f.close()

from_addr = credentials['from_addr']
to_addr = credentials['to_addr']
headers = {"User-Agent": credentials["User-Agent"]}
password = credentials['password']

#Saves dictionary onto a JSON file
def write_data(dict,json=json):
    json = json.dumps(dict)
    file = open("ofertas.json", "w+")
    file.write(json)
    file.close()
    return

#Reads previous saved dictionary and returns it
def read_data():
    file = open("ofertas.json","r")
    return json.load(file) #Returns dictionary

def send_email(menu, prev_price, now_price, imageSrc):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(from_addr,password)
    subject = "Precio bajado en: " + menu

    msg = MIMEText('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="text-align: center"><div style="background: #F2F2F2"><h1 style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:42px;line-height:50px;font-weight:700;letter-spacing:0;color:#4c4c4c">'+menu+'</h1><a href="'+URL+'" target="_blank" style="text-decoration: none"><img src="'+imageSrc+'" /></a><br><p style="font-family: fantasy;text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;font-size: 2em;color:#4c4c4c"><span style="color:#ff3d51">'+str(prev_price)+'€'+'</span> &#8594; <span style="color:#46fa70">'+str(now_price)+'€'+'</span></p><a href="'+URL+'" style="display:inline-block;width:100%;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;line-height:19px;letter-spacing:0.4px;color:#ffffff;text-align:center;text-decoration:none;background-color:#1cb0f6;border-radius:14px;border-top:12px solid #1cb0f6;border-bottom:12px solid #1cb0f6;text-transform:uppercase; width:30%" target="_blank">Ve a comprobarlo</a><br><br><br></div></body></html>','html','utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server.sendmail(from_addr,to_addr,msg.as_string())
    print("Email Sent")
    server.quit()

def check_price():
    print("Checking price")
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all("div", class_="mod_addable_product")
    titles = soup.find_all(class_="heading-m")
    images = soup.find_all(class_="promotion lazy")
    menus = {}
    images_and_menus = {}
    if len(titles)==len(divs): #Get menu titles
        for i in range(0, len(titles)):     #Creates a dictionary with the name of the product as Key and price as Value
            title = titles[i].get_text()
            priceText = divs[i].findChildren("h3",recursive=False)[0].get_text()
            price = float(priceText.replace(",",".")[:-1])
            menus[title] = price
            images_and_menus[title] = images[i]['data-src']

    prev_menus = read_data()
    for key, value in menus.items():
        if(menus[key]<prev_menus[key]):   #Sends email if the current price is lower than the previous one
            send_email(key,prev_menus[key],menus[key],images_and_menus[key])


    #Saves dictionary onto a JSON file
    write_data(menus)

while(True): #Checks price every 60 seconds
    check_price()
    time.sleep(60)
