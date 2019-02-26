## Publicly Verifiable Symmetric Encryption

**Caution! This is an intuitive and experimental work, DO NOT USE in production unless proof and optimization is fulfilled.**

Commitments are widely used cryptographic scheme in order to submit a value in an encrypted form. In some cases, commitments need to be revealed not to the public but only to a group of participants. So, out-of-band communication is required for users to reveal their committed values privately.

We define a mechanism that openings of commitments that remain publicly hidden can be extracted by _predefined observers_ just after the commitment phase where proof of extractability is verified on a public machine.

In this way sharing a secret value is done without a private reveal phase communication cost.
 
Here an encryption and decryption mechanism is developed only for openings of Pedersen commitments which are widely used commitment scheme.

### Overview

> *We define a mechanism that openings of commitments that remain publicly hidden can be extracted by _predefined observers_ just after the commitment phase where proof of extractability is verified on a public machine.*

Participants that reveal secret values to each other on public execution environment perform a one-time-only setup to generate a set of shared secret parameters which are target and shuffle scalars.

A _hint-to-target_ protocol is applied. Target point values which are derived from those shared secret parameters are stored on public storage. Naively, while a scalar `a` is a secret shared, point `aG` is a target point in some sense. A participant who commits a value with Pedersen commitments to some application deployed on a public machine, together with the commitment point, he or she is required to provide a hint vector that satisfies the target point. It is publicly verified that given hint vector properly hits the target. The verification protocol can be basically shown as `Commitment + Hint ?= Target`. Publicly published hint values are only meaningful for those who actually know the openings of the target, namely the shared secret parameters.

Thus, the proposed scheme can also be interpreted as publicly verifiable symmetric encryption technique.

Moreover, it is required that public target points are updated in each round in order to prevent an attacker from analyzing publicly provided hint vectors to extract openings. Openings of updated target points will remain secret among participants. Updating targets also do not reveal a relationship between two consecutive target points. To this end, the shared shuffle parameter is used to update target points. Furthermore, the update operation is publicly verified.

### Notation

Upper case letters, like `P`, are group elements (points) and lower case letters, such as `a`, `r`, are scalars. Multiplication is represented as `aG` which simply means `a` times `G`. All scalar operations are under group order modulus. `G` is the generator of an elliptic curve group and `H = hash_to_point(G)`. `C = vG + rH`  is a Pedersen commitment where `v` is the committed value or _the opening_ and `r` is the blinding factor.

### Setup

At the setup phase, a set of shared secret parameters are generated and corresponding points are stored on a public machine.

```
T1 = aG + bH
T2 = cG
S = sG
storeMonitorParameters(T1 ,T2, S)
```

Note that, `bH` part of `T1` should be generated collaboratively not to disclose blinding factors of published commitments. It can simply be done by adding many points of which discrete log is only known by related participants.

`a`, `c` and `s` values are wallet values and shared secret values among a group of participants.

Both point `T1` which is in the form of Pedersen Commitment and Point `T2` of which discrete log is known by participators, are target points that must be hit by a hint vector.

Scalar `s` is _the update anchor_ that updates point `T1` in each commitment round.

`T1`, `T2`, and `S` are stored on public execution machine in the setup phase.

### Commitment

A participant decides to commit a value `v`, and picks a random number `r` and calculates `C`

```
C = vG + rH
```

The commitment will be sealed with a hint vector and an updated target point.

#### A. Hint Vector

A hint vector is calculated as follows,

```
x = a - v
y = b - r
z = c/x
X = xG
Y = yH
hint = (X,Y,z)
```

The first part of the hint `(X, Y)` is simply the difference between commitment point `C` and first target point `T1`. Furthermore, the publisher must provide signatures so as to prove that he knows the discrete log of `X` and `Y` over the generators `G` and `H`, respectively.

Second part of the hint, `z` which is a scalar is given to reveal what `x` of `X` is. Knowing the value of `e` and `a`, an observer will be able to extract the opening.

#### B. Update Target

A user who makes a commitment also have to provide a new valid target point `T1'`. This point will be the replacement of `T1`.

`(T1, S, T1')` must be in the form of `(mG, nG, mnG)` which is called as Diffie-Hellmann (DH) tuple. Proof of the tuple which is denoted as `dh3π` must be delivered.


```
  T_new = sT
  r = rand()
  e = hash_to_scalar(rG, rT)
  u = r + s*e
  dh3π = (u,e)
```

#### C. Broadcast

Along with an actual commitment, the hint vector and the DH tuple proof are sent to a public execution machine. Note that, these values now become publicly available.

```
commit_to_public(C, X, Y, z, dh3π)
```

### Public Verification

Public verification is the process of checking if a hint vector is properly provided and if the newly suggested target point is valid. Public verification is done before storing a commitment. If the verification is not successful, the public machine should revert the execution.

#### A. Hint Verification

The hint vector must hit the target points.

```
C + X + Y ?= T1
zX ?= T2
```

#### B. Update Verification

The newly suggested target `T'` must form a DH Tuple with the shuffle point `S` and the previous target point `T`.

```
P = uG - eS
Q = uT - eT'
e' = hashToScalar(P,Q)
e ?= e'
T := T'
```

### Extraction

In the broadcast phase the hint vector `(X, Y, z)` is published.

An observer who possesses the corresponding secret values `a`, `c` and `s` can simply calculate `v`.

```
x = (c/z)
t = a * s^i
v = t - x
```

where `i` is the number of updates.

### Demo

A simple demonstration is given at [test script](https://github.com/kilic/observable-commitments/blob/master/test.py) where ethereum is used as the public machine.


