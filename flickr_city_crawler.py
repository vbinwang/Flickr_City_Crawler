import requests
import json
import pandas as pd
import time
import multiprocessing as mp
import threading as td
import threadpool
import urllib
import flickrapi
from lxml import etree
import xlwt
from multiprocessing.dummy import Pool as ThreadPool
from geopy.geocoders import Nominatim

def flickrAPI():
    api_key=u'382e669299b2ea33fa2288fd7180326a'
    api_secret=u'b556d443c16be15e'
    flickr = flickrapi.FlickrAPI(api_key, api_secret,cache=True)
    return flickr
def places_find(text):
    flickr=flickrAPI()
    #获取位置ID
    places=flickr.places.find(query=text)
    for place in places[0]:
        placeID=place.attrib['place_id']
        return placeID
    

def flicker(city):
    
    lost=[]
    difdata=[]
    #address, (latitude, longitude)=geolocator.geocode(city)
    latitude='32.3942090'
    longitude='119.4129390'
    data = [
                ('page', '1'),
                ('per_page', '250'),
                #('place_id', placeid),
                ('lat',latitude),
                ('lon',longitude),
                ('radius','32'),
                ('sort', 'interestingness-desc'),
                ('extras', 'owner_name,geo,media'),
                ('format', 'json'),
                ('nojsoncallback', '1'),
                ('has_geo','1'),
                ('min_taken_date', '1970-01-01 00:00:00'),
                ('method', 'flickr.photos.search'),
                ('api_key', '184af065261f8af3da4c44597c9cc26e'),
                ('accuracy','11')]
    try:
        response = requests.post('https://api.flickr.com/services/rest', headers=headers, data=data).text
    except Exception as e:
        print(e)
    fli=json.loads(response)
    print(fli)
    total=fli['photos']['pages']
    #time.sleep(10)
    for i in range(1,total+1):
        data = [
                ('page', '%s'%i),
                ('per_page', '250'),
                #('place_id', placeid),
                ('lat',latitude),
                ('lon',longitude),
                ('radius','32'),
                ('sort', 'interestingness-desc'),
                ('extras', 'owner_name,geo,media'),
                ('format', 'json'),
                ('nojsoncallback', '1'),
                ('has_geo','1'),
                ('min_taken_date', '1970-01-01 00:00:00'),
                ('method', 'flickr.photos.search'),
                ('api_key', '184af065261f8af3da4c44597c9cc26e'),
                ('accuracy','11')]
        try:
            response = requests.post('https://api.flickr.com/services/rest', headers=headers, data=data).text
        except Exception as e:
            print(e)
            continue    
        fli=json.loads(response)
        if fli['stat']=='fail':
            lost.append(page)
            return fli
        else:
            # print(fli)
            data1=fli['photos']['photo']
            #print 
            #print(data1)
            print(city+'目前'+str(i)+',总共'+str(total))
            if not data1 or firstid==data1[0]['id']:
                print(city+'第一个一样，结束')
                return(difdata)
            else:
                firstid==data1[0]['id']
                for item in data1:
                    dif=[item['owner'],item['latitude'],item['longitude'],item['title'],item['id']]
                    try:
                        EXI=flickr.photos.getExif(photo_id=dif[4],format="json",nojsoncallback="true")
                    except Exception as e:
                        print(e)
                        continue
                    Exif=json.loads(EXI)
                    #print(Exif)
                    try:
                        Exif=Exif['photo']['exif']
                    except KeyError:
                        continue
                    #print(Exif)
                    m_time_i=next((x for x in Exif if x['label'] == 'Date and Time (Modified)'), None)
                    o_time_i=next((x for x in Exif if x['label'] == 'Date and Time (Original)'), None)
                    if m_time_i and o_time_i:
                        #print(dif)
                        try:
                            tag_url='https://api.flickr.com/services/rest?photo_id=%s&method=flickr.tags.getListPhoto&api_key=7411cde9e638660af0d3dc71a62afd48&format=json&hermes=1&hermesClient=1&nojsoncallback=1'%dif[4]
                            tag_text=requests.get(tag_url).text
                            #print(json.loads(tag_text))
                        except Exception as e:
                            print(e)
                            continue 
                        try:
                            tag_list=json.loads(tag_text)['photo']['tags']['tag']
                            #print(json.loads(tag_text))
                        except Exception as e:
                            print(e)
                            continue
                        tags=[]
                        if len(tag_list)>0:
                            for i in tag_list:
                                tags.append(i['_content'])
                        dif.append(','.join(tags))
                        dif.append(m_time_i['raw']['_content'])
                        dif.append(o_time_i['raw']['_content'])
                        difdata.append(dif)
                        #if len(difdata)%100==0:
                            #print(city+' 已经爬取了 '+str(len(difdata))+' 条')
    print('全部爬完，结束')
    return(difdata)
                    
def process(city):
    result=flicker(city)
    if result:
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet(city)
        head = ['owner name'	,'latitude',	'longitude','title','photo ID','tag','Date and Time (Modified)','Date and Time (Original)']
        for h in range(len(head)):
            sheet.write(0, h, head[h])
        j=1
        for x in result:
            for i in range(len(head)):
                sheet.write(j,i,x[i])
            j+=1
        workbook.save(city+'.xls')
        print(city+' 写入excel成功')
    else:
        f=open('不存在的城市','w+')
        f.write(city+'\n')    
        f.close()




if __name__ == '__main__':
    flickr = flickrAPI()
    FLICKR_API_KEY = '184af065261f8af3da4c44597c9cc26e'
    FLICKR_PLACE_FIND_URL = 'https://api.flickr.com/services/rest/?'
    geolocator = Nominatim()
    headers = {
    'origin': 'https://www.flickr.com',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'referer': 'https://www.flickr.com/map',
    'authority': 'api.flickr.com',
    'cookie': 'BX=19820o5dm3hq8&b=3&s=1c; xb=264136; localization=zh-hk%3Bus%3Bus; adCounter=6; flrbp=1533212999-ef8116da81c4a606156b0b0b039e873cf51629fb; flrbs=1533212999-b44e3db098c4df17c527fc3bdbc6a69813419694; flrbgrp=1533212999-121537547a9e7645251e87653f7a1824863e73e3; flrbgdrp=1533212999-27617076a577c01184c39035b5f8f3839b19fc26; flrbgmrp=1533212999-78d72d1fcc5b83f19ac8eac9e3a21378e7ef53a1; flrbcr=1533212999-13650ff4b6ce790be1a8802505e5b0592d30812a; flrbrst=1533212999-878d4ea9cafb1f5aa7e231eec6a0e7ddddaf1332; flrtags=1533212999-de92f2f35f1f11b81be4691497cbe3c5f619de7b; flrbrp=1533212999-a22791171a5d0ce72580a02a0c495b42dd96590b; flrb=29; RT=s=1533213211006&u=&r=https%3A//www.flickr.com/map; vp=929%2C847%2C2%2C15%2Ctag-photos-everyone-view%3A1344%2Cexplore-page-view%3A800',
    'dnt': '1',
    }
    firstid=0
    flickrAPI()
  
    pool = ThreadPool(12)
    cities=['上海','南京','无锡','常州','苏州','泰州','杭州','宁波','嘉兴','金华','舟山','合肥']
    #'芜湖','马鞍山','铜陵','安庆','滁州','池州','宣城''台州','湖州''绍兴','南通','盐城','扬州','镇江'
    #cities.reverse()
    pool.map(process,cities)
    pool.close()
    pool.join()   
 
        
        
