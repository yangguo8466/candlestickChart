# k线图绘制描述当日最高价与当日最低价
# 开盘低于收盘时显示盈利红，开盘低于收盘时显示亏损绿

# 绘制方法
# 首先我们找到该日或某一周期的最高和最低价，垂直地连成一条直线
# 然后再找出当日或某一周期的开市和收市价，把这二个价位连接成一条狭长的长方柱体
# 假如当日或某一周期的收市价较开市价为高（即低开高收），我们便以红色来表示，或是在柱体上留白，这种柱体就称之为"阳线"
# 如果当日或某一周期的收市价较开市价为低（即高开低收），我们则以绿色表示，又或是在住柱上涂黑色，这柱体就是"阴线"

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from numpy import *
from matplotlib.dates import DateFormatter, DayLocator, num2date
from matplotlib.finance import candlestick_ohlc as candle1
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.path import Path
from CandlestickCharts.FetchStockData import StockInMongo

def candle_chart1(stock):
    'draw candlestick chart'
    fig = plt.figure(facecolor='black')
    plt.style.use('dark_background')

    # 获取子图对象
    ex = fig.add_subplot(1, 1, 1)

    # 绘制日k线图
    candle1(ex, stock.ohlc_quotes(), width=1, colorup='r', colordown='g')

    # 设置刻度格式%y-%m-%d,每次间隔15天
    ex.xaxis.set_major_locator(DayLocator(bymonthday=range(1, 32), interval=15))
    ex.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    # 获得股票开盘日期
    dates = stock.get_dates()

    ex.set_xlim(dates.min(), dates.max())
    print("重复获取数据待处理")

    # 设置刻度
    for label in ex.xaxis.get_ticklabels():
        label.set_rotation(45)

    ex.set_ylabel("price")
    ex.set_title(stock.get_stockname())
    plt.grid(True)
    plt.show()

def candle_with_MTM(code,width=0.5,timelength=6):
    """
    :param stock: 股票代码
    :param timeLength: 时间跨度
    :return:

    """
    fig = plt.figure(facecolor='black')
    plt.style.use('dark_background')
    ax = fig.add_subplot(2, 1, 1)
    stockmongo=StockInMongo(code,timelength)
    stocklist=stockmongo.get_stocklist()

    for candle in stocklist:

        date = candle['date']
        open = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']

        verts = [(date - width, open),
                 (date - width, close),
                 (date + width, close),
                 (date + width, open),
                 (date - width, open)]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY]

        path = Path(verts, codes)

        if open<=close:
            patch = patches.PathPatch(path, facecolor='r', edgecolor='r')
            ax.plot([date, date], [low, high], color='r')
        else:
            patch = patches.PathPatch(path, facecolor='g', edgecolor='g')
            ax.plot([date, date], [low, high], color='g')

        ax.add_patch(patch)

     # 格式化刻度信息 设置刻度格式%y-%m-%d,每次间隔30天
    ax.xaxis.set_major_locator(DayLocator(bymonthday=range(1, 32), interval=30))
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(10)

    dates = stockmongo.get_dates()
    lows = stockmongo.get_lows()
    highs=stockmongo.get_highs()

    ax.set_ylim(lows.min()-5, highs.max()+5)
    ax.set_xlim(dates.min(), dates.max())

    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(30)

    ax.set_ylabel("price")
    ax.set_title(code)
    plt.grid(True)

    ex=fig.add_subplot(2, 1, 2)
    poordata=stockmongo.get_poorMtm()
    pmtm=poordata['mtms']
    dateMtm = poordata["dates"]
    poorMtm = plt.plot(dateMtm, pmtm, color='b',label="poor-MTM")
    plt.legend(loc=2)

    # 设置为次坐标轴
    ex2=ex.twinx()
    dmtm=stockmongo.get_divisionMtm()['mtms']
    divisionMtm=plt.plot(dateMtm,dmtm,color='g',label="division-MTM")
    plt.legend(loc=1)
    ex.xaxis.set_major_locator(DayLocator(bymonthday=range(1, 32), interval=30))
    ex.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    for label in ex.xaxis.get_ticklabels():
        label.set_rotation(30)
    for tick in ex.xaxis.get_major_ticks():
        tick.label1.set_fontsize(10)
    ex.set_xlim(dates.min(), dates.max())
    plt.grid(True)
    plt.show()

def candle_chart2(stockdata, width):
    """
    draw candlesticks by auto define function
    candles:  Candlestick type
    width: width of rectangle
    dates: Stock‘s dates
    """
    candles = stockdata.transform_candles()

    fig = plt.figure(facecolor='black')
    plt.style.use('dark_background')

    canvas = FigureCanvas(fig)

    ax = fig.add_subplot(1, 1, 1)
    print(len(candles))
    for candle in candles:

        mapdata = candle.get_kdata()
        date = mapdata['date']
        open = mapdata['open']
        high = mapdata['high']
        low = mapdata['low']
        close = mapdata['close']

        verts = [(date - width, open),
                 (date - width, close),
                 (date + width, close),
                 (date + width, open),
                 (date - width, open)]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY]

        path = Path(verts, codes)
        if candle.is_positive():
            patch = patches.PathPatch(path, facecolor='r', edgecolor='r')
            ax.plot([date, date], [low, high], color='r')
        else:
            patch = patches.PathPatch(path, facecolor='g', edgecolor='g')
            ax.plot([date, date], [low, high], color='g')

        ax.add_patch(patch)

    # 格式化刻度信息 设置刻度格式%y-%m-%d,每次间隔30天
    ax.xaxis.set_major_locator(DayLocator(bymonthday=range(1, 32), interval=30))
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    dates = stockdata.get_dates()
    lows = stockdata.get_lows()
    ax.set_ylim(5, 20)
    ax.set_xlim(dates.min(), dates.max())
    print(type(dates))
    # print("重复获取数据")

    # 设置刻度样式
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)

    ax.set_ylabel("price")
    ax.set_title(stockdata.get_stockname())
    plt.grid(True)
    plt.show()
