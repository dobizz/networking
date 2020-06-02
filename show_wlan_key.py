#!/usr/bin/python

import subprocess
import os
import re
import qrcode

def make_wifi_qr(ssid, password, auth):
    if auth is None:
        auth = "WPA"  
    data = f"WIFI:S:{ssid};T:{auth};P:{password};;"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    print("\n\n\tSCAN CODE TO CONNECT\n")
    qr.print_ascii(invert=True)
       
def query_net_key(network: str) -> str:
    cmd = f'netsh wlan show profile name="{network}" key=clear'
    try:
        results = subprocess.check_output(cmd)
        key = re.findall(r'Key Content\s+:\s+(.+?)\\r\\n\\r', str(results))[0]
        auth = re.findall(r'Authentication[ ]+:[ ]+([a-zA-Z0-9-_]+)', str(results))[0]
        if 'WPA' in auth:
            auth = 'WPA'
        elif 'WEP' in auth:
            auth = 'WEP'
        return (key, auth)
    except:
        return (None, None)
       
def list_networks() -> None:
    cmd = 'netsh wlan show profile'
    results = subprocess.check_output(cmd)
    return re.findall(r'All User Profile\s+:\s+(.+?)\\r\\n', str(results))

def main() -> None:
    while True:
        os.system('cls')
        print('Available Networks:\n')
        networks = list_networks()
        
        print(f'\t.:ID:.\t.:Wireless SSID:.')
        for index, network in enumerate(networks):
            print(f'\t {index} \t: {network}')
        
        try:
            choice = int(input("\nEnter ID [-1 to Exit]: "))
        except:
            continue
        else:
            if choice < 0:
                break
                
        network = networks[choice]
        key, auth = query_net_key(network)
        
        os.system('cls')
        
        print(f'\nThere is no network key cached for {network}' if key is None \
            else f'\nThe network key for {network} is: {key}')
        
        if key:
            make_wifi_qr(network, key, auth)
        
        # clear screen
        input("\nPress ENTER to continue ...\n")
    os.system('cls')
    
if __name__ == '__main__':
    if os.name == 'nt':
        main()
    else:
        print('Sorry, this program is only for Windows')