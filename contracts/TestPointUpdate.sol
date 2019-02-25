pragma solidity ^0.5.0;

import "./Curve.sol";

contract TestPointUpdate  {

  using Curve for Curve.G1Point;
  Curve.G1Point public A;
  Curve.G1Point public P;

  constructor (uint256[2] memory A_, uint256[2] memory P_) public {
    A = Curve.G1Point(A_[0], A_[1]);
    P = Curve.G1Point(P_[0], P_[1]);
  }

  function update(uint256 z, uint256 e, uint256[2] memory P_)
  public{
    require(verifyDHTuple(z, e, P_), "");
    P = Curve.G1Point(P_[0], P_[1]);
  }

  function verifyDHTuple(uint256 z, uint256 e, uint256[2] memory P_) 
  public view
  returns(bool){
    Curve.G1Point memory zG = Curve.G1().g1mul(z);
    Curve.G1Point memory zP = P.g1mul(z);
    Curve.G1Point memory eA = A.g1mul(e);
    Curve.G1Point memory eU = Curve.G1Point(P_[0], P_[1]).g1mul(e);
    return e == uint256(keccak256(abi.encodePacked(zG.g1add(eA.g1neg()).X, zP.g1add(eU.g1neg()).X))) % Curve.Q();
  }
}
