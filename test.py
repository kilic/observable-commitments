from contracts import deploy
from crypto.dh_tuple import dh_create, dh_verify
from crypto.altbn128 import *
from observer import Observer, pedersen_c, H
from web3 import Web3, HTTPProvider
import unittest

provider = HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout': 10})
web3 = Web3(provider)
web3.eth.defaultAccount = web3.eth.accounts[0]


class TestObservableCommitments(unittest.TestCase):

  def test_update_commitment(self):
    a = randsn()
    p = randsn()
    A = multiply(G1, a)
    P = multiply(G1, p)
    contract = deploy(web3, 'TestPointUpdate', *(pasint(A), pasint(P)))
    u, e, _, P_ = dh_create(G1, P, a)
    b = contract.functions.verifyDHTuple(u, e, pasint(P_)).call()
    self.assertTrue(b)


  # target_a _> target_a
  # target_b _> target_b
  # target_c _> target_c
  # z -> u
  # u -> u
  # a -> x
  def test_commitment(self):

    Alice = web3.eth.accounts[1]
    contract = deploy(web3, 'CommitHere')

    # Observer sets monitor parameters for Alice,
    observer = Observer(web3, contract)
    target_a, target_b, target_c, shuffle, _ = observer.set_monitor_parameters(Alice)
    # and sends them to Alice

    # Alice makes a commitment to a value
    val = randsn()
    C, r = pedersen_c(val)

    # Alice prepares her hint values
    x = submodn(target_a, val)
    X = multiply(G1, x)
    Y = multiply(H, submodn(target_b, r))
    z = mulmodn(invmodn(x), target_c)

    # Alice prepares the update commitment
    T, _ = pedersen_c(target_a, target_b)
    u, e, A, T_ = dh_create(G1, T, shuffle)

    # Alice publicly broadcasts her commitment and hint
    tx_hash = contract.functions.storeCommitment(pasint(C), pasint(X) + pasint(Y), z, u, e, pasint(T_)).transact({'from': Alice})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    nonce = 0

    C_ = contract.functions.getCommitment(Alice).call()
    self.assertEqual(C[0], C_[0])
    self.assertEqual(C[1], C_[1])

    monitor_params = contract.functions.getMonitorParameters(Alice).call()
    self.assertTrue(monitor_params[0], T_[0])
    self.assertTrue(monitor_params[1], T_[1])

    # Observer extracts value as;
    val_ = observer.extract_value(Alice, z, nonce)
    self.assertEqual(val, val_)

    # Alice makes a commitment to another value
    val = randsn()
    C, r = pedersen_c(val)

    # Alice prepares her hint values
    target_a = mulmodn(target_a, shuffle)
    target_b = mulmodn(target_b, shuffle)
    x = submodn(target_a, val)
    X = multiply(G1, x)
    Y = multiply(H, submodn(target_b, r))
    z = mulmodn(invmodn(x), target_c)

    # Alice prepares the update commitment
    T, _ = pedersen_c(target_a, target_b)
    u, e, A, T_ = dh_create(G1, T, shuffle)

    # Alice publicly broadcasts her commitment and hint
    tx_hash = contract.functions.storeCommitment(pasint(C), pasint(X) + pasint(Y), z, u, e, pasint(T_)).transact({'from': Alice})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    nonce = 1

    C_ = contract.functions.getCommitment(Alice).call()
    self.assertEqual(C[0], C_[0])
    self.assertEqual(C[1], C_[1])

    # Observer extracts value as;
    val_ = observer.extract_value(Alice, z, nonce)
    self.assertEqual(val, val_)


if __name__ == '__main__':
  unittest.main()
