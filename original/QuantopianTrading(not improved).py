# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 10:32:29 2020

@author: BCK10G_B
"""

def initialize(context):
    # AA
    context.aa = [sid(50428)]
 
def handle_data(context, data):
    close_history = data.history(context.aa, fields="close", bar_count=3, frequency="1d")
    
    for s in context.aa:
        prev_aa_close_bar = close_history[s][-3]
        yest_aa_close_bar = close_history[s][-2]
        curr_aa_close_bar = close_history[s][-1]
        
    open_history = data.history(context.aa, fields="open", bar_count=3, 
frequency="1d")
    
    for s in context.aa:
        prev_aa_open_bar = open_history[s][-3]
        yest_aa_open_bar = open_history[s][-2] 
        
        if prev_aa_open_bar < yest_aa_open_bar and prev_aa_open_bar < yest_aa_close_bar and prev_aa_close_bar < yest_aa_open_bar and prev_aa_close_bar > yest_aa_open_bar : 
         order_target_percent( sid(50428), 1.0)        
        elif prev_aa_open_bar < yest_aa_open_bar and prev_aa_open_bar < yest_aa_close_bar and prev_aa_close_bar < yest_aa_open_bar and prev_aa_close_bar < yest_aa_open_bar : 
         order_target_percent( sid(50428), 1.0)        
        elif prev_aa_open_bar < yest_aa_open_bar and prev_aa_open_bar < yest_aa_close_bar and prev_aa_close_bar > yest_aa_open_bar and prev_aa_close_bar < yest_aa_close_bar : 
         order_target_percent( sid(50428), 1.0)
        elif prev_aa_open_bar > yest_aa_open_bar and prev_aa_open_bar < yest_aa_close_bar and prev_aa_close_bar < yest_aa_open_bar and prev_aa_close_bar < yest_aa_close_bar : 
         order_target_percent( sid(50428), 1.0)
        elif prev_aa_open_bar < yest_aa_open_bar and prev_aa_open_bar > yest_aa_close_bar and prev_aa_close_bar < yest_aa_open_bar and prev_aa_close_bar < yest_aa_close_bar :              order_target_percent( sid(50428), 1.0)
        elif curr_aa_close_bar < yest_aa_close_bar :
         order_target_percent( sid(50428), 0)
        
        if prev_aa_open_bar < yest_aa_open_bar and prev_aa_open_bar > yest_aa_close_bar and prev_aa_close_bar > yest_aa_open_bar and prev_aa_close_bar > yest_aa_open_bar : 
         order_target_percent( sid(50428), -1.0)
        
        elif prev_aa_open_bar > yest_aa_open_bar and prev_aa_open_bar > yest_aa_close_bar and prev_aa_close_bar > yest_aa_open_bar and prev_aa_close_bar > yest_aa_open_bar : 
         order_target_percent( sid(50428), -1.0)
 
        elif prev_aa_open_bar > yest_aa_open_bar and prev_aa_open_bar < yest_aa_close_bar and prev_aa_close_bar > yest_aa_open_bar and prev_aa_close_bar > yest_aa_open_bar : 
         order_target_percent( sid(50428), -1.0)
 
        elif prev_aa_open_bar > yest_aa_open_bar and prev_aa_open_bar > yest_aa_close_bar and prev_aa_close_bar > yest_aa_open_bar and prev_aa_close_bar < yest_aa_open_bar : 
         order_target_percent( sid(50428), -1.0)
        
        elif prev_aa_open_bar > yest_aa_open_bar and prev_aa_open_bar > yest_aa_close_bar and prev_aa_close_bar < yest_aa_open_bar and prev_aa_close_bar < yest_aa_open_bar : 
         order_target_percent( sid(50428), -1.0)
        elif curr_aa_close_bar > yest_aa_close_bar :
         order_target_percent( sid(50428), 0)