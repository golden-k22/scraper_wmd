import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import re
from json import dumps, loads as load_json, dump
import csv
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import validator, add_numeric_validation, add_regex_validation
from scraper import ScrapClass
from sqldb import SqlManager
from concurrent.futures import Future
from ttkbootstrap.dialogs.dialogs import Messagebox
from bulkscraper import *

PRICE_DB = "c1lsd"
# PRICE_DB = "c1w21db1"
URL_DB = "scrapelistdb"
POOL_SIZE = 4


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


class WorkspaceWindow(tk.Tk):
    scrapeData = []
    mysqlData = []
    exportData = []
    extraScaleData = []
    urlList = []

    def __init__(self, *args, **kwargs):
        self.scraper = ScrapClass()
        tk.Tk.__init__(self, *args, **kwargs)
        self.scrapeTypes = tk.StringVar()
        self.itemValues = tk.StringVar()
        self.formatTypeValues = tk.StringVar()
        self.inkTypeValues = tk.StringVar()
        self.densityTypeValues = tk.StringVar()
        self.productTimeValues = tk.StringVar()

        self.wm_title("Scraping Envelope")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.minsize(500, 200)

        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Make the frame fill the entire window
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, pad=5)
        main_frame.grid_rowconfigure(1, pad=5)

        # Create Scraper interface
        scrapeFrame = ttk.LabelFrame(main_frame, text="1.Scraper")
        scrapeFrame.grid(row=0, column=0, sticky="NSWE")
        scrapeFrame.grid_columnconfigure(0, weight=1)
        scrapeFrame.grid_columnconfigure(1, weight=3)
        scrapeFrame.grid_columnconfigure(2, weight=1)
        scrapeFrame.grid_rowconfigure(0, pad=5)

        ttk.Label(scrapeFrame, text="URL:").grid(
            row=0, column=0, sticky="W", padx=5)
        self.url_entry = ttk.Entry(scrapeFrame)
        self.url_entry.insert(
            0, "https://www.wir-machen-druck.de/postkarten-235-cm-x-125-cm.html")
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="WE")
        self.fetchUrlButton = ttk.Button(
            scrapeFrame, text="Verbinden", command=lambda: self.scraper.getTypeData(self))
        self.fetchUrlButton.grid(
            row=0,
            column=3,
            sticky="WE",
            padx=(5, 5))

        # Create Typ Select Widget
        ttk.Label(scrapeFrame, text="Typ:").grid(
            row=1, column=0, sticky="W", padx=5)

        self.typeSelector = ttk.Menubutton(scrapeFrame, text="Select Format Type", width=60)
        self.typeSelector.grid(
            row=1, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.typeMenu = tk.Menu(self.typeSelector)
        self.typeSelector['menu'] = self.typeMenu

        self.express_option = tk.StringVar()
        # Create Option Check for time
        ttk.Label(scrapeFrame, text="Production time:").grid(
            row=2, column=0, sticky="W", pady=5, padx=5)
        ttk.Radiobutton(scrapeFrame, text="Planmäßige", value="STANDARD_PRODUCTION",
                        variable=self.express_option).grid(row=2, column=1, sticky="WE")
        ttk.Radiobutton(scrapeFrame, text="48h-Express", value="48h",
                        variable=self.express_option).grid(row=2, column=2, sticky="WE")
        ttk.Radiobutton(scrapeFrame, text="24h-Express", value="24h",
                        variable=self.express_option).grid(row=2, column=3, sticky="WE", padx=5)

        self.express_option.set("STANDARD_PRODUCTION")

        ttk.Label(scrapeFrame, text="Stop Count Pieces:").grid(
            row=3, column=0, sticky="WE", padx=5)
        self.stopCntInput = ttk.Entry(scrapeFrame)
        self.stopCntInput.grid(
            row=3, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        add_numeric_validation(self.stopCntInput, when="key")

        self.startScrapButton = ttk.Button(
            scrapeFrame, text="Start scrape", command=lambda: self.scraper.startScrap(self))
        self.startScrapButton.grid(
            row=4, column=1, padx=(15, 0), sticky="WE", pady=5)
        self.stopScrapButton = ttk.Button(
            scrapeFrame, text="Stop scrape", state="disabled", command=lambda: self.scraper.stopScrap(self))
        self.stopScrapButton.grid(row=4, column=2, padx=(15, 0), sticky="WE")
        self.resetScrapButton = ttk.Button(scrapeFrame, text="Reset", command=self.resetAll)
        self.resetScrapButton.grid(row=4, column=3, padx=(15, 5), sticky="WE")

        # Interface of Lettershop Database

        sqlFrame = ttk.LabelFrame(main_frame, text="2. Lettershop Database")
        sqlFrame.grid(row=1, column=0, sticky="NSWE")
        sqlFrame.grid_rowconfigure(0, pad=5)
        sqlFrame.grid_columnconfigure(0, weight=1)
        sqlFrame.grid_columnconfigure(1, weight=3)

        ttk.Label(sqlFrame, text="Item:").grid(
            row=0, column=0, sticky="WE", pady="5", padx=5)
        self.itemSelector = ttk.Menubutton(sqlFrame, text="Select Item", width=50)
        self.itemSelector.grid(
            row=0, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.itemMenu = tk.Menu(self.itemSelector)
        self.itemSelector['menu'] = self.itemMenu

        ttk.Label(sqlFrame, text="Products:").grid(
            row=1, column=0, sticky="WE", pady="5", padx=5)
        self.typeListSelector = ttk.Menubutton(sqlFrame, text="Select Format Type", width=50)
        self.typeListSelector.grid(
            row=1, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.typeListMenu = tk.Menu(self.typeListSelector)
        self.typeListSelector['menu'] = self.typeListMenu

        ttk.Label(sqlFrame, text="Ink Type:").grid(
            row=2, column=0, sticky="WE", pady="5", padx=5)
        self.inkTypeSelector = ttk.Menubutton(sqlFrame, text="Select Ink Type", width=50)
        self.inkTypeSelector.grid(
            row=2, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.inkTypeMenu = tk.Menu(self.inkTypeSelector)
        self.inkTypeSelector['menu'] = self.inkTypeMenu

        ttk.Label(sqlFrame, text="Density Type:").grid(
            row=3, column=0, sticky="WE", pady="5", padx=5)
        self.densityTypeSelector = ttk.Menubutton(sqlFrame, text="Select Density Type", width=50)
        self.densityTypeSelector.grid(
            row=3, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.densityTypeMenu = tk.Menu(self.densityTypeSelector)
        self.densityTypeSelector['menu'] = self.densityTypeMenu

        ttk.Label(sqlFrame, text="Product Times:").grid(
            row=4, column=0, sticky="WE", pady="5", padx=5)
        self.productTimesSelector = ttk.Menubutton(sqlFrame, text="Select Product Times", width=50)
        self.productTimesSelector.grid(
            row=4, column=1, columnspan=3, sticky="WE", pady=5, padx=5)
        self.productTimesMenu = tk.Menu(self.productTimesSelector)
        self.productTimesSelector['menu'] = self.productTimesMenu

        ttk.Label(sqlFrame, text="Work Day:").grid(
            row=5, column=0, sticky="WE", padx=5)
        self.workDayInput = ttk.Entry(sqlFrame)
        self.workDayInput.grid(
            row=5, column=1, columnspan=3, sticky="WE", pady=5, padx=5)

        ttk.Label(sqlFrame, text="Coeff:").grid(
            row=6, column=0, sticky="WE", padx=5)
        self.coeffInput = ttk.Entry(sqlFrame)
        self.coeffInput.grid(
            row=6, column=1, columnspan=3, sticky="WE", pady=5, padx=5)

        ttk.Button(sqlFrame, text="Fetch Data from MySQL Database", command=self.fetchDataFromDB).grid(row=7, column=3,
                                                                                                       sticky="WE",
                                                                                                       padx=5)

        # Interface of scraping status

        self.scrapeThreadLabel = []

        bulkStatusFrame = ttk.LabelFrame(main_frame, text="5. Status of Bulk Scraping")
        bulkStatusFrame.grid(row=2, column=1, sticky="NSWE", padx=(15, 15))
        bulkStatusFrame.grid_rowconfigure(0, pad=5)
        bulkStatusFrame.grid_columnconfigure(0, weight=1)
        bulkStatusFrame.grid_columnconfigure(1, weight=3)

        i = 0
        while i < POOL_SIZE:
            label = ttk.Label(bulkStatusFrame, text="Thread " + str(i + 1) + ":", width="80")
            label.grid(row=i, column=0, sticky="WE", padx=5, pady=5)
            self.scrapeThreadLabel.append(label)
            i += 1

        # Interface of Extra
        extraFrame = ttk.LabelFrame(main_frame, text="3. Extra Option")
        extraFrame.grid(row=2, column=0, sticky="NSWE")
        extraFrame.grid_rowconfigure(0, pad=5)
        extraFrame.grid_columnconfigure(0, weight=1)
        extraFrame.grid_columnconfigure(1, weight=3)

        ttk.Label(extraFrame, text="Start Count & Value:").grid(row=0, column=0, sticky="WE", padx=5)
        self.extraCountEntry = ttk.Entry(extraFrame)
        self.extraCountEntry.grid(row=0, column=1, sticky="WE", padx=5, pady=5)
        add_numeric_validation(self.extraCountEntry, when="key")
        self.extraValueEntry = ttk.Entry(extraFrame)
        self.extraValueEntry.grid(row=0, column=2, sticky="WE", padx=5, pady=5)
        ttk.Button(extraFrame, text="Fetch", command=self.fetchCountFromValue).grid(row=0, column=3, sticky="WE",
                                                                                    padx=5, pady=5)

        ttk.Label(extraFrame, text="Stop Count Pieces:").grid(row=1, column=0, sticky="WE", padx=5)
        self.extraStopCountEntry = ttk.Entry(extraFrame)
        self.extraStopCountEntry.grid(row=1, column=1, columnspan=3, sticky="WE", padx=5, pady=5)
        add_numeric_validation(self.extraStopCountEntry, when="key")
        ttk.Button(extraFrame, text="Generate Extra Scale", command=self.generateScaleData).grid(row=2, column=3,
                                                                                                 sticky="WE", padx=5,
                                                                                                 pady=5)

        # Interface of Result Table
        exportFrame = ttk.LabelFrame(main_frame, text="4. Result Table")
        exportFrame.grid(row=0, column=1, sticky="NSWE", rowspan=2, padx=(15, 15))
        exportFrame.grid_rowconfigure(0, pad=5)
        exportFrame.grid_columnconfigure(0, weight=1)
        exportFrame.grid_columnconfigure(1, weight=3)

        coldata = [
            {"text": "Count", "stretch": True, "width": 70},
            {"text": "Price", "stretch": True, "width": 70},
        ]

        self.scrapeTable = Tableview(
            master=exportFrame,
            coldata=coldata,
            rowdata=self.scrapeData,
            bootstyle=PRIMARY,
            height=30,
        )
        self.scrapeTable.grid(row=0, column=0, padx=5)

        self.sqlTable = Tableview(
            master=exportFrame,
            coldata=coldata,
            rowdata=self.mysqlData,
            bootstyle=PRIMARY,
            height=30,
        )
        self.sqlTable.grid(row=0, column=1, padx=5)

        self.exportTable = Tableview(
            master=exportFrame,
            coldata=coldata,
            rowdata=self.exportData,
            bootstyle=PRIMARY,
            height=30
        )
        self.exportTable.grid(row=0, column=2, padx=5, columnspan=2)

        # Create Scrap and Export button

        ttk.Button(exportFrame, text="Merge", command=self.mergeData).grid(row=1, column=0, padx=(15, 0), sticky="WE",
                                                                           pady=5)
        ttk.Button(exportFrame, text="Export DB", command=self.exportDataToDatabase).grid(row=1, column=1, padx=(15, 0),
                                                                                          sticky="WE")
        ttk.Button(exportFrame, text="Export Scale", command=self.exportScaleDataToDB).grid(row=1, column=2,
                                                                                            padx=(15, 0), sticky="WE")

        # Create Bulk Scrap Part
        bulkScrapeFrame = ttk.LabelFrame(main_frame, text="4. Bulk Scrape")
        bulkScrapeFrame.grid(row=3, column=0, sticky="NSWE", columnspan=2, padx=(5, 5))
        bulkScrapeFrame.grid_rowconfigure(0, pad=5)
        bulkScrapeFrame.grid_columnconfigure(0, weight=1)
        bulkScrapeFrame.grid_columnconfigure(1, weight=3)
        bulkScrapeFrame.grid_columnconfigure(2, weight=3)
        bulkScrapeFrame.grid_columnconfigure(3, weight=3)

        coldata = [
            {"text": "ID"},
            {"text": "URL", "width": 500},
            {"text": "Type"},
            {"text": "Production Times(Scrape)"},
            {"text": "Stop Count", "width": 80},
            {"text": "Item"},
            {"text": "Product"},
            {"text": "Ink type"},
            {"text": "Density Type"},
            {"text": "Production Times(DB)"},
            {"text": "WorkDay"},
            {"text": "Coeff"},
            {"text": "Extrapolation Limit"},
            {"text": "Last Scrape"},
            {"text": "Last Export"},
        ]

        self.urlListTable = Tableview(
            master=bulkScrapeFrame,
            coldata=coldata,
            bootstyle=PRIMARY,
            height=10,
            searchable=True,
            autofit=True,
        )
        self.urlListTable.grid(row=0, column=0, padx=5, sticky="WE", columnspan=4)
        self.urlListTable.view.bind("<Double-1>", self.urlItemSelected)

        ttk.Button(bulkScrapeFrame, text="Add to List", command=self.addUrlToList).grid(row=1, column=0, pady=5)
        ttk.Button(bulkScrapeFrame, text="Remove From List", command=self.removeUrlFromList).grid(row=1, column=1,
                                                                                                  pady=5)
        ttk.Button(bulkScrapeFrame, text="Change Data", command=self.updateUrlInList).grid(row=1, column=2, pady=5)
        ttk.Button(bulkScrapeFrame, text="Bulk Scrape", command=self.bulkScrape).grid(row=1, column=3, pady=5)

        # Init SQL

        # Connect price db
        self.sql = SqlManager(self, host="XXXXXX", user="XXXXX", pwd="XXXXXX",
                              port="3306", database="c1lsd")

        # Connect Url List DB
        self.scrapeDB = SqlManager(self, host="localhost", user="root", pwd="", port="3306", database=URL_DB)

    def connectedDB(self, db):
        if db == PRICE_DB:
            self.after(0, self.LoadItemFromDB)
            self.after(0, self.LoadProductTimesFromDB)
        elif db == URL_DB:
            self.after(0, self.LoadURLList)

    def setItemText(self, txt):
        self.itemSelector.configure(text=txt)

    def setProductTimesText(self, txt):
        self.productTimesSelector.configure(text=txt)

    def setInkTypeText(self, txt):
        self.inkTypeSelector.configure(text=txt)

    def setDensityTypeText(self, txt):
        self.densityTypeSelector.configure(text=txt)

    def setFormatTypeText(self, txt):
        self.typeListSelector.configure(text=txt)

    def setScrapeTypeText(self, txt):
        self.typeSelector.configure(text=txt)

    def LoadItemFromDB(self):
        query = "SELECT * FROM items"
        itemList = self.sql.query(query).result()

        for item in itemList:
            self.itemMenu.add_radiobutton(
                label=item[2], value=item[0], variable=self.itemValues,
                command=lambda txt=item[2]: self.setItemText(txt))

        self.itemValues.trace('w', callback=self.itemChanged)

    def LoadProductTimesFromDB(self):
        query = "SELECT id, name FROM product_times"
        productTimesList = self.sql.query(query).result()
        for productTime in productTimesList:
            self.productTimesMenu.add_radiobutton(
                label=productTime[1], value=productTime[0], variable=self.productTimeValues,
                command=lambda txt=productTime[1]: self.setProductTimesText(txt))

    def LoadURLList(self):
        query = "SELECT * FROM tbl_url_list"
        self.urlList = self.scrapeDB.query(query).result()
        row = 0
        for urlData in self.urlList:
            self.urlListTable.insert_row(row, (
            urlData[0], urlData[1], urlData[3], urlData[4], urlData[5], urlData[7], urlData[9], urlData[11],
            urlData[13], urlData[15], urlData[16], urlData[17], urlData[20], urlData[18], urlData[19]))
            row += 1
        self.urlListTable.load_table_data()

    def itemChanged(self, *args):
        self.typeListMenu.delete(0, self.typeListMenu.index('end'))
        self.formatTypeValues.set("")

        itemId = self.itemValues.get()
        query = f"""
            SELECT DISTINCT ft.id, ft.name
            FROM format_types ft
            JOIN item_prices ip ON ip.format_type_id = ft.id
            WHERE ip.item_id = {itemId}
            """
        fTypeList = self.sql.query(query).result()

        for fType in fTypeList:
            self.typeListMenu.add_radiobutton(label=fType[1], value=fType[0], variable=self.formatTypeValues,
                                              command=lambda txt=fType[1]: self.setFormatTypeText(txt))

        self.formatTypeValues.trace('w', callback=self.formatTypeChanged)

    def formatTypeChanged(self, *args):
        self.inkTypeMenu.delete(0, self.inkTypeMenu.index('end'))
        self.inkTypeValues.set("")

        formatTypeId = self.formatTypeValues.get()
        if formatTypeId == "":
            return
        query = f"""
            SELECT DISTINCT it.id, it.name
            FROM inking_types it
            JOIN item_prices ip ON ip.inking_type_id = it.id
            WHERE ip.format_type_id = {formatTypeId}
            """
        inkTypeList = self.sql.query(query).result()
        for inkType in inkTypeList:
            self.inkTypeMenu.add_radiobutton(label=inkType[1], value=inkType[0], variable=self.inkTypeValues,
                                             command=lambda txt=inkType[1]: self.setInkTypeText(txt))

        self.inkTypeValues.trace('w', callback=self.inkTypeChanged)

    def inkTypeChanged(self, *args):
        self.densityTypeMenu.delete(0, self.densityTypeMenu.index('end'))
        self.densityTypeValues.set("")

        itemId = self.itemValues.get()
        formatTypeId = self.formatTypeValues.get()
        if formatTypeId == "":
            return
        query = f"""
            SELECT DISTINCT dt.id, dt.name
            FROM density_types dt
            JOIN item_prices ip ON ip.density_type_id = dt.id
            WHERE ip.item_id = {itemId} AND ip.format_type_id = {formatTypeId}
            """
        densityTypeList = self.sql.query(query).result()
        for densityType in densityTypeList:
            self.densityTypeMenu.add_radiobutton(label=densityType[1], value=densityType[0],
                                                 variable=self.densityTypeValues,
                                                 command=lambda txt=densityType[1]: self.setDensityTypeText(txt))

    def fetchDataFromDB(self):
        itemId = self.itemValues.get()
        ftypeId = self.formatTypeValues.get()
        inkTypeId = self.inkTypeValues.get()
        densityTypeId = self.densityTypeValues.get()
        productTimeId = self.productTimeValues.get()

        if itemId == "":
            Messagebox.show_error("Select Item!", "Error")
            return
        if ftypeId == "":
            Messagebox.show_error("Select Format Type!", "Error")
            return
        if inkTypeId == "":
            Messagebox.show_error("Select ink Type!", "Error")
            return
        if densityTypeId == "":
            Messagebox.show_error("Select Density Type!", "Error")
            return
        if productTimeId == "":
            Messagebox.show_error("Select Product Time!", "Error")
            return

        query = f"""
        SELECT ipr.count, ipptr.sum
        FROM item_price_product_time_rows ipptr
        INNER JOIN item_price_rows ipr ON ipptr.item_price_row_id = ipr.id
        INNER JOIN item_prices ip ON ipr.item_price_id = ip.id
        WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} AND ipptr.product_time_id = {productTimeId}
        ORDER BY ipr.count
        """
        self.mysqlData = self.sql.query(query).result()
        print(query)

        self.sqlTable.delete_rows()
        for dbData in self.mysqlData:
            self.sqlTable.insert_row(values=(str(dbData[0]), round(float(dbData[1]), 2)))

        self.sqlTable.load_table_data()

    def findInList(self, findList, tpl):
        for data in findList:
            if data[0] == tpl[0]:
                return True
        return False

    def mergeData(self):
        self.exportData = []
        self.scrapeData = sorted(self.scrapeData, key=lambda tpl: float(tpl[0]))

        if len(self.scrapeData) == 0:
            Messagebox.show_error("Scrape data before merge!", "Error")
            return

        if len(self.mysqlData) == 0:
            Messagebox.show_error("Fetch data from sql database before merge!", "Error")
            return

        self.exportTable.delete_rows()
        self.exportData = self.scrapeData

        print(self.scrapeData)
        rate = float(self.scrapeData[-1][1]) / int(self.scrapeData[-1][0])
        for sqlData in self.mysqlData:
            flag = False
            for data in self.scrapeData:
                if int(data[0]) == int(sqlData[0]):
                    flag = True
                    break
                if int(data[0]) > int(sqlData[0]):
                    flag = True
                    self.exportData.append((sqlData[0], data[1]))
                    break

            if flag:
                continue
            print(self.scrapeData[-1])
            print(rate)
            self.exportData.append((sqlData[0], rate * int(sqlData[0])))
        self.exportData = sorted(self.exportData, key=lambda tpl: float(tpl[0]))

        for expData in self.exportData:
            self.exportTable.insert_row(values=(str(expData[0]), round(float(expData[1]), 2)))

        self.exportTable.load_table_data()

        self.extraCountEntry.delete(0, 'end')
        self.extraCountEntry.insert(0, self.scrapeData[-1][0])
        self.fetchCountFromValue()

    def exportDataToDatabase(self):
        itemId = self.itemValues.get()
        ftypeId = self.formatTypeValues.get()
        inkTypeId = self.inkTypeValues.get()
        densityTypeId = self.densityTypeValues.get()
        productTimeId = self.productTimeValues.get()
        workDay = self.workDayInput.get()
        coeff = self.coeffInput.get()

        if len(self.exportData) == 0:
            Messagebox.show_error("Merge scraped data and sql data before export!", "Error")
            return

        for exp in self.exportData:
            query = f"""
            SELECT ipr.id
            FROM item_price_product_time_rows ipptr
            INNER JOIN item_price_rows ipr ON ipptr.item_price_row_id = ipr.id
            INNER JOIN item_prices ip ON ipr.item_price_id = ip.id
            WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} AND ipptr.product_time_id = {productTimeId} AND ipr.count={exp[0]}
            ORDER BY ipr.count
            """
            ret = self.sql.query(query).result()
            if len(ret) == 0:
                query = f"""
                    INSERT INTO item_price_rows (item_price_id, count) 
                    SELECT ip.id, "{exp[0]}"
                    FROM item_prices ip
                    WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} 
                """
                insertID = self.sql.insert_query(query).result()

                query = f"""
                    INSERT INTO item_price_product_time_rows (item_price_row_id, product_time_id, sum, coefficient, work_day)
                    VALUES({insertID}, {productTimeId}, {exp[1]}, {coeff}, '{workDay}') 
                """
                self.sql.insert_query(query).result()
            else:
                query = f"""
                        UPDATE item_price_product_time_rows ipptr
                        INNER JOIN item_price_rows ipr ON ipptr.item_price_row_id = ipr.id
                        INNER JOIN item_prices ip ON ipr.item_price_id = ip.id
                        SET ipptr.sum={exp[1]}, ipptr.coefficient={coeff}, ipptr.work_day='{workDay}'
                        WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} AND ipptr.product_time_id = {productTimeId} AND ipr.count={exp[0]}
                        """
                ret = self.sql.query(query).result()
        self.fetchDataFromDB()

    def fetchCountFromValue(self):
        if len(self.scrapeData) == 0:
            Messagebox.show_error("Scarpe Data First", "Error")
            return

        count = self.extraCountEntry.get()
        if count == "":
            Messagebox.show_error("Insert count value!", "Error")
            return

        for tpl in self.scrapeData:
            if int(tpl[0]) == int(count):
                self.extraValueEntry.delete(0, 'end')
                self.extraValueEntry.insert(0, tpl[1])
                return

        Messagebox.show_error("No matching count in scraped data!", "Error")

    def generateScaleData(self):
        self.extraScaleData = []
        baseCount = self.extraCountEntry.get()
        baseValue = self.extraValueEntry.get()
        stopPiece = self.extraStopCountEntry.get()
        if baseValue == "" or stopPiece == "":
            Messagebox.show_error("Fill all the fields!", "Error")
            return

        baseCount = int(baseCount)
        baseValue = float(baseValue)
        stopPiece = int(stopPiece)

        if baseCount == 0 or baseValue == 0 or stopPiece <= 0:
            Messagebox.show_error("Wrong value for base count or value or stop piece!", "Error")
            return

        idx = baseCount + 1000
        while idx <= stopPiece:
            price = baseValue / baseCount * idx
            self.extraScaleData.append((idx, price))
            idx += 1000

        self.exportTable.delete_rows()
        for extraData in self.extraScaleData:
            self.exportTable.insert_row(values=(str(extraData[0]), round(float(extraData[1]), 2)))

        self.exportTable.load_table_data()
        print(self.extraScaleData)

    def exportScaleDataToDB(self):
        itemId = self.itemValues.get()
        ftypeId = self.formatTypeValues.get()
        inkTypeId = self.inkTypeValues.get()
        densityTypeId = self.densityTypeValues.get()
        productTimeId = self.productTimeValues.get()
        workDay = self.workDayInput.get()
        coeff = self.coeffInput.get()

        for exportData in self.extraScaleData:
            query = f"""
                INSERT INTO item_price_rows (item_price_id, count) 
                SELECT ip.id, "{exportData[0]}"
                FROM item_prices ip
                WHERE ip.item_id = {itemId} AND ip.format_type_id = {ftypeId} AND ip.inking_type_id = {inkTypeId} AND ip.density_type_id = {densityTypeId} 
            """
            insertID = self.sql.insert_query(query).result()

            query = f"""
                INSERT INTO item_price_product_time_rows (item_price_row_id, product_time_id, sum, coefficient, work_day)
                VALUES({insertID}, {productTimeId}, {exportData[1]}, {coeff}, '{workDay}') 
            """
            self.sql.insert_query(query).result()

        self.fetchDataFromDB()

    def resetAll(self):
        self.scrapeData = []
        self.mysqlData = []
        self.exportData = []
        self.extraScaleData = []
        self.scrapeTable.delete_rows()
        self.sqlTable.delete_rows()
        self.exportTable.delete_rows()
        self.scraper.reset()

    def addUrlToList(self):
        url = self.url_entry.get()
        typ = self.scrapeTypes.get()
        scrapeTime = self.express_option.get()
        stopCount = self.stopCntInput.get()
        itemId = self.itemValues.get()
        ftypeId = self.formatTypeValues.get()
        inkTypeId = self.inkTypeValues.get()
        densityTypeId = self.densityTypeValues.get()
        productTimeId = self.productTimeValues.get()
        workDay = self.workDayInput.get()
        coeff = self.coeffInput.get()
        extraLimit = self.extraStopCountEntry.get()

        if url == "":
            Messagebox.show_error("Input URL!", "Error")
            return

        if typ == "":
            Messagebox.show_error("Select type of scrape data!", "Error")
            return

        if scrapeTime == "":
            Messagebox.show_error("Select Express Option!", "Error")
            return

        if stopCount == "":
            Messagebox.show_error("Input Stop count pieces!", "Error")
            return

        if itemId == "":
            Messagebox.show_error("Select Item!", "Error")
            return

        if ftypeId == "":
            Messagebox.show_error("Select format type!", "Error")
            return

        if inkTypeId == "":
            Messagebox.show_error("Select Ink Type!", "Error")
            return

        if densityTypeId == "":
            Messagebox.show_error("Select Density Type!", "Error")
            return

        if productTimeId == "":
            Messagebox.show_error("Select Product Time!", "Error")
            return

        if workDay == "":
            Messagebox.show_error("Input Work Day!", "Error")
            return

        if coeff == "":
            Messagebox.show_error("Input Coeff!", "Error")
            return

        if extraLimit == "":
            extraLimit = "0"

        query = f"""
                    INSERT INTO tbl_url_list (url, type, type_text, prod_scrape_time, stop_count, item, item_text, products, products_text, inktype, inktype_text, densitytype, densitytype_text, prod_db_time, prod_db_time_text, workday, coeff, extra_limit)
                    VALUES("{url}",{typ},"{self.typeSelector.cget('text')}","{scrapeTime}",{stopCount},{itemId},"{self.itemSelector.cget('text')}",{ftypeId},"{self.typeListSelector.cget('text')}",{inkTypeId},"{self.inkTypeSelector.cget('text')}",{densityTypeId},"{self.densityTypeSelector.cget('text')}",{productTimeId},"{self.productTimesSelector.cget('text')}",'{workDay}',{coeff}, {extraLimit}) 
                """

        insertID = self.scrapeDB.insert_query(query).result()

        self.urlList.append((insertID, url, typ, self.typeSelector.cget('text'), scrapeTime, stopCount, itemId,
                             self.itemSelector.cget('text'), ftypeId, self.typeListSelector.cget('text'), inkTypeId,
                             self.inkTypeSelector.cget('text'), densityTypeId, self.densityTypeSelector.cget('text'),
                             productTimeId, self.productTimesSelector.cget('text'), workDay, coeff, extraLimit))

        self.urlListTable.insert_row(values=(
        insertID, url, self.typeSelector.cget('text'), scrapeTime, stopCount, self.itemSelector.cget('text'),
        self.typeListSelector.cget('text'), self.inkTypeSelector.cget('text'), self.densityTypeSelector.cget('text'),
        self.productTimesSelector.cget('text'), workDay, coeff, extraLimit))

        self.urlListTable.load_table_data()

    def removeUrlFromList(self):
        deleteRowIDs = self.urlListTable.get_rows(selected=True)

        if len(deleteRowIDs) == 0:
            Messagebox.show_error("Select Urls from DB!", "Error")
            return

        if Messagebox.yesno("Do you want to delete selected rows?", "Delete") == 'No':
            return

        urlIDList = ()
        for rowID in deleteRowIDs:
            rowID.delete()
            urlIDList += (rowID.values[0],)
            for data in self.urlList:
                if int(data[0]) == int(rowID.values[0]):
                    self.urlList.remove(data)
                    break

        tplStr = ""
        if len(urlIDList) == 1:
            tplStr += str(urlIDList[0])
        else:
            tplStr = str(urlIDList)
        query = f"""
                    DELETE FROM tbl_url_list WHERE id IN {tplStr}
                """
        self.scrapeDB.query(query).result()

    def urlItemSelected(self, event):
        rows = self.urlListTable.get_rows(selected=True)
        if len(rows) > 1:
            Messagebox.show_error("Don't select multiple items!", "Error")
            return

        if len(rows) == 0:
            Messagebox.show_error("Select Item from Table!", "Error")
            return

        rowData = rows[0].values
        print(rowData)
        self.url_entry.delete(0, 'end')
        self.url_entry.insert(0, rowData[1])

        self.stopCntInput.delete(0, 'end')
        self.stopCntInput.insert(0, rowData[4])

        self.workDayInput.delete(0, 'end')
        self.workDayInput.insert(0, rowData[10])

        self.coeffInput.delete(0, 'end')
        self.coeffInput.insert(0, rowData[11])

        self.setItemText(rowData[5])
        self.setFormatTypeText(rowData[6])
        self.setInkTypeText(rowData[7])
        self.setDensityTypeText(rowData[8])
        self.setProductTimesText(rowData[9])
        self.setScrapeTypeText(rowData[2])
        self.express_option.set(rowData[3])

        self.extraStopCountEntry.delete(0, 'end')
        self.extraStopCountEntry.insert(0, rowData[12])

    def updateUrlInList(self):
        rows = self.urlListTable.get_rows(selected=True)
        if len(rows) > 1:
            Messagebox.show_error("Don't select multiple items!", "Error")
            return

        if len(rows) == 0:
            Messagebox.show_error("Select Item from Table!", "Error")
            return

        url = self.url_entry.get()
        typ = self.scrapeTypes.get()
        scrapeTime = self.express_option.get()
        stopCount = self.stopCntInput.get()
        itemId = self.itemValues.get()
        ftypeId = self.formatTypeValues.get()
        inkTypeId = self.inkTypeValues.get()
        densityTypeId = self.densityTypeValues.get()
        productTimeId = self.productTimeValues.get()
        workDay = self.workDayInput.get()
        coeff = self.coeffInput.get()
        extraLimit = self.extraStopCountEntry.get()

        if url == "":
            Messagebox.show_error("Input URL!", "Error")
            return

        if typ == "":
            Messagebox.show_error("Select type of scrape data!", "Error")
            return

        if scrapeTime == "":
            Messagebox.show_error("Select Express Option!", "Error")
            return

        if stopCount == "":
            Messagebox.show_error("Input Stop count pieces!", "Error")
            return

        if itemId == "":
            Messagebox.show_error("Select Item!", "Error")
            return

        if ftypeId == "":
            Messagebox.show_error("Select format type!", "Error")
            return

        if inkTypeId == "":
            Messagebox.show_error("Select Ink Type!", "Error")
            return

        if densityTypeId == "":
            Messagebox.show_error("Select Density Type!", "Error")
            return

        if productTimeId == "":
            Messagebox.show_error("Select Product Time!", "Error")
            return

        if workDay == "":
            Messagebox.show_error("Input Work Day!", "Error")
            return

        if coeff == "":
            Messagebox.show_error("Input Coeff!", "Error")
            return

        if extraLimit == "":
            extraLimit = "0"

        rowData = rows[0].values

        for idx, data in enumerate(self.urlList):
            if int(data[0]) == int(rowData[0]):
                self.urlList[idx] = (data[0], url, typ, self.typeSelector.cget('text'), scrapeTime, stopCount, itemId,
                                     self.itemSelector.cget('text'), ftypeId, self.typeListSelector.cget('text'),
                                     inkTypeId, self.inkTypeSelector.cget('text'), densityTypeId,
                                     self.densityTypeSelector.cget('text'), productTimeId,
                                     self.productTimesSelector.cget('text'), workDay, coeff, extraLimit)
                break

        rows[0].values = (
        rowData[0], url, self.typeSelector.cget('text'), scrapeTime, stopCount, self.itemSelector.cget('text'),
        self.typeListSelector.cget('text'), self.inkTypeSelector.cget('text'), self.densityTypeSelector.cget('text'),
        self.productTimesSelector.cget('text'), workDay, coeff, extraLimit)

        query = f"""
                UPDATE tbl_url_list
                SET url="{url}", type={typ}, type_text="{self.typeSelector.cget('text')}", prod_scrape_time="{scrapeTime}", stop_count={stopCount}, item={itemId}, item_text="{self.itemSelector.cget('text')}", products={ftypeId}, products_text="{self.typeListSelector.cget('text')}", inktype={inkTypeId}, inktype_text="{self.inkTypeSelector.cget('text')}", densitytype={densityTypeId}, densitytype_text="{self.densityTypeSelector.cget('text')}", prod_db_time={productTimeId}, prod_db_time_text="{self.productTimesSelector.cget('text')}", workday={workDay}, coeff={coeff}, extra_limit={extraLimit}
                WHERE id={rowData[0]}
                """

        self.scrapeDB.query(query).result()

    def bulkScrape(self):
        scrapeRowIDs = self.urlListTable.get_rows(selected=True)
        infoList = []

        for rowID in scrapeRowIDs:
            for data in self.urlList:
                if int(data[0]) == int(rowID.values[0]):
                    infoList.append(data)
                    break

        self.bulkScraper = BulkScraper(infoList, self)
        self.bulkScraper.startBulkScrape()


def main():
    window = WorkspaceWindow()
    window.mainloop()


if __name__ == "__main__":
    main()
