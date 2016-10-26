# 获取数据
# 导入数据到数据库
# 绘制k线图
# 方法二自定义方法绘图
# 获取数据data从tushare接口
import CandlestickCharts.FetchStockData as Fsd
import CandlestickCharts.Analyse as an
import CandlestickCharts.DrawChart as draw
# data = Fsd.StockData(ticket='000001', start='2015-04-02', end='2016-05-08')
# 插入数据到mongodb
# # data.insert_mongo()
# k=an.AnalyseK(data)
#
# # k.find_holdline()
# # k.find_morningstars()
# # k.find_eveningstars()
# # k.find_darkcloud()
#
# # 纺锤线
# k.find_spinning_tops()
#
# # 高浪线
# k.find_high_wave()
#
# # 锤线
# k.find_hammer()
#
# # 上吊线
# k.find_hanging_man()
#
# # 射击之星（流星线）
# k.find_shooting_star()
#
# # 多头突破（曙光初现）
# k.find_bullishPiercingPattern()
#
# # 多头吞噬
# k.find_bullishEngulfingPattern()
#
# # 多头反击
# k.find_bullishCounterattackPattern()
#
# # 空头反击
# k.find_bearishCounterattackPattern()
#
# # 空头吞噬
# k.find_bearishEngulfingPattern()

# 自定义绘图
# draw.candle_chart2(data,0.5)
draw.candle_with_MTM('600131',width=0.5,timelength=12)