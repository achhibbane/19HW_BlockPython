import subprocess

import json

from dotenv import load_dotenv

import os

from constants import *

from web3 import Web3

import web3

from eth_account import Account

import bit

from bit.network import NetworkAPI

load_dotenv()

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

#MAC users
## command = './derive -g --mnemonic="few patrol rubber bone blush hour fox tunnel duty tattoo lens retreat" --cols=path,address,privkey,pubkey --format=json'

mnemonic = os.getenv('MNEMONIC')
# Windows users
# command = 'php derive -g --mnemonic="few patrol rubber bone blush hour fox tunnel duty tattoo lens retreat" --cols=path,address,privkey,pubkey'



def derive_wallets(mnemonic=mnemonic, coin=BTC, depth=3):
    command = f'php derive -g --mnemonic="{mnemonic}" --coin={coin} --numderive={depth} --cols=path,address,privkey,pubkey --format=json'

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    
    keys = json.loads(output)
    

coins = {BTCTEST: derive_wallets(coin=BTCTEST),
        ETH:derive_wallets(coin=ETH)}


def priv_key_to_account(coin, priv_key):
    if coin == 'BTCTEST':
        return bit.PrivateKeyTestnet(priv_key)
    if coin == 'ETH':
        return Account.privateKeyToAccount(priv_key)
    
def create_tx(coin, account, to, amount):
    if coin == 'eth':
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "value": amount})
        return {
        "to": to,
        "from": account.address,
        "value": amount,
        "gas": gasEstimate,            
        "gasPrice": w3.eth.gasPrice,
        "nonce": w3.eth.getTransactionCount(account.address),
        "chainId": w3.eth.chainId
        }
    if coin == 'btc-test':
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to.address, amount, BTC)])

def send_tx(coin, account, to, amount):
    raw_tx=create_tx(coin, account, to, amount)
    if coin == 'eth':
        signed = account.sign_transaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == 'btc-test':
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)    

#BTC TEST send transaction
account_one = priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey'])
account_two = priv_key_to_account(BTCTEST, coins[BTCTEST][1]['privkey'])

#ETH TEST send transcation
account_one = priv_key_to_account(ETH, coins[ETH][0]['privkey'])
account_two = priv_key_to_account(ETH, coins[ETH][1]['privkey'])