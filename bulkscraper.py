from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future
import threading
import time
import queue
import requests
from bs4 import BeautifulSoup
from json import dumps
from json import loads as load_json
from json import dump
from threading import Thread
from datetime import datetime

POOL_SIZE = 1
local_storage = threading.local()

SCRAPE_TIME_LIMIT = 10
CONTINUOUS_REQUEST = 3
SLEEPING_TIME_BETWEEN_REQUEST = 1

def call_with_future(fn, future, args, kwargs):
    try:
        result = fn(*args, **kwargs)
        future.set_result(result)
    except Exception as exc:
        future.set_exception(exc)

def threaded(fn):
    def wrapper(*args, **kwargs):
        future = Future()
        Thread(target=call_with_future, args=(
            fn, future, args, kwargs)).start()
        return future
    return wrapper

sql_lock = threading.Lock()
class BulkScraper() :
    
    def __init__(self, scrapeList, mainWindow, *args, **kwargs) :
                
        self.dataList = scrapeList
        self.window = mainWindow
        self.labelFlag = [0] * POOL_SIZE
        self.flagLock = threading.Lock()
        
    def scarpeWork(self, urlInfo, threadID) :
        try:
            # find empty label
            labelID = -1
            print(self.labelFlag)
            with self.flagLock:
                for i in range(POOL_SIZE) :
                    if self.labelFlag[i] == 0:
                        self.labelFlag[i] = 1
                        labelID = i
                        break
                    
            if labelID < 0 :
                print("Syncronize Error while: "+str(urlInfo[0]))
                return
            
            priceList = []
            self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1)+":Start scraping for url:'"+ urlInfo[1]+"' ")
            
            try:
                response = requests.get(urlInfo[1], timeout = SCRAPE_TIME_LIMIT)
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
                self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                self.labelFlag[labelID] = 0
                return
            except  requests.exceptions.Timeout :
                print("Request time out while scraping: " + urlInfo[1])
                self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                self.labelFlag[labelID] = 0
                return
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get Token
            hiddenInputs = soup.select('input[type=hidden]')
            
            param = {
                "token": '',
                "isIndividualQuantity": False,
                "categoryId": "",
                "shopId": "0", "userId": "0",
                "articleId": "",
                "substrateId": "498355",  # This is id for typ
                "quantity": "50",
                "priceScaleId": "15783758",  # This is id for Auflage
                "deliveryOption": "STANDARD_PRODUCTION",
                "keyword": "WmD--7dccecd3c1bb84233a8c5e9ae0660bd4",
                "voucherCode": ""
            }
            
            for input in hiddenInputs:
                if input.get('name') == '_token':
                    param['token'] = input['value']
                if input.get('name') == 'categoryId':
                    param['categoryId'] = str(input['value'])
                if input.get('name') == 'c':
                    param['articleId'] = input['value']
                    
            param["deliveryOption"] = urlInfo[4]
            param['substrateId'] = urlInfo[2]
            
            stopPoint = urlInfo[5]
            if stopPoint == "" or int(stopPoint) == None :
                stopPoint = -1
            else :
                stopPoint=int(stopPoint)
            
            # Request post to get Auflage options
            post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-sorten-auflage"
            
            try :
                response = requests.post(post_url, json=param, allow_redirects=False, timeout= SCRAPE_TIME_LIMIT)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
                self.labelFlag[labelID] = 0
                return
            except requests.exceptions.Timeout :
                print("Request time out while scraping auflage options for: " + urlInfo[1])
                self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                self.labelFlag[labelID] = 0
                return
            
            auflage_data = load_json(response.text)
            auflageList = auflage_data['data']['response']
            
            # result = []
            cnt = 0
            
            session = requests.Session()
            for auflageOption in auflageList:
                
                if param['deliveryOption'] == 'STANDARD_PRODUCTION' :
                    if stopPoint > 0 and auflageOption['wert'] > stopPoint :
                        break
                    priceList.append((auflageOption['wert'], auflageOption['preis']))
                    continue
                
                # self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1)+":Scraping price for "+str(urlInfo[0])+"_"+urlInfo[3] + "("+urlInfo[4]+") wert:"+str(auflageOption['wert']))
                self.window.scrapeThreadLabel[labelID].configure(text=str(urlInfo[0])+" - "+str(auflageOption['wert'])+" - "+urlInfo[3] + "("+urlInfo[4]+") wert:") 

                # Get option data
                param['priceScaleId'] = str(auflageOption['id'])
                param['quantity'] = auflageOption['wert']

                post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-options"
                
                try :
                    response = session.post(
                        url = post_url,
                        data = dumps(param),
                        timeout = SCRAPE_TIME_LIMIT
                    )
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(f"HTTP error occurred: {err}")
                    self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                    self.labelFlag[labelID] = 0
                    return
                except requests.exceptions.Timeout :
                    print("Request time out while scraping option data for: " + urlInfo[1])
                    self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                    self.labelFlag[labelID] = 0
                    return
                
                option_data = load_json(response.text)

                optionsList = option_data['data']['response']
                flag = True
                deliveryOptionsList = optionsList['deliveryOptionsField']
                for option in deliveryOptionsList :
                    if hasattr(deliveryOptionsList, 'append') :
                        optionVal = option
                    else:
                        optionVal = deliveryOptionsList[option]
                    if urlInfo[4] in optionVal['bezeichnung'] :
                        param['deliveryOption'] = str(optionVal['id'])
                        flag = False
                if flag:
                    break

                # Get Price Data
                post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-price"
                
                try :
                    response = requests.post(post_url, json=param, allow_redirects=False, timeout=SCRAPE_TIME_LIMIT)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(f"HTTP error occurred: {err}")
                    self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                    self.labelFlag[labelID] = 0
                    return
                except requests.exceptions.Timeout :
                    print("Request time out while scraping price data for: " + urlInfo[1])
                    self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                    self.labelFlag[labelID] = 0
                    return
                
                auflage_data = load_json(response.text)
                auflage_data = auflage_data['data']['response']
                
                if auflage_data['deliveryCharge'] == None :
                    break
                
                if stopPoint > 0 and auflageOption['wert'] > stopPoint :
                    break

                price = float(auflage_data['price']) - float(auflage_data['shippingCost'])
                priceList.append((auflageOption['wert'], price))
                cnt = cnt + 1
                if cnt % CONTINUOUS_REQUEST == 0 :
                    time.sleep(SLEEPING_TIME_BETWEEN_REQUEST)
            
            self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1)+":Scraping Finished ")
            
            # Write the scraping time in db
            timeString = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            query = f"""
                    UPDATE tbl_url_list
                    SET last_scrape="{timeString}"
                    WHERE id = {urlInfo[0]}
                    """
            sql_lock.acquire()
            try :
                self.window.scrapeDB.query(query)
            finally :
                sql_lock.release()
            
            for row in self.window.urlListTable.get_rows() :
                if row.values[0] == urlInfo[0]:
                    temp = row.values
                    temp[12] = timeString
                    row.values = temp
        
            # Merge pricelist to the db
            self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID)+":Merging price data...")
            
            print(urlInfo)
            itemId = urlInfo[6]
            ftypeId = urlInfo[8]
            inkTypeId = urlInfo[10]
            densityTypeId = urlInfo[12]
            productTimeId = urlInfo[14]
            
            query = f"""
            SELECT ipr.count, ipptr.sum
            FROM item_price_product_time_rows ipptr
            INNER JOIN item_price_rows ipr ON ipptr.item_price_row_id = ipr.id
            INNER JOIN item_prices ip ON ipr.item_price_id = ip.id
            WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} AND ipptr.product_time_id = {productTimeId}
            ORDER BY ipr.count
            """
            mysqlData = self.window.sql.query(query).result()
            
            exportData = []
            priceList = sorted(priceList, key = lambda tpl: float(tpl[0]))
            
            if len(priceList) == 0:
                print("Error: No Price list-" + str(urlInfo[0]))
                self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                self.labelFlag[labelID] = 0
                return
            
            if len(mysqlData) == 0:
                print("Error: No SQL Data-" + str(urlInfo[0]))
                self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID + 1))
                self.labelFlag[labelID] = 0
                return
            
            exportData = priceList
            
            rate = float(priceList[-1][1]) / int(priceList[-1][0])
            for sqlData in mysqlData :
                flag = False
                for data in priceList:
                    if int(data[0]) == int(sqlData[0]) :
                        flag = True
                        break
                    if int(data[0]) > int(sqlData[0]) :
                        flag = True
                        exportData.append((sqlData[0], data[1]))
                        break
                    
                if flag :
                    continue
                exportData.append((sqlData[0], rate * int(sqlData[0])))
                
            exportData = sorted(exportData, key = lambda tpl: float(tpl[0]))
            self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID)+":Exporting to sql database...")
            
            workDay = urlInfo[16]
            coeff = urlInfo[17]
            
            limitExport = int(urlInfo[20])
            # Find ID of item.
            
            query = f"""
                    SELECT ip.id
                    FROM item_prices ip 
                    
                    WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId}
                    """
                    
            itemPriceID = self.window.sql.query(query).result()
            itemPriceID = itemPriceID[0][0]
            print(itemPriceID)
            
            for exp in exportData :
                if limitExport > 0 and exp[0] > limitExport :
                    continue
                
                query = f"""
                    SELECT ipr.id, ipr.count
                    FROM item_price_rows ipr
                    
                    WHERE ipr.item_price_id = {itemPriceID} AND ipr.count={exp[0]}
                    """
                itemCountList = self.window.sql.query(query).result()
                                
                insertID = -1
                updateFlag = False
                
                if itemCountList == None or len(itemCountList) == 0 : # No Count Data, Create Count Record in item_price_rows table
                    query = f"""
                        INSERT INTO item_price_rows (item_price_id, count) 
                        VALUES({itemPriceID}, {exp[0]})
                    """

                    insertID = self.window.sql.insert_query(query).result()
                else :
                    insertID = itemCountList[0][0]
                    # Find the id of price
                    query = f"""
                        SELECT ipptr.id
                        FROM item_price_product_time_rows ipptr
                        
                        WHERE ipptr.item_price_row_id = {insertID} AND ipptr.product_time_id={productTimeId}
                        """
                    itemPriceList = self.window.sql.query(query).result()
                    # print("Item price :" + str(itemPriceList))
                    if itemPriceList != None and len(itemPriceList) > 0 :
                        updateFlag = True
                        itemUpdateID = itemPriceList[0][0]
                
                # print("Insert ID:" + str(insertID))

                if updateFlag == False : # Create count and value
                    
                    query = f"""
                        INSERT INTO item_price_product_time_rows (item_price_row_id, product_time_id, sum, coefficient, work_day)
                        VALUES({insertID}, {productTimeId}, {exp[1]}, {coeff}, '{workDay}') 
                    """
                    self.window.sql.insert_query(query).result()

                else: # Update count and value
                    query = f"""
                        UPDATE item_price_product_time_rows ipptr

                        SET ipptr.sum={exp[1]}, ipptr.coefficient={coeff}, ipptr.work_day='{workDay}'
                        WHERE ipptr.id={itemUpdateID}
                        """
                    
                    ret = self.window.sql.query(query).result()
                        
            # Write the scraping time in db
            timeString = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            query = f"""
                    UPDATE tbl_url_list
                    SET last_export="{timeString}"
                    WHERE id = {urlInfo[0]}
                    """
            

            self.window.scrapeDB.query(query)
                
            for row in self.window.urlListTable.get_rows() :
                if row.values[0] == urlInfo[0]:
                    temp = row.values
                    temp[13] = timeString
                    row.values = temp
            self.window.scrapeThreadLabel[labelID].configure(text="Thread "+str(labelID)+":Completed exporting to sql database...")
            self.labelFlag[labelID] = 0
        except Exception as e:
            print(e)
            
            
    @threaded
    def startBulkScrape(self) :
            
        with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
            i = 0
            for scrapeInfo in self.dataList:
                thread_index = i % POOL_SIZE
                labelWnd = self.window.scrapeThreadLabel[thread_index]
                executor.submit(self.scarpeWork, scrapeInfo, thread_index)
                i = i + 1