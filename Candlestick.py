# 单日k线类包括判断k线形态方法
# ocrate=|收盘价-开盘价|/开盘价
# hlrate=最高价-最低价/最低价
# 阳线---收盘价>开盘价
# 阴线---收盘价<开盘价
# 大阳线---（收盘价-开盘价）/开盘价>7%
# 大阴线---（开盘价-收盘价）/开盘价>7%
# 中阳线---7%>(收盘价-开盘价）/开盘价>3%
# 中阴线---7%>(开盘价-收盘价）/开盘价>3%
# 小阳线---3%>（收盘价-开盘价）/开盘价>1%
# 小阴线---3%>（开盘价-收盘价）/开盘价>1%
# 一字线---波动率<1%且无上下影线（最高价-最低价）/最高价<1%
# 十字线---波动率<1%且有上下影线

from matplotlib.dates import num2date


class Candlestick:
    def __init__(self, date, openprice, highprice, lowprice, closeprice):
        self._date = date
        self._open = openprice
        self._high = highprice
        self._low = lowprice
        self._close = closeprice
        # 开收盘波动率
        self._ocrate = round(abs(openprice - closeprice) / openprice, 2)
        # 最高价最低价波动率
        self._hlrate = round((highprice - lowprice) / highprice, 2)

    #     高低价波动<0.01影线较短，>0.01影线较长
    def __init__(self, quote):
        if len(quote) == 5:
            date = quote[0]
            openprice = quote[1]
            highprice = quote[2]
            lowprice = quote[3]
            closeprice = quote[4]

            self._date = date
            self._open = openprice
            self._high = highprice
            self._low = lowprice
            self._close = closeprice

            # 开收盘波动率
            self._ocrate = round(abs(openprice - closeprice) / openprice, 2)
            # 最高价最低价波动率
            self._hlrate = round((highprice - lowprice) / highprice, 2)

        else:
            print('length of quote is {0} at least 5'.format(len(quote)))

    def print_candle(self):

        print('date={0},open={1},high={2},low={3},close={4}'.
              format(num2date(self._date), self._open, self._high, self._low, self._close))

    def get_kdata(self):
        '获取candle参数列表'
        kdata = {'date': self._date,
                 'open': self._open,
                 'high': self._high,
                 'low': self._low,
                 'close': self._close}
        return kdata

    def is_positive(self):
        '阳线'
        return self._open <= self._close

    def is_negative(self):
        '阴线'
        return self._open >= self._close

    def is_maxpositive(self):
        '大阳线'
        if self.is_positive():
            return self._ocrate >= 0.07
        return False

    def is_maxnegative(self):
        '大阴线'
        if self.is_negative():
            return self._ocrate >= 0.07
        return False

    def is_minpositive(self):
        '小阳线'
        if self.is_positive():
            flag = self._ocrate
            return 0.03 > flag >=0.01
        return False

    def is_minnegative(self):
        '小阴线'
        if self.is_negative():
            flag = self._ocrate
            return 0.03 > flag >=0.01
        return False

    def is_midpositive(self):
        '中阳线'
        if self.is_positive():
            flag = self._ocrate
            return 0.07 > flag >= 0.03
        return False

    def is_midnegative(self):
        '中阴线'
        if self.is_negative():
            flag = self._ocrate
            return 0.07 > flag >= 0.03

    def is_doji(self):
        '十字星,具有上影线与下影线(较长或者较短)'
        return (self._ocrate < 0.01) & (self._hlrate > 0.01)

        # def is_hammer(self):
        #     '锤头'
        #     return False

    def is_oneline(self):
        '一字线'
        return (self._ocrate < 0.01) & (self._hlrate < 0.01)

    def is_spinning_top(self):
        '纺锤线实体较小且带有较长影线'
        percent = round((abs(self._open - self._close) / (self._high - self._low)), 2)
        if self.is_positive():
            upline = round((self._high - self._close) / (self._high - self._low), 2)
            downline = round((self._open - self._low) / (self._high - self._low), 2)
        else:
            upline = round((self._high - self._open) / (self._high - self._low), 2)
            downline = round((self._close - self._low) / (self._high - self._low), 2)
        return (0.2>=percent>=0.1)&(upline>0.2)&(downline>0.2)

    def is_high_wave(self):
        '高浪线定义：实体占k线小于0.2或小阴线小阳线，上下影线比例大于0.4'
        entity = round((abs(self._open - self._close) / (self._high - self._low)), 2)
        if self.is_positive():
            upline = round((self._high - self._close) / (self._high - self._low), 2)
            downline = round((self._open - self._low) / (self._high - self._low), 2)
        else:
            upline = round((self._high - self._open) / (self._high - self._low), 2)
            downline = round((self._close - self._low) / (self._high - self._low), 2)

        return (self.is_minpositive() | self.is_minnegative()) & (entity >= 0.1) & (upline >= 0.4) & (downline >= 0.4)

    def is_hammer(self):
        '锤子线：下影线长度为实体的2倍，设置一般为实体长度较小介于中线实体与小线实体之间,'
        entity = round((abs(self._open - self._close) / (self._high - self._low)), 2)
        if self.is_positive():
            upline = round((self._high - self._close) / (self._high - self._low), 2)
            downline = round((self._open - self._low) / (self._high - self._low), 2)
            return (self.is_minpositive() | self.is_midpositive()) & (downline >= 2 * entity) & (upline <= 0.1)
        else:
            upline = round((self._high - self._open) / (self._high - self._low), 2)
            downline = round((self._close - self._low) / (self._high - self._low), 2)
            return (self.is_minnegative() | self.is_midnegative()) & (downline >= 2 * entity) & (upline <= 0.1)

    def is_hanging_man(self):
        '上吊线：下影线长度实体的2倍，设置实体较小,上影线较短或没有'
        entity = round((abs(self._open - self._close) / (self._high - self._low)), 2)
        if self.is_positive():
            upline = round((self._high - self._close) / (self._high - self._low), 2)
            downline = round((self._open - self._low) / (self._high - self._low), 2)
            return (self._ocrate == 0.01) & (downline >= 2 * entity) & (upline <= 0.1)
        else:
            upline = round((self._high - self._open) / (self._high - self._low), 2)
            downline = round((self._close - self._low) / (self._high - self._low), 2)
            return (self._ocrate == 0.01) & (downline >= 2 * entity) & (upline <= 0.1)

    def is_inverted_hammer(self):
        '倒置锤线：上影线长度为实体的两倍以上，设置实体较小，下影线较短或者没有'
        entity = round((abs(self._open - self._close) / (self._high - self._low)), 2)

        if self.is_positive():
            upline = round((self._high - self._close) / (self._high - self._low), 2)
            downline = round((self._open - self._low) / (self._high - self._low), 2)
            return (self._ocrate == 0.01) & (upline >= 2 * entity) & (downline <= 0.1)
        else:
            upline = round((self._high - self._open) / (self._high - self._low), 2)
            downline = round((self._close - self._low) / (self._high - self._low), 2)
            return (self._ocrate == 0.01) & (upline >= 2 * entity) & (downline <= 0.1)

    def get_ocrate(self):
        '波动范围'
        return self._ocrate
