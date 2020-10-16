#!/usr/bin/env python

'''
Basic verus calculator for mining and staking. 

Requires verusrpc.py (included in this repo) and configuration via rpc_api.conf

Written 2020 by Jonathan Barnes <j@jbsci.dev>
'''

#-# Imports #-#

import sys
import verusrpc as vrpc
from flask import Flask, request
from flask_api import FlaskAPI, status, exceptions 
from flask_sslify import SSLify
from flask_talisman import Talisman

#--# Definitions #--#

app = FlaskAPI(__name__)

#---# Configuration #---#

class readconfig:
    def __init__(self):
        for line in open('rpc_api.conf', 'r'):
            if line.find('#') >= 0:
                line = line.split('#')[0]
            line = line.strip()
            if len(line) > 0:
                segments = line.split('=')
                inparam = segments[0].strip()
                inval = segments[1].strip()
                if inparam == 'apiport':
                    self.port = int(inval)
                elif inparam == 'apihost':
                    self.host = inval
                elif inparam == 'SSL':
                    if inval.upper() == 'YES':
                        self.ssl = True
                    else:
                        self.ssl = False
                elif inparam == 'SSL_KEY':
                    self.sslkey = inval
                elif inparam == 'SSL_CRT':
                    self.sslcrt = inval

apiconf = readconfig()

if apiconf.ssl:
    Talisman(app)
    if apiconf.sslkey == 'none' or apiconf.sslcrt == 'none':
        sys.exit('ERROR: SSL enabled but no key or cert specified')
    context = (apiconf.sslcrt, apiconf.sslkey)
    sslify = SSLify(app)

#----# Functions #----#

def getcurrentstate(param, rpcid='getstate'):
    '''
    Uses given rpc method to get current state information. 

    Parameter value can be either staking (current supply estimate) or mining (current network hashrate)
    '''
    result = vrpc.verusquery('getmininginfo', [], rpcid=rpcid)
    if param == 'staking':
        stake_supply = result['result']['stakingsupply']
        return stake_supply
    elif param == 'mining':
        networkhashrate = result['result']['networkhashps']
        return float(networkhashrate) / 1024 / 1024

def stakemath(balance):
    '''
    Currently just provides simple estimates
    '''
    current = float(getcurrentstate('staking'))
    bal = float(balance)
    perc = bal / current
    daily = perc * 720
    weekly = daily * 7
    yearly = daily * 365.25
    monthly = yearly / 12
    return perc, daily, weekly, monthly, yearly 

def minemath(hashrate):
    '''
    Currently provides only simple estimates
    '''
    current_net_mh = float(getcurrentstate('mining')) 
    input_hashrate = float(hashrate)
    perc = input_hashrate / current_net_mh
    daily = perc * 720
    weekly = daily * 7
    yearly = daily * 365.25
    monthly = yearly / 12
    return perc, daily, weekly, monthly, yearly 

#-----# API #-----#

@app.route("/")
def index():
    return """
    <h1>Welcome to the Verus calculator API</h1>
    <h4> Current estimated supply: {:f} </h4> 
    <h4> Current network hashrate {:f} GH/s </h4> 
    <p> Staking calculator: <code> /stake/?balance=[balance] </code> </p>
    <p> Mining calculator: <code> /mine/?hashrate=[hashrate (MH/s)] </code> </p>
    """.format(getcurrentstate('staking'), getcurrentstate('mining') / 1024)

@app.route("/stake/", methods=["GET"])
def staking_calc():
    keys = list(request.args.keys())
    if 'balance' not in keys:
        return {"error" : 2, "error_detail" : "No balance specified"},400
    else:
        perc, daily, weekly, monthly, yearly = stakemath(request.args['balance'])
        return { "percentage" : perc, "daily" : daily, "weekly" : weekly, "monthly" : monthly, "yearly" : yearly}


@app.route("/mine/", methods=["GET"])
def mining_calc():
    keys = list(request.args.keys())
    if 'hashrate' not in keys:
        return {"error" : 2, "error_detail" : "No hashrate specified"},400
    else:
        perc, daily, weekly, monthly, yearly = minemath(request.args['hashrate'])
        return { "percentage" : perc, "daily" : daily, "weekly" : weekly, "monthly" : monthly, "yearly" : yearly}


#------# Run #------#

if __name__ == '__main__':
    if apiconf.ssl:
        context = (apiconf.sslcrt, apiconf.sslkey)
        app.run(host=apiconf.host, port=apiconf.port, ssl_context = context)
    else:
        app.run(host=apiconf.host, port=apiconf.port)
