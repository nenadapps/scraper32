from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
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
        stamp['raw_text'] = raw_text
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
        stamp['raw_text'] = stamp['title']

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

categories = get_categories()
for category_name in categories:
    category = categories[category_name]
    page_items = get_page_items(category)
    for page_item in page_items:
        stamp = get_details(page_item, category_name)

