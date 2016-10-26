# 导入股票数据数据库
# 连接MongoDB

import pymongo


# Stock集合用于股票的行业分类信息存储
# Stockdata集合用于各只股票信息存储
class MongoDatabase:
    def __init__(self):

        client = pymongo.MongoClient(host='115.159.75.92', port=27017)
        self._db = client.test
        self._db.authenticate("guoyang", "846686")

    def use_stock_classify(self):
        stockClassify = self._db.stockClassify

        return stockClassify

    def use_stock_data(self):
        stockData = self._db.stockData
        # stockData.inser(datalist)
        return stockData

        # def classify_json(self):
if __name__ == "__main__":
    db = MongoDatabase()
    try:
        stockdata=db.use_stock_data()
        datalist=stockdata.find().count()
        print(datalist)
    except:
        print("连接出错")