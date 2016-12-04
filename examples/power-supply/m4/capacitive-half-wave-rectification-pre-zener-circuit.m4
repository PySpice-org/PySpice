.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
define(`bigdiode',
  `resized(2., `diode', $1)')
define(`bigzenerdiode',
  `resized(2., `reversed', `diode', $1, S)')
Neutral: Here
  dot; "N" below;
  source(up_ elen*2, AC); llabel(,V_{AC},); dot; "L" above;
  line right_ elen/2; dot;
  {
    line down_ elen/2;
    resistor(right_ elen); llabel(,R_{emi},);
    line up_ elen/2;
  }
  capacitor(right_ elen); llabel(,C_{in},); dot; "1" above;
  resistor(right_ elen); llabel(,R_{in},); dot; "2" above;
  bigdiode(right_ elen); rlabel(,D_{1},); dot;
  {
    C2: capacitor(down_ elen, C+); llabel(,C_{2},); dot; "3" at C2.end ljust;
    { bigdiode(left_ elen); llabel(,D_{2},); line up_ elen; }
    resistor(down_ elen); llabel(,R_{2},); dot;
  }
  line right_ elen; dot;
  {
    bigzenerdiode(down_ elen*2); llabel(,Dz,); dot;
  }
  line right_ elen; dot;
  {
    capacitor(down_ elen*2, C+); llabel(,C,); dot;
  }
  line right_ elen then down epsilon; "out" above;
  resistor(down_ elen*2); llabel(,R_{load},);
  line down epsilon then to Neutral then up epsilon
.PE
