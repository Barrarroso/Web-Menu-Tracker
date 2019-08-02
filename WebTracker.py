import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

#TODO Better HTML Design

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

    msg = MIMEText('<!DOCTYPE html><html><body><p>Mira el link: '+ URL +'</p><img src="'+imageSrc+'" /><br><br><p> Ha pasado de: ' + str(prev_price) + '€' + ' a: ' + str(now_price) + '€' + '</p></body></html>','html','utf-8')
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
