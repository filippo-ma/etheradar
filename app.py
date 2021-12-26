import config
import time
import ccxt
from flask import Flask, render_template, request, redirect, flash
from web3 import Web3 
import os

app = Flask(__name__, template_folder="templates")

app.secret_key = os.urandom(12).hex()

# ethereum node connection
w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))


def get_eth_price():
    ftx = ccxt.ftx()
    eth_price = ftx.fetch_ticker('ETH/USD')

    return eth_price




@app.get("/")
def index():
    
    eth_price = get_eth_price()

    latest_blocks = []
    for block_number in range(w3.eth.block_number, w3.eth.block_number-10, -1):
        block = w3.eth.get_block(block_number)
        latest_blocks.append(block)

    latest_transactions = []
    for tx in latest_blocks[-1]['transactions'][-10:]:
        transaction = w3.eth.get_transaction(tx)
        latest_transactions.append(transaction)

    
    return render_template(
        "index.html", 
        eth_price=eth_price, 
        latest_blocks=latest_blocks,
        latest_transactions=latest_transactions,
        eth = w3.eth,
        current_time = time.time()
        )



@app.get("/transaction/<hash>")
def transaction(hash):
    transaction = w3.eth.get_transaction(hash)
    value = w3.fromWei(transaction.value, 'ether')
    receipt = w3.eth.get_transaction_receipt(hash)
    eth_price = get_eth_price()
    gas_price = w3.fromWei(transaction.gasPrice, 'ether')

    return render_template("transaction.html", hash=hash, transaction=transaction, value=value, receipt=receipt, gas_price=gas_price, eth_price=eth_price)


@app.get("/block/<block_number>")
def block(block_number):
    block = w3.eth.get_block(int(block_number))

    return render_template("block.html", block=block)


@app.get("/address")
def address():
    address = request.args.get('address')

    eth_price = get_eth_price()

    try:
        address = w3.toChecksumAddress(address)
    except:
        flash('Invalid address', 'danger')
        return redirect('/')

    balance = w3.eth.get_balance(address)
    balance = w3.fromWei(balance, 'ether')

    return render_template("address.html", address=address, eth_price=eth_price, balance=balance)




app.run()
