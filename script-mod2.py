# bstamps
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

from fake_useragent import UserAgent
import os
import sqlite3
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks
import requests

controller = Controller.from_port(port=9051)
controller.authenticate()

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')
hdr = {'User-Agent': UA.random}
#hdr = {'User-Agent': 'Mozilla/5.0'}

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers=hdr)
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url, category):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('#MainContentPlaceHolder_PriceText')[0].get_text().strip()
        stamp['price'] = price.replace('£', '').replace(',', '').strip()
    except: 
        stamp['price'] = None
        
    try:
        title = html.select('#MainContentPlaceHolder_StampTitle')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None
    
    try:
        cat_price = html.select('#MainContentPlaceHolder_SGText')[0].get_text().strip()
        stamp['cat_price'] = cat_price.replace('£', '').replace(',', '').strip()
    except:
        stamp['cat_price'] = None    
        
    try:
        condition = html.select('#MainContentPlaceHolder_ConditionText')[0].get_text().strip()
        stamp['condition'] = condition
    except:
        stamp['condition'] = None
        
    try:
        cat_num = html.select('#MainContentPlaceHolder_CatText')[0].get_text().strip()
        stamp['cat_num'] = cat_num
    except:
        stamp['cat_num'] = None      
        
    try:
        year = html.select('#MainContentPlaceHolder_YearText')[0].get_text().strip()
        stamp['year'] = year
    except:
        stamp['year'] = None   
        
    try:
        raw_text = html.select('#MainContentPlaceHolder_DescriptionText')[0].get_text().strip()
        stamp['raw_text'] = raw_text.replace('"',"'")
    except:
        stamp['raw_text'] = None          
        
    stamp['category'] = category   

    stamp['currency'] = "GBP"

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.find_all('img', {'style': 'float:left;max-width:100%;'})
        for image_item in image_items:
            img = 'https://www.bcstamps.co.uk/' + image_item.get('src')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title'].replace('"',"'")

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):
    
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item_cont in html.select('.icontable'):
            item_link_href = item_cont.select('a')[0].get('href')
            item_link = 'https://www.bcstamps.co.uk/' + item_link_href
            if item_link not in items:
                items.append(item_link)
                
        if not items:
            for item in html.select('#MainContentPlaceHolder_ItemSplash a'):
                item_href = item.get('href')
                if 'item-' in item_href:  
                    item_link = 'https://www.bcstamps.co.uk/' + item_href
                    if item_link not in items:
                        items.append(item_link)
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items

def get_categories():
    
    url = 'https://www.bcstamps.co.uk/full-list.html'
    
    items = {}

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('#centercontent p a'):
            item_link = 'https://www.bcstamps.co.uk/' + item.get('href')
            item_name = item.get_text().strip()
            if item_link not in items: 
                items[item_name] = item_link
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    print (file_name)
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM bcstamps WHERE {cn} == "{un}" AND {cn2} == "{un2}"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        try:
            conn1.commit()
            conn1.close()
        except:
            conn1.commit()
            conn1.close()
        print (" ")
        sleep(randint(10,45))
        next_step = 'continue'
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        try:
            conn2.commit()
            conn2.close()
        except:
            conn2.commit()
            conn2.close()
        next_step = 'pass'
    print("Price Updated")
    return(next_step)

def db_update_image_download(stamp): 
    req = requests.Session()
    directory = "/Volumes/Stamps/stamps/bcstamps/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    names = file_names(stamp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    image_paths = [directory + names[i] for i in range(len(names))]
    for item in range(0,len(names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=60, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=60, stream=True)
        if imgRequest1.status_code==200:
            with open(names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    database_update =[]
    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['cat_num'],
        stamp['condition'],
        stamp['year'],
        stamp['category'],
        stamp['cat_price'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO bcstamps ('url','raw_text', 'title','cat_num',
    'condition','year','category','cat_price','scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", database_update)
    try:
        conn.commit()
        conn.close()
    except:
        conn.commit()
        conn.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(45,140)) 

connectTor()
count = 0

categories = get_categories()
for category_name in categories:
    category = categories[category_name]
    page_items = get_page_items(category)
    for page_item in page_items:
        count += 1
        if count > randint(100, 256):
            print('Sleeping...')
            sleep(randint(600, 4000))
            hdr['User-Agent'] = UA.random
            renew_tor()
            connectTor()
            count = 0
        else:
            pass
        stamp = get_details(page_item, category_name)
        if stamp['price']==None or stamp['price']=='':
            sleep(randint(500,700))
            continue
        next_step = query_for_previous(stamp)
        if next_step == 'continue':
            print('Only updating price')
            continue
        elif next_step == 'pass':
            print('Inserting the item')
            pass
        else:
            break
        db_update_image_download(stamp)
print('Scrape Complete')
