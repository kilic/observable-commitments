from .altbn128 import *

def dh_create(G, H, w):
  U = multiply(G, w)
  V = multiply(H, w)
  r = randsn()
  A = multiply(G, r)
  B = multiply(H, r)
  e = hashsn(A[0].n, B[0].n)
  z = addmodn(r, mulmodn(e, w))
  return z, e, U, V

def dh_verify(G, H, z, e, U, V):
  zG = multiply(G,z)
  zH = multiply(H,z)
  eU = multiply(U, e)
  eV = multiply(V, e)
  A = add(zG, negp(eU))
  B = add(zH, negp(eV))
  e_ = hashsn(A[0].n, B[0].n)
  return e == e_

# a = randsn()
# b = randsn()
# H = multiply(G1, a)
# z, e, U, V = dh_create(G1, H, b)
# x = dh_verify(G1, H, z, e, U, V)

def dh_create_p():
  pass

def dh_verify_p():
  pass