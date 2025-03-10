import requests
from bs4 import BeautifulSoup
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from json import dumps
from json import loads as load_json
from json import dump
from threading import Thread
from concurrent.futures import Future
import time

def call_with_future(fn, future, args, kwargs):
    try:
        result = fn(*args, **kwargs)
        future.set_result(result)
    except Exception as exc:
        future.set_exception(exc)

def threaded(fn):
    def wrapper(*args, **kwargs):
        future = Future()
        Thread(target=call_with_future, args=(fn, future, args, kwargs)).start()
        return future
    return wrapper

class ScrapClass:
    param = {
        "token": "",
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

    typIdList = []
    stopFlag = True

    def reset(self):
        self.typIdList = []
        self.stopFlag = True

    @threaded
    def getTypeData(self, window):
        try:
            result = {}
            csv_result = []
            window.fetchUrlButton.configure(state="disabled")

            window.typeMenu.delete(0, window.typeMenu.index('end'))
            window.scrapeTypes.set("")

            if window.url_entry.get() == "":
                return

            try:
                response = requests.get(window.url_entry.get(), headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                Messagebox.show_error("Error while scraping URL with requests. Please confirm URL.", "Error")
                print(f"Error: {e}")
                return

            hiddenInputs = soup.select('input[type=hidden]')
            for input in hiddenInputs:
                if input.get('name') == '_token':
                    self.param['token'] = input['value']
                if input.get('name') == 'c':  # Artikel-ID
                    self.param['articleId'] = input['value']
                if input.get('name') == 'categoryId':  # Kategorie-ID
                    self.param['categoryId'] = input['value']

            print(f"Abgerufenes Token: {self.param['token']}")
            print(f"Abgerufenes ArticleId: {self.param['articleId']}")
            print(f"Abgerufenes CategoryId: {self.param['categoryId']}")

            sorten_dropdown = soup.find('select', {'id': 'sorten'})
            if not sorten_dropdown:
                print("Dropdown nicht gefunden.")
                return

            sorten_options = sorten_dropdown.find_all('option')

            for sorten_option in sorten_options:
                window.typeMenu.add_radiobutton(
                    label=sorten_option.text, value=sorten_option['value'], variable=window.scrapeTypes,
                    command=lambda txt=sorten_option.text: window.setScrapeTypeText(txt)
                )

            window.fetchUrlButton.configure(state="enabled")
        except Exception as e:
            print(f"Fehler beim Abrufen der Typ-Daten: {e}")


    
    @threaded
    def getOptionsId(self, window, edition, scrapeType):
        try:
            # Get option data
            self.param['priceScaleId'] =edition
            self.param['substrateId'] = scrapeType

            post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-options"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Origin": "https://www.wir-machen-druck.de",
                "Referer": "https://www.wir-machen-druck.de/"
            }

            print(f"API-Parameter: {self.param}")

            response = requests.post(post_url, json=self.param, headers=headers, allow_redirects=False)

            if response.status_code != 200 or not response.text.strip():
                print("Fehlerhafte oder leere Antwort erhalten.")
                return

            
            option_data = load_json(response.text)

            optionsList = option_data['data']['response']['deliveryOptionsField']

            selectedOption = window.express_option.get()
            if selectedOption == "STANDARD_PRODUCTION":
                return selectedOption

            if isinstance(optionsList, dict):
                optionsList = optionsList.values()
            # Dynamically create radio buttons
            for idx, option in enumerate(optionsList):
                bezeichnung = option['bezeichnung']
                if selectedOption in bezeichnung:
                    return option['id']
            return -1
        except Exception as e:
            print(f"Fehler beim Scraping: {e}")

    @threaded
    def getPrice(self, window, edition, scrapeType, optionId, quantity):
        try:
            # Get option data
            self.param['priceScaleId'] =edition
            self.param['substrateId'] = scrapeType
            self.param['deliveryOption'] = optionId
            self.param['quantity'] = quantity

            post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-price"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Origin": "https://www.wir-machen-druck.de",
                "Referer": "https://www.wir-machen-druck.de/"
            }

            print(f"API-Parameter: {self.param}")

            response = requests.post(post_url, json=self.param, headers=headers, allow_redirects=False)

            if response.status_code != 200 or not response.text.strip():
                print("Fehlerhafte oder leere Antwort erhalten.")
                return 0

            
            price_data = load_json(response.text)

            price_data = price_data['data']['response']
            return price_data['price']+price_data['currency']

        except Exception as e:
            print(f"Fehler beim Scraping: {e}")

    @threaded
    def startScrap(self, window):
        try:
            self.stopFlag = False

            window.startScrapButton.configure(state="disabled")
            window.stopScrapButton.configure(state="enabled")
            window.scrapeTable.delete_rows()

            self.param["deliveryOption"] = window.express_option.get()
            self.param['substrateId'] = window.scrapeTypes.get()

            stopPoint = window.stopCntInput.get()
            stopPoint = int(stopPoint) if stopPoint.isdigit() else -1

            if not self.param['articleId'] or not self.param['substrateId'] or not self.param['quantity'] or not self.param['categoryId']:
                print("Ungültige Parameter: Anfrage wird nicht gesendet.")
                return

            post_url = "https://www.wir-machen-druck.de/wmdrest/article/get-sorten-auflage"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Origin": "https://www.wir-machen-druck.de",
                "Referer": "https://www.wir-machen-druck.de/"
            }

            print(f"API-Parameter: {self.param}")

            response = requests.post(post_url, json=self.param, headers=headers, allow_redirects=False)

            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code != 200 or not response.text.strip():
                print("Fehlerhafte oder leere Antwort erhalten.")
                return

            try:
                auflage_data = load_json(response.text)
            except Exception as e:
                print(f"JSON-Parsing fehlgeschlagen: {e}")
                return

            auflageList = auflage_data.get('data', {}).get('response', [])

            window.scrapeData = []
            for auflageOption in auflageList:
                if self.stopFlag:
                    return
                if stopPoint > 0 and auflageOption['wert'] > stopPoint:
                    break
                selectedOption = window.express_option.get()
                if selectedOption == "STANDARD_PRODUCTION":
                    window.scrapeData.append((auflageOption['wert'], auflageOption['preis']))
                else:
                    editionId = auflageOption['id']
                    optionId = self.getOptionsId(window, editionId, self.param['substrateId']).result()
                    quantity = auflageOption['wert']
                    price = self.getPrice(window, editionId, self.param['substrateId'], optionId, quantity).result()
                    window.scrapeData.append((auflageOption['wert'], price))

            window.scrapeTable.delete_rows()
            for data in window.scrapeData:
                window.scrapeTable.insert_row(values=data)
            window.scrapeTable.load_table_data()

            window.startScrapButton.configure(state="enabled")
            window.stopScrapButton.configure(state="disabled")
        except Exception as e:
            print(f"Fehler beim Scraping: {e}")

    def stopScrap(self, window):
        self.reset()
        window.startScrapButton.configure(state="enabled")
        window.stopScrapButton.configure(state="disabled")
