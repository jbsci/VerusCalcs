'''
Simple wrapper to query the verus RPC client and perform various operations. 

Needs configuration specified for RPC authentication, either with the verus 
RPC configuration file path or user input dictionary formatted as follows:
    
    { "rpcuser" : "$username", "rpcpassword" : "$rpcpassword", "rpcport" : $port } 

Written 2020 by Jonathan Barnes <j@jbsci.dev>
'''

#-# imports #-#

import sys
import requests
import ast
from requests.auth import HTTPBasicAuth

#--# Configuration #--#

#modify rpc_api.conf
class readconfig:
    '''Reads configuration file and stores relevant information'''
    def __init__(self):
        for line in open('rpc_api.conf', 'r'):
            if line.find('#') >= 0:
                line = line.split('#')[0]
                if len(line) > 0:
                    segments = line.split("=")
                    inparam  = segments[0].strip()
                    inval    = segments[1].strip()
                    if inparam  == 'rpcconf':
                        if inval[0] == "{" and inval[-1] == "}":
                            self.rpcconf = ast.literal_eval(inval)
                        elif inval == 'none':
                            sys.exit('ERROR: Please specify an rpc config file or path to config file in rpc_api.conf')
                        else:
                            self.rpcconf = inval
                    elif inparam == 'rpchost':
                        self.rpchost = inval

rpcconfig = readconfig()

#---# Functions #---#

def rpcdetails(conffile):
    '''
    Reads in config file and stores in dictionary for use.

    If conf is given as a dictionary to start, will just return.
    '''
    if type(conffile) == dict:
        return conffile
    elif len(conffile) == 0:
        return "ERROR: Specify a configuration file with RPC login information"
    return { line.split('=')[0] : line.split('=')[1].strip('\n') for line in open(conffile, 'r')}

def verusquery(method, params, rpcid= " ", rpcinfo=rpcdetails(rpcconfig.rpcconf), host=rpcconfig.rpchost):
    '''
    Function to query the Verus RPC client. Builds payload based on method and parameters.
    
    Default configuration is from the confpath specified above.
    '''
    if type(params) != list:
        print("ERROR: Params must be given as a list")
    payload = {"jsonrpc" : "1.0", "id": rpcid , "method" : method, "params": params}
    response = requests.post(host+':'+ rpcinfo['rpcport'], json=payload, headers={'content-type': 'text/plain;'}, auth=HTTPBasicAuth(rpcinfo['rpcuser'], rpcinfo['rpcpassword'])).json()
    return response


#----# Run #----#

if __name__ == '__main__':
    pass
