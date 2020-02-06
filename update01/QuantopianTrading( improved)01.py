# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 12:09:42 2020

@author: BCK10G_B
"""

"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
#algo
import quantopian.algorithm as algo
#create pipline
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.data import EquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.experimental import risk_loading_pipeline
from quantopian.pipeline.factors import CustomFactor
from quantopian.pipeline.factors import Returns
from quantopian.pipeline.factors import AverageDollarVolume
#optimize
import quantopian.optimize as opt
#pandas and numphy
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
 
# Constraint parameters
MAX_GROSS_LEVERAGE = 1.0        # Only use capital from our portfolio
MAX_SHORT_POSITION_SIZE = 0.04  # 5%
MAX_LONG_POSITION_SIZE = 0.04   # 5%
 
# pre-declared inputs and window length
class OpenBeforeYesterday(CustomFactor):
    inputsOpen = [USEquityPricing.open]
    window_length=2
    def compute(self, today ,assets, out, open):
        out[:]=open[0]
        
class OpenYesterday(CustomFactor):
    inputsOpen = [USEquityPricing.open]
    window_length=2
    def compute(self, today ,assets, out, open):
        out[:]=open[1]
 
class CloseBeforeYesterday(CustomFactor):
    inputsClose = [USEquityPricing.close]
    window_length=2
    def compute(self, today ,assets, out, close):
        out[:]=close[0]
        
class CloseYesterday(CustomFactor):
    inputsClose = [USEquityPricing.close]
    window_length=2
    def compute(self, today ,assets, out, close):
        out[:]=close[1]
 
class ValueDaybeforeYesterday(CustomFactor):
    window_length = 2
    def compute(self, today, assets, out, values):
        out[:] = values[0]    
 
class ChangeAverage(CustomFactor):
    def compute(self, today, assets, out, values):
        mean = pd.DataFrame(values).pct_change().mean()
        out[:] = mean.values
        
class ChangeAverageLog(CustomFactor):
    def compute(self, today, assets, out, values):
        df = pd.DataFrame(values)
        mean = (df.shift(1) / df).mean().apply(np.log)
        out[:] = mean.values
 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # Constraint parameters
    '''
    context.max_leverage = 1.0
    context.max_pos_size = (1.0 / context.m)
    context.max_turnover = 0.95
    '''
    context.max_turnover = 0.95
    # set commission and slippage
    '''
    set_commission(commission.PerShare(cost=0.0075, min_trade_cost=1))
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.1, price_impact=0.1))
    '''
 
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )
 
    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )
 
    # Create our dynamic stock selector.
    algo.attach_pipeline(make_pipeline(), 'pipeline')
    
    algo.attach_pipeline(
        risk_loading_pipeline(),
        'risk_pipe'
    )
def make_pipeline():
    pipe = Pipeline()
    # Base universe set to the QTradableStocksUS
    base_universe = QTradableStocksUS()
    #AverageDollarVolume
    dollar_volume = AverageDollarVolume(window_length=30)
    high_dollar_volume = dollar_volume.percentile_between(99, 100)
    # Factor of yesterday's close price.
    yesterday_close = USEquityPricing.close.latest
    #price
    latest_close = EquityPricing.close.latest
    above_10 = latest_close > 10
    
    #LongPattern
    LongPattern = (CloseYesterday(inputs = [USEquityPricing.close]) - CloseBeforeYesterday(inputs =[USEquityPricing.close])) / (CloseYesterday(inputs = [USEquityPricing.close])) 
    
    #pipe.add(LongPattern, 'LongPattern')
    #LongPatternZscore
    LongPattern_Zscore = LongPattern.zscore()
    high_returns = LongPattern_Zscore.percentile_between(99,100)
    low_returns = LongPattern_Zscore.percentile_between(0,99)
    
    #securities_to_trade
    securities_to_trade = (high_returns | low_returns )
    
    #volume
    volume_day_before_yeseterday = ValueDaybeforeYesterday(inputs =[USEquityPricing.volume])
    volume_change_mean = ChangeAverage(inputs = [USEquityPricing.volume], window_length = 5)        
    my_screen = base_universe  & high_dollar_volume & securities_to_trade & above_10
    
    pipe.set_screen(my_screen)
    return pipe
 
 
def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    Results = context.output = algo.pipeline_output('pipeline')
    context.risk_factor_betas = algo.pipeline_output('risk_pipe')
    #print(results)
    #update
    #AfterResults = results.sort_values(by = 'LongPattern',axis = 0,ascending = False)
    #print(AfterResults)
    
    # These are the securities that we are interested in trading each day.
    context.security_list = Results.index
    #context.StocksIndex = AfterResults.head(25).index
    context.stocks = Results.index.tolist()
    
    #print(context.security_list.dtype)
    context.m = len(context.stocks)
    
def compute_weights(context,data):
     
    """
    Calculate the ideal weights for the portfolio
    """
    # Initialize lists and variables
    context.longs = []
    context.shorts = []
    weights = {}
    
    for stock in context.security_list:
    
        # When to go long
        if stock > 0:
            context.longs.append(stock)
            
        # When to go short
        if stock < 0:
            context.shorts.append(stock)
            
        if len(context.longs) > 0:
            weights[stock] = 0.4 / (len(context.longs))
            
        if len(context.shorts) > 0:
            weights[stock] = - 0.4 / (len(context.shorts))
    
    for stock in context.portfolio.positions:
        if stock not in context.security_list:
            weights[stock] = 0.0
            
            
            
    return weights
    
 
def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    weights = compute_weights(context, data)
    # Optimize API variables
    objective = opt.TargetWeights(weights)
    
    leverage_constraint = opt.MaxGrossExposure(MAX_GROSS_LEVERAGE)
    
    max_turnover = opt.MaxTurnover(context.max_turnover)
    
    factor_risk_constraints = opt.experimental.RiskModelExposure(
            context.risk_factor_betas,
            version=opt.Newest
        )
    
    position_size = opt.PositionConcentration.with_equal_bounds(
        -MAX_SHORT_POSITION_SIZE,
        MAX_LONG_POSITION_SIZE,
    )
    
    market_neutral = opt.DollarNeutral()
    
    algo.order_optimal_portfolio(
        objective = objective,
        constraints = [
            leverage_constraint,
            position_size,
            market_neutral,
            max_turnover,
            factor_risk_constraints,
        ],
    )
   
    
def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass