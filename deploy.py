import json
from msilib.schema import Signature
from aiohttp import TraceDnsCacheHitParams
from solcx import compile_standard, install_solc
from web3 import Web3

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    print(" Installing..")
    install_solc("0.6.0")

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.6.0",
    )
    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0xeD535AC0d5B148B94Ba5f066657165E61E693769"
private_key = "0xa10a450275cf0d49685961bebecbca2f370aa9e83b6f69063c0e88deac9b2e4a"

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)


nonce = w3.eth.getTransactionCount(my_address)
print(nonce)

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)


print(simple_storage.functions.retrieve().call())

greet_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_greet_txn = w3.eth.account.sign_transaction(
    greet_transaction, private_key=private_key
)

tx_greet_hash = w3.eth.send_raw_transaction(signed_greet_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greet_hash)

print(simple_storage.functions.retrieve().call())
