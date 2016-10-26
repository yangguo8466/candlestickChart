# 获得每日股票数据信息
import tushare as ts
from CandlestickCharts.Candlestick import Candlestick
from CandlestickCharts.Database import MongoDatabase
from matplotlib.dates import date2num,num2date

import json
import string
from numpy import *

class StockData:
    ' 单只股票股票数据 未设计数据库'

    def __init__(self, ticket, start, end):
        self._ticket = ticket
        self._start = start
        self._end = end
        self._data = ts.get_h_data(self._ticket, self._start, self._end, retry_count=99)
        self.database = MongoDatabase()


    def get_data(self):
        '获得每日数据'
        # data = ts.get_h_data(self._ticket, self._start, self._end)
        # print(type(self._data))
        return self._data

    def ohlc_quotes(self):
        'format data 格式化参数[time,open,high,low,close]'

        data = self.get_data()
        list_times = []
        list_opens = []
        list_highs = []
        list_lows = []
        list_closes = []

        # time时间
        times = data.index.date
        for i in times:
            # print(i,date2num(i))
            list_times.append(date2num(i))

        # open开盘
        opens = data.open
        for i in opens:
            list_opens.append(i)

        # high最高价
        highs = data.high
        for i in highs:
            list_highs.append(i)

        # low最低价
        lows = data.low
        for i in lows:
            list_lows.append(i)

        # close收盘
        closes = data.close
        for i in closes:
            list_closes.append(i)

        quotes = list()
        for i in range(0, len(list_times)):
            quotes.append((list_times[i], list_opens[i], list_highs[i], list_lows[i], list_closes[i]))
        # print(len(quotes))
        return quotes

    def get_dates(self):
        '获得开盘日期'
        data = self.get_data()
        dates = data.index.date
        return dates

    def get_lows(self):
        data = self.get_data()
        lows = data.low
        return lows

    def transform_candles(self):
        quotes = self.ohlc_quotes()
        candles = list()
        for quote in quotes:
            candle = Candlestick(quote)
            candles.append(candle)
        # 存储到MongoDB中

        return candles

    def insert_mongo(self):
        # 获取日期
        dates = self.get_dates()
        code = self._ticket
        # 获取数据列表
        data = self.get_data()
        datajson = json.loads(data.to_json(orient='records'))
        for i in range(len(datajson)):
            datajson[i]['date'] = date2num(dates[i])
            datajson[i]['code'] = code

        stockData = self.database.use_stock_data()
        stockData.insert(datajson)
        # stockData.createIndex()

    def get_stockname(self):
        return self._ticket

class StockInMongo:
    '涉及数据库'
    def __init__(self,code,timelength=6):
        self.database=MongoDatabase()
        self.code=code
        self.timelength=timelength
    def get_dates(self):
        '获得股票日期'
        stocklist=self.get_stocklist()
        dates=list()
        for stock in stocklist:
            dates.append(num2date(stock['date']))

        return array(dates)
    def get_lows(self):
        '获得最低价'
        stocklist = self.get_stocklist()
        lows = list()
        for stock in stocklist:
            lows.append(stock['low'])
        return array(lows)
    def get_highs(self):
        '获得最高价'
        stocklist = self.get_stocklist()
        highs = list()
        for stock in stocklist:
            highs.append(stock['high'])
        return array(highs)
    def get_stocklist(self):
        '获得股票列表'
        stockData = self.database.use_stock_data()

        return stockData.find({"code":self.code})

    def get_poorMtm(self):
        return MTM(self.code,self.timelength).get_poorMtm()
    def get_divisionMtm(self):
        return MTM(self.code,self.timelength).get_divisionMtm()
    # def get_poorMtm(self):
    #     return MTM(self.code,self.time)

class MTM:
    'MTM指标在数据库中设置以及相关参数信息的获取'
    def __init__(self, code, timelength=6):
        self.code = code
        self.timelength = timelength
        self.database = MongoDatabase()
        self.divisionMtm=dict()
        self.poorMtm=dict()
        self.poor_caculate()
        self.division_caculate()

    def poor_caculate(self):
        "作差法计算MTM"
        stockData = self.database.use_stock_data()
        datalist = stockData.find({'code': self.code})
        length = datalist.count()
        # print("length",length)
        # poormtms=list()
        for i in range(length):
            if i < self.timelength:
                stockData.update({"code": self.code, "date": datalist[i]['date']}, {'$set': {"poorMtm": "null"}})
                continue
            # n日前股票数据
            pre = datalist[i - self.timelength]
            #     当前股票数据
            cur = datalist[i]
            curdate=datalist[i]['date']
            mtm = round((cur['close'] - pre['close']),2)
            datelist=list()
            mtmlist=list()
            datelist.append(curdate)
            mtmlist.append(mtm)
            self.poorMtm={"dates":datalist,"mtms":mtmlist};
            stockData.update({"code": self.code,"date":curdate}, {'$set': {"poorMtm": mtm}})
            # datalist[i]['poorMtm'] = mtm
        # print("i",i)

    def division_caculate(self):
        "做除法计算MTM"
        stockData = self.database.use_stock_data()
        datalist = stockData.find({'code': self.code})
        length = datalist.count()

        for i in range(length):
            if i < self.timelength:
                stockData.update({"code": self.code, "date": datalist[i]['date']}, {'$set': {"divisionMtm": "null"}})
                continue

            pre = datalist[i - self.timelength]
            cur = datalist[i]
            curdate = datalist[i]['date']
            mtm = round(((cur['close'] / pre['close']) * 100 - 100), 2)
            # 载入做除动量指标数据
            datelist = list()
            mtmlist = list()
            datelist.append(curdate)
            mtmlist.append(mtm)
            self.divisionMtm = {"dates": datalist, "mtms": mtmlist};
            stockData.update({"code": self.code,"date":curdate}, {'$set': {"divisionMtm": mtm}})


    def get_poorMtm(self):

        stockData = self.database.use_stock_data()
        datalist = stockData.find({"code": self.code})
        datelist = list()
        mtmlist = list()
        # print(len(self.poorMtm))
        # 剔除开始几天的数据
        for data in datalist:
            if data['poorMtm']!="null":
                datelist.append(data['date'])
                mtmlist.append(data['poorMtm'])
                # print(data['date'],data['poorMtm'])

        self.poorMtm = {"dates": datelist, "mtms": mtmlist};
        # print(type(datelist),"datelist")
        # print(type(mtmlist),"mtmlist")
        return self.poorMtm


    def get_divisionMtm(self):
        # if len(self.divisionMtm)==0:
        stockData = self.database.use_stock_data()
        datalist = stockData.find({"code": self.code})

        datelist = list()
        mtmlist = list()
            # print(len(self.divisionMtm))
        for data in datalist:
            if data['divisionMtm']!= 'null':
                datelist.append(data['date'])
                mtmlist.append(data['divisionMtm'])

        self.divisionMtm = {"dates": datelist, "mtms": mtmlist};
        return self.divisionMtm

class ClassifiedStock:
    def __init__(self):
        self.mongo = MongoDatabase()

    def fetch_data(self):
        data = ts.get_industry_classified('sina')
        classify = self.mongo.use_stock_classify()
        classify.remove()
        classify.insert(json.loads(data.to_json(orient='records')))

    def get_classifies(self):
        '获得行业分类'
        classify = self.mongo.use_stock_classify()
        classifies = classify.distinct("c_name")
        return classifies

    def get_stocklist(self):
        '获得各行业股票代码信息'
        classify = self.mongo.use_stock_classify()
        # 行业分类+股票代码
        stockinfo = classify.find({}, {"code": 1, "_id": 0, "c_name": 1})

        return stockinfo

    def get_beclassify(self, code):
        '获取股票所属行业类别'

        stockInfo = self.get_stocklist()
        index = 0
        for stock in stockInfo:
            flag = stock['code']
            if flag==code:
                classify = stockInfo[index]['c_name']
                break
            index += 1
        return classify


# if __name__ == "__main__":
    # def get_stocklist():
    #     mongo=MongoDatabase()
    #     stockData=mongo.use_stock_data()
    #     return stockData.distinct("code")
    # stocklist=get_stocklist()
    # for stock in stocklist:
    #     print("当前code:",stock)
    #     mtm = MTM(code=stock, timelength=6)
    #     mtm.poor_caculate()
    #     mtm.division_caculate()
    #     # except:
    #     #     print("error")
    # print("赋值结束")
    # data=MTM('600131',6).get_poorMtm()
    # print(type(data))
    # print(len(data['dates']),len(data['mtms']))