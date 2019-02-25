pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./Curve.sol";

contract CommitHere  {

  using Curve for Curve.G1Point;
  Curve.G1Point public H;

  address observer;
  mapping(address => Curve.G1Point) commitments;
  mapping(address => Monitor) monitorParameters;

  struct Monitor{
    Curve.G1Point targetC;
    Curve.G1Point targetA;
    Curve.G1Point shuffleC;
    //Curve.G1Point shuffleA;
    uint256 nonce;
  }

  modifier onlyObserver(){
    require(observer == msg.sender, "only observer can");
    _;
  }

  constructor () public {
    observer = msg.sender;
    uint256 h = uint256(keccak256(abi.encodePacked(Curve.G1().X, Curve.G1().Y))) % Curve.Q();
    H = Curve.HashToPoint(h);
  }

  function storeCommitment(
    uint256[2] memory c,
    uint256[4] memory hintC,
    uint256 hintA,
    uint256 z,
    uint256 e,
    uint256[2] memory targetCU)
  public {
    Curve.G1Point memory aG = Curve.G1Point(hintC[0], hintC[1]);
    Curve.G1Point memory rH = Curve.G1Point(hintC[2], hintC[3]);
    Curve.G1Point memory C = Curve.G1Point(c[0], c[1]);
    require(C.g1add(aG).g1add(rH).g1eq(monitorParameters[msg.sender].targetC), "1st hint");
    require(aG.g1mul(hintA).g1eq(monitorParameters[msg.sender].targetA), "2nd hint");
    Curve.G1Point memory targetCU_ = Curve.G1Point(targetCU[0], targetCU[1]);
    require(verifyDHTuple(z, e,
        monitorParameters[msg.sender].targetC,
        monitorParameters[msg.sender].shuffleC,
        targetCU_), "dh tuple");
    commitments[msg.sender] = C;
    monitorParameters[msg.sender].targetC = targetCU_;
  }

  function verifyDHTuple(uint256 z, uint256 e,
  Curve.G1Point memory P,
  Curve.G1Point memory A,
  Curve.G1Point memory P_) 
  public view
  returns(bool){
    Curve.G1Point memory zG = Curve.G1().g1mul(z);
    Curve.G1Point memory zP = P.g1mul(z);
    Curve.G1Point memory eA = A.g1mul(e);
    Curve.G1Point memory eU = P_.g1mul(e);
    return e == uint256(keccak256(abi.encodePacked(zG.g1add(eA.g1neg()).X, zP.g1add(eU.g1neg()).X))) % Curve.Q();
  }

  function setMonitorParameters(
    address addr,
    uint256[6] memory mp)
  public
  onlyObserver{
    monitorParameters[addr] = Monitor(
      Curve.G1Point(mp[0], mp[1]),
      Curve.G1Point(mp[2], mp[3]),
      Curve.G1Point(mp[4], mp[5]),
      // Curve.G1Point(mp[6], mp[7]),
       1);
  }

  function getCommitment(address addr)
  public view
  returns(uint256[2] memory){
    return [commitments[addr].X, commitments[addr].Y]; 
  }

  function getMonitorParameters(address addr)
  public view
  returns(uint256[7] memory){
    Monitor memory m = monitorParameters[addr];
    return [m.targetC.X, m.targetC.Y, m.targetA.X, m.targetA.Y, m.shuffleC.X, m.shuffleC.Y, m.nonce];
  }
}