from py_ecc.bn128 import add, multiply, curve_order, G1, FQ
from crypto.altbn128 import *
from random import randint

rand = lambda: randint(0, 2**256 - 1)
H = hashtopoint(hashpn(G1))

def pedersen_c(v, r=None):
  if r is None:
    r = randsn()
  return add(multiply(G1, v), multiply(H, r)), r


class Observer:

  def __init__(self, web3, contract):
    self.web3 = web3
    self.wait_tx = web3.eth.waitForTransactionReceipt
    self.contract = contract
    self.a1 = rand()
    self.a2 = rand()
    self.r = rand()
    self.s = rand()

  def monitor_parameters(self, address):
    from web3 import Web3
    ta = hashsn(self.a1, Web3.toInt(hexstr=address))
    tb = hashsn(self.a2, Web3.toInt(hexstr=address))
    tc = hashsn(self.r, Web3.toInt(hexstr=address))
    s = hashsn(self.s, Web3.toInt(hexstr=address))
    return ta, tb, tc, s

  def set_monitor_parameters(self, address):
    ta, tb, tc, s = self.monitor_parameters(address)
    target1, _ = pedersen_c(ta, tb)
    target2 = multiply(G1, tc)
    shuffle = multiply(G1, s)
    tx_hash = self.contract.functions.setMonitorParameters(address, pasint(target1) + pasint(target2) + pasint(shuffle)).transact()
    receipt = self.wait_tx(tx_hash)
    return ta, tb, tc, s, receipt

  def get_monitor_parameters(self, address):
    parameters = self.contract.functions.getMonitorParameters(address).call()
    target = parameters[:2]
    shuffle = parameters[2:4]
    index = parameters[4]
    return (FQ(target[0]), FQ(target[1])), (FQ(shuffle[0]), FQ(shuffle[1])), index

  def extract_value(self, address, hint, nonce):
    ta, _, tc, s = self.monitor_parameters(address)
    ta = mulmodn(ta, expmodn(s, nonce))
    return submodn(ta, mulmodn(tc, invmodn(hint)))
