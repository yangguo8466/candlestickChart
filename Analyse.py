# 分析k线形态
# 先找出小阴线或者小阳线位置，再判断前后线型（早晨之星，黄昏之星）
#
class AnalyseK:
    '组合形态分析函数'

    def __init__(self, stockdata):
        self._candles = stockdata.transform_candles()

    # 找出十字星
    def find_doji(self):
        'candles 是 CandleStick类型'

        dojis = {}
        position = 0
        for candle in self._candles:

            if candle.is_doji():
                dojis.setdefault(position, candle)
            position += 1

        # for i in doji:
        #     i.print_candle()
        # print('doji length {0}'.format(len(dojis)))

        return dojis

    def find_maxpositives(self):
        '找出所有大阳线'
        maxpositives = {}
        position = 0
        for candle in self._candles:
            if candle.is_maxpositive():
                maxpositives.setdefault(position, candle)
            position += 1
        # print('maxnegatives length {0}'.format(len(maxpositives)))

        return maxpositives

    def find_maxnegatives(self):
        '找出所有大阴线'
        maxnegatives = {}
        position = 0
        for candle in self._candles:
            if candle.is_maxnegative():
                maxnegatives.setdefault(position, candle)
            position += 1
        # print('maxpositive length {0}'.format(len(maxnegatives)))

        return maxnegatives
    def find_midnegatives(self):
        midnegatives={}
        position=0
        for candle in self._candles:
            if candle.is_midnegative():
                midnegatives.setdefault(position,candle)
            position+=1
        return midnegatives
    def find_midpositives(self):
        midpositives = {}
        position = 0
        for candle in self._candles:
            if candle.is_midpositive():
                midpositives.setdefault(position, candle)
            position += 1
        return midpositives

    def find_oneline(self):
        # 一字线
        onelines = []
        for candle in self._candles:
            if candle.is_oneline():
                onelines.append(candle)
        print('oneline length {0}'.format(len(onelines)))
        for i in onelines:
            print(i.print_candle())

        return onelines

    def find_morningstars(self):
        '返回字典类型'
        morstars = []
        dojis = self.find_doji()
        for position in dojis.keys():

            doji = dojis[position]
            lcandle = self._candles[position + 1]
            rcandle = self._candles[position - 1]
            # 判断是否是早晨之星左侧为阴线下降趋势右侧为阳线上升趋势
            # 只是简单的判断需要在Morningstar中进一步修正

            if lcandle.is_negative() & rcandle.is_positive():
                morstar = Morningstar(lcandle, doji, rcandle)
                if morstar.check():
                    morstars.append(morstar)
                    print("morstar>>>>>>>>>")
                    morstar.print_morningstar()

        print('修正后的早晨之星数目{0}'.format(len(morstars)))

        return morstars

    def find_eveningstars(self):
        '返回字典类型'
        evenstars = []
        dojis = self.find_doji()
        for position in dojis.keys():

            doji = dojis[position]
            lcandle = self._candles[position + 1]
            rcandle = self._candles[position - 1]
            # 判断是否是黄昏之星左侧为阳线上升趋势右侧为阴线下降趋势
            # 只是简单的判断需要在Eveningstar中进一步修正

            if lcandle.is_positive() & rcandle.is_negative():
                evenstar = Eveningstar(lcandle, doji, rcandle)
                if evenstar.check():
                    evenstars.append(evenstar)
                    print("evenstar:")
                    evenstar.print_eveningstar()

        print('修正后黄昏之星数目:{0}'.format(len(evenstars)))
        return evenstars

    def find_darkcloud(self):
        '前一天上升趋势，第二天开盘价高于昨日最高价，跳空高开,收盘价低于昨日收盘价，'
        darkclouds = []
        maxnegatives = self.find_maxnegatives()

        for position in maxnegatives.keys():
            maxnega = maxnegatives[position]
            lcandle = self._candles[position + 1]
            llcandle = self._candles[position + 2]

            # 简单判断上升趋势
            is_up = lcandle.is_maxpositive() & llcandle.is_positive()

            ldata = lcandle.get_kdata()
            negadata = maxnega.get_kdata()

            lopen = ldata['open']
            negaopen = negadata['open']
            lclose = ldata['close']
            negaclose = negadata['close']

            # 是否跳空高开,第二根阴线是否深入第一根实体内部
            is_tohigh = (negaopen > lopen) & (negaclose < lclose)

            if is_up & is_tohigh:
                darkcloud = Darkcloudcover(lcandle, maxnega)
                darkclouds.append(darkclouds)
                darkcloud.print_darkcloud()

        if len(darkclouds) != 0:
            print('乌云盖顶数目:{}'.format(len(darkclouds)))
        else:
            print("当前范围未出现乌云盖顶")

    def find_holdline(self):
        '两种抱线形态，1.穿头破脚阴包阳，2.穿头破脚阳包阴'
        # 阴抱阳
        blackholdreds = []
        maxblacks = self.find_maxnegatives()
        for position in maxblacks.keys():
            # 大阴线
            curblack = maxblacks[position]
            # 阳线
            lred = self._candles[position + 1]

            ldata = lred.get_kdata()
            curdata = curblack.get_kdata()

            # 阳线开盘收盘价
            lopen = ldata['open']
            lclose = ldata['close']

            # 较长阴线开盘收盘价
            curopen = curdata['open']
            curclose = curdata['close']

            # 阴线实体完全抱住阳线实体
            flag = (lopen > curclose) & (lclose < curopen)

            if flag:
                blackholdred = Holdline1(lred, curblack)
                blackholdreds.append(blackholdred)
                print("阴抱阴")
                blackholdred.print_holdlines()

        # 阳抱阴
        redholdblacks = []
        maxreds = self.find_maxpositives()
        for position in maxreds.keys():
            # 大阳线
            curred = maxreds[position]
            # 阴线
            lblack = self._candles[position + 1]

            ldata = lblack.get_kdata()
            curdata = curred.get_kdata()

            # 阴线开盘收盘价
            lopen = ldata['open']
            lclose = ldata['close']

            # 较长阳线开盘收盘价
            curopen = curdata['open']
            curclose = curdata['close']

            # 阳线实体完全抱住阴线实体
            flag = (lopen < curclose) & (lclose > curopen)

            if flag:
                redholdblack = Holdline0(lblack, curred)
                redholdblacks.append(redholdblack)
                print("阳抱阴")
                blackholdred.print_holdlines()

        print("阴抱阳线长度{0}".format(len(blackholdreds)))

        print("阳抱阴线长度{0}".format(len(redholdblacks)))

    def find_spinning_tops(self):
        '纺锤线是一种实体很小，影线很长的线形，它即可以是阴线也可以是阳线'
        spinning = {}
        position = 0
        print("纺锤线是一种实体很小，影线很长的线形，它即可以是阴线也可以是阳线")
        for candle in self._candles:
            if candle.is_spinning_top():
                spinning.setdefault(position, candle)
            position += 1
        if len(spinning)!=0:
            print(">>>>>纺锤线>>>>>")
            for key in spinning.keys():
                candle = spinning[key]
                candle.print_candle()
        else:
            print("当前时间段内不存在纺锤线形态,请更换时间段或者股票")

        return spinning

    def find_high_wave(self):
        '高浪线：高浪线上影线和下影线都很长的而实体很小的线形，代表多空胶着，迷失市场方向，趋势将产生变化，是变盘的前兆'
        print("高浪线上影线和下影线都很长的而实体很小的线形，代表多空胶着，迷失市场方向，趋势将产生变化，是变盘的前兆")
        highWave = {}
        position = 0;
        for candle in self._candles:
            if candle.is_high_wave():
                highWave.setdefault(position, candle)
            position += 1

        if len(highWave)!=0:
            print(">>>>高浪线>>>>>>")
            for key in highWave.keys():
                candle = highWave[key]
                candle.print_candle()
        else:
            print("当前时间段内不存在高浪线形态,请更换时间段或者股票")
        return highWave

    def find_hammer(self):
        '锤线：锤子线是指K线型态像一把锤子，下影线很长，没有或只有很短、可以忽略不计的上影线，开盘价和收盘价价位很接近，看上去就象锤子形状'
        print("锤子线是指K线型态像一把锤子，下影线很长，没有或只有很短、可以忽略不计的上影线，开盘价和收盘价价位很接近，看上去就象锤子形状")
        hammer = {}
        position = 0;
        for candle in self._candles:
            if candle.is_hammer():
                hammer.setdefault(position, candle)
            position += 1

        if len(hammer)!=0:
            print(">>>>>>锤线>>>>>>>")
            for key in hammer.keys():
                candle = hammer[key]
                candle.print_candle()
        else:
            print("当前时间段内不存在锤线形态,请更换时间段或者股票")

        return hammer

    def find_hanging_man(self):
        '吊线：表示一个交易日里股价低开或平开，然后盘不断振荡下挫，只到收盘时才将股价拉起，停在高位留下一根长长的下阴线。一般是见顶的信号'
        hanging = {}
        position = 0
        print("吊线：表示一个交易日里股价低开或平开，然后盘不断振荡下挫，只到收盘时才将股价拉起，停在高位留下一根长长的下阴线。一般是见顶的信号")
        for candle in self._candles:
            if candle.is_hanging_man():
                hanging.setdefault(position, candle)
            position += 1

        if len(hanging)!=0:
            print(">>>>>>吊线>>>>>>")
            for key in hanging.keys():
                candle = hanging[key]
                candle.print_candle()
        else:
            print("当前时间段内不存在吊线形态,请更换时间段或者股票")
        return hanging

    def find_shooting_star(self):
        '流星线：在上升趋势中具有较大的涨幅,并向上跳空高开(当日开盘价大于前一日收盘价)，预示着股市由升转跌'
        # (当前最新成交价（或收盘价）-开盘参考价)/开盘参考价   开盘参考价=前一交易日收盘价
        print("流星线：在上升趋势中具有较大的涨幅,并向上跳空高开(当日开盘价大于前一日收盘价)，预示着股市由升转跌")
        shootstar = {}
        position = 0;
        length = len(self._candles) - 3
        for candle in self._candles:
            if candle.is_inverted_hammer()&(position<=length):
                lcandle=self._candles[position+1]
                llcandle = self._candles[position + 2]
                lllcandle=self._candles[position+3]
                l_kdata=lcandle.get_kdata();
                ll_kdata=llcandle.get_kdata();
                lll_kdata=lllcandle.get_kdata();
                lrate=round((l_kdata['close']-ll_kdata['open'])/ll_kdata['open'],2)
                llrate=round((ll_kdata['close']-lll_kdata['open'])/lll_kdata['open'],2)
                candledata=candle.get_kdata()
                # 上涨趋势
                if (lrate>0)&(llrate>0):
                    if (l_kdata['close']) < (candledata['open']):
                            shootstar.setdefault(position, candle)
            position += 1
        # print(len(shootstar))
        print(">>>>>流星线>>>>>>")
        if len(shootstar)!=0:

            for key in shootstar.keys():
                candle = shootstar[key]
                candle.print_candle()
            print("观察得股市行情由原来的升转跌")
        else:
            print("当前时间段内无流星线形态")
        return shootstar

    def find_bullishPiercingPattern(self):
        '多方突破形态（曙光初现）:两日k线形态，左侧长阴线，右侧 低开(开盘价低于大阴线最低价) 长阳线，并且收盘价深入长阴线实体一半位置'
        # 找出所有的大阴线
        print("多方突破形态（曙光初现）:两日k线形态，左侧长阴线，右侧 低开(开盘价低于大阴线最低价) 长阳线，并且收盘价深入长阴线实体一半位置")
        bullish_piercing=[]
        maxnegatives=self.find_maxnegatives()
        for position in maxnegatives.keys():
            maxpositive=self._candles[position-1]
            maxnegative=self._candles[position]
            if maxpositive.is_maxpositive():
                negaKdata=maxnegative.get_kdata()
                posiKdata=maxpositive.get_kdata()

                negaOpen=negaKdata['open']
                negaClose=negaKdata['close']
                negaLow=negaKdata['low']
                posiClose=posiKdata['close']
                posiOpen=posiKdata['open']

                flag=round((posiClose-negaClose)/(negaOpen-negaClose),2)

                if (flag>=0.5)&(posiOpen<negaLow):
                    pattern=BullishPiercingPattern(maxnegative,maxpositive)
                    pattern.print_pattern()
                    bullish_piercing.append(pattern)

        if len(bullish_piercing)!=0:
            for pattern in bullish_piercing:
                pattern.print_pattern
        else:
            print("当前时间段内不存在多头突破形态,请更换时间段或者股票（上证指数2008.10.28）")
        return bullish_piercing

    def find_bullishEngulfingPattern(self):
        '多头吞噬形态：两日k线形态由一根小阴线和大阳线组成，大阳线实体完全覆盖小阴线,一般在下跌趋势中'
        print("多头吞噬形态：两日k线形态由一根小阴线和大阳线组成，大阳线实体完全覆盖小阴线,一般在下跌趋势中")
        bullishEngulfing=[]
        midnegatives=self.find_midnegatives()
        for position in midnegatives.keys():
            midnegative=self._candles[position]
            maxpositive=self._candles[position-1]
            if maxpositive.is_maxpositive():
                lcandle=self._candles[position+1]
                llcandle=self._candles[position+2]
                lllcandle=self._candles[position+3]
                l_kdata = lcandle.get_kdata();
                ll_kdata = llcandle.get_kdata();
                lll_kdata = lllcandle.get_kdata();
                lrate = round((l_kdata['close'] - ll_kdata['open']) / ll_kdata['open'], 2)
                llrate = round((ll_kdata['close'] - lll_kdata['open']) / lll_kdata['open'], 2)
                # 判断下跌趋势
                if (lrate<0)&(llrate<0):
                    negaKdata=midnegative.get_kdata();
                    posiKdata=maxpositive.get_kdata();
                    negaOpen = negaKdata['open']
                    negaClose = negaKdata['close']
                    posiClose = posiKdata['close']
                    posiOpen = posiKdata['open']

                    if (posiOpen<negaClose)&(posiClose>negaOpen):
                        pattern=BullishEngulfingPattern(midnegative,maxpositive)
                        pattern.print_pattern()
                        bullishEngulfing.append(pattern)

        if len(bullishEngulfing) != 0:
            for pattern in bullishEngulfing:
                pattern.print_pattern
        else:
            print("当前时间段内不存在多头吞噬形态,请更换时间段或者股票")

        return bullishEngulfing

    def find_bearishEngulfingPattern(self):
        '空头吞噬形态：两日k线形态，一根较短阳线，一根较长阴线，大阴线实体完全覆盖小阳线实体，一般在上升趋势中'
        print("空头吞噬形态：两日k线形态，一根较短阳线，一根较长阴线，大阴线实体完全覆盖小阳线实体，一般在上升趋势中")
        bearishEngulfing=[]
        midpositives=self.find_midpositives()
        for position in midpositives.keys():
            midpositive = self._candles[position]
            maxnegative = self._candles[position - 1]
            if maxnegative.is_maxnegative():
                lcandle = self._candles[position + 1]
                llcandle = self._candles[position + 2]
                lllcandle = self._candles[position + 3]
                l_kdata = lcandle.get_kdata();
                ll_kdata = llcandle.get_kdata();
                lll_kdata = lllcandle.get_kdata();
                lrate = round((l_kdata['close'] - ll_kdata['open']) / ll_kdata['open'], 2)
                llrate = round((ll_kdata['close'] - lll_kdata['open']) / lll_kdata['open'], 2)
                # 判断上升趋势
                if (lrate > 0) & (llrate > 0):
                    negaKdata = maxnegative.get_kdata();
                    posiKdata = midpositive.get_kdata();
                    negaOpen = negaKdata['open']
                    negaClose = negaKdata['close']
                    posiClose = posiKdata['close']
                    posiOpen = posiKdata['open']

                    if (posiOpen > negaClose) & (posiClose < negaOpen):
                        pattern = BullishEngulfingPattern(midpositive, maxnegative)
                        pattern.print_pattern()
                        bearishEngulfing.append(pattern)

        if len(bearishEngulfing) != 0:
            for pattern in bearishEngulfing:
                pattern.print_pattern
        else:
            print("当前时间段内不存在空头吞噬形态,请更换时间段或者股票")
        return bearishEngulfing

    def find_bullishCounterattackPattern(self):
        '多头反击形态：在上涨趋势中如果出现第一根大阳线后又出现了一根高高跳空高开的大阴线，并且该阴线的收盘价和前一根阳线的收盘价是相同的'
        bullishCounterattack=[]
        maxpositives=self.find_maxpositives()
        print("多头反击形态：在上涨趋势中如果出现第一根大阳线后又出现了一根高高跳空高开的大阴线，并且该阴线的收盘价和前一根阳线的收盘价是相同的")
        for position in maxpositives.keys():
            maxpositive = self._candles[position]
            if position==0:
                continue
            maxnegative = self._candles[position - 1]
            if maxnegative.is_maxnegative():
                lcandle = self._candles[position + 1]
                llcandle = self._candles[position + 2]
                lllcandle = self._candles[position + 3]
                l_kdata = lcandle.get_kdata();
                ll_kdata = llcandle.get_kdata();
                lll_kdata = lllcandle.get_kdata();
                lrate = round((l_kdata['close'] - ll_kdata['open']) / ll_kdata['open'], 2)
                llrate = round((ll_kdata['close'] - lll_kdata['open']) / lll_kdata['open'], 2)

                # 判断上升趋势
                if (lrate > 0) & (llrate > 0):
                    negaKdata = maxnegative.get_kdata();
                    posiKdata = maxpositive.get_kdata();
                    negaClose = negaKdata['close']
                    posiClose = posiKdata['close']

                    if negaClose==posiClose:
                        pattern = BullishCounterattackPattern(maxpositive, maxnegative)
                        pattern.print_pattern()
                        bullishCounterattack.append(pattern)
        if len(bullishCounterattack) != 0:
            for pattern in bullishCounterattack:
                pattern.print_pattern
        else:
            print("当前时间段内不存在多头反击形态,请更换时间段或者股票")
        return bullishCounterattack

    def find_bearishCounterattackPattern(self):
        "空头反击形态：如果在下降趋势中出现了一根大跌的大阴线而后一天又出现了一根大幅低开的大阳线，并且这根阳线的收盘价与上一根阴线的收盘价相吻合"
        bearishCounterattack=[]
        maxnegatives = self.find_maxnegatives()
        print("空头反击形态：如果在下降趋势中出现了一根大跌的大阴线而后一天又出现了一根大幅低开的大阳线，并且这根阳线的收盘价与上一根阴线的收盘价相吻合")
        for position in maxnegatives.keys():
            maxnegative = self._candles[position]
            maxpositive = self._candles[position - 1]

            if maxpositive.is_maxpositive():
                lcandle = self._candles[position + 1]
                llcandle = self._candles[position + 2]
                lllcandle = self._candles[position + 3]
                l_kdata = lcandle.get_kdata();
                ll_kdata = llcandle.get_kdata();
                lll_kdata = lllcandle.get_kdata();
                lrate = round((l_kdata['close'] - ll_kdata['open']) / ll_kdata['open'], 2)
                llrate = round((ll_kdata['close'] - lll_kdata['open']) / lll_kdata['open'], 2)

                # 判断下降趋势
                if (lrate < 0 )& (llrate < 0):
                    negaKdata = maxnegative.get_kdata();
                    posiKdata = maxpositive.get_kdata();
                    negaClose = negaKdata['close']
                    posiClose = posiKdata['close']

                    if negaClose == posiClose:
                        pattern = BearishCounterattackPattern(maxnegative, maxpositive)
                        pattern.print_pattern()
                        bearishCounterattack.append(pattern)

        if len(bearishCounterattack) != 0:
            for pattern in bearishCounterattack:
                pattern.print_pattern
        else:
            print("当前时间段内不存在空头反击形态,请更换时间段或者股票")
        return bearishCounterattack


class BullishPiercingPattern:
    '多头突破形态'
    def __init__(self,negaCandle,posiCandle):
        self._pattern=[negaCandle,posiCandle]
    def trend(self):
        return False
    def print_pattern(self):
        print(">>>>多头反击形态>>>>")
        for candle in self._pattern:
            candle.print_candle()
class BullishEngulfingPattern:
    '多头吞噬形态'
    def __init__(self,midnegaCandle,maxPosiCandle):
        self._pattern=[midnegaCandle,maxPosiCandle]
    def print_pattern(self):
        print(">>>>多头吞噬形态>>>>")
        for candle in self._pattern:
            candle.print_candle()
class BearishEngulfingPattern:
    '空头吞噬形态'
    def __init__(self, midposiCandle, maxnegaCandle):
        self._pattern = [midposiCandle, maxnegaCandle]

    def print_pattern(self):
        print(">>>>空头吞噬形态>>>>")
        for candle in self._pattern:
            candle.print_candle()
class BullishCounterattackPattern:
    '多头反击形态'
    def __init__(self, maxposiCandle, maxnegaCandle):
        self._pattern = [maxposiCandle, maxnegaCandle]

    def print_pattern(self):
        print(">>>>多头反击形态>>>>")
        for candle in self._pattern:
            candle.print_candle()
class BearishCounterattackPattern:
    '空头反击形态：'
    def __init__(self,maxnegaCandle,maxposiCandle):
        self._pattern=[maxnegaCandle,maxposiCandle]
    def print_pattern(self):
        print(">>>>空头反击形态>>>>")
        for candle in self._pattern:
            candle.print_candle()
class Morningstar:
    def __init__(self, lcandle, mcandle, rcandle):
        self._mornstar = [lcandle, mcandle, rcandle]

    def trend(self):
        '趋势分析'
        return False

    def print_morningstar(self):
        for candle in self._mornstar:
            candle.print_candle()

    def check(self):
        '第一次修正'
        # 较长阴线
        lcandle = self._mornstar[0]

        # 较长阳线 实体部分超出阴线回升趋势大,
        rcandle = self._mornstar[2]
        lflag = (lcandle.get_ocrate() >= 0.03)
        rflag = (rcandle.get_ocrate() >= 0.03)

        return rflag & lflag
class Eveningstar:
    def __init__(self, candle1, candle2, candle3):
        self._evenstar = [candle1, candle2, candle3]

    def trend(self):
        '趋势分析'
        return False

    def print_eveningstar(self):
        for candle in self._evenstar:
            candle.print_candle()

    def check(self):
        '第一次修正'
        # '右侧阴线波动大于0.03即为非小阴线'
        rcandle = self._evenstar[2]
        return rcandle.get_ocrate() >= 0.03
class Darkcloudcover:
    def __init__(self, candle1, candle2):
        self._darkcloud = [candle1, candle2]

    def trend(self):
        return False

    def print_darkcloud(self):
        for candle in self._darkcloud:
            candle.print_candle()
class Holdline1:
    def __init__(self, candle1, candle2):
        '阴抱阳'
        self._holdlines = [candle1, candle2]

    def print_holdlines(self):
        if len(self._holdlines) == 0:
            print("未出现阳抱阴线")
        else:
            for candle in self._holdlines:
                candle.print_candle()

    def trend(self):
        print()
class Holdline0:
    '阳抱阴'

    def __init__(self, candle1, candle2):
        self._holdlines = [candle1, candle2]

    def print_holdlines(self):
        if len(self._holdlines) == 0:
            print("未出现阳抱阴线")
        else:
            for candle in self._holdlines:
                candle.print_candle()

    def trend(self):
        print()
