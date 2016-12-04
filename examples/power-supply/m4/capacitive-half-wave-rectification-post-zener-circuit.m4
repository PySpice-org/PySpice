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
  source(up_ elen, AC); llabel(,V_{AC},); dot; "L" above;
  resistor(right_ elen); llabel(,R_{in},); dot; "1" above;
  capacitor(right_ elen); llabel(,C_{in},); dot; "2" above;
  {
  bigzenerdiode(down_ elen); rlabel(,Dz,); dot;
  }
  bigdiode(right_ elen); rlabel(,D,); dot;
  {
  capacitor(down_ elen, C+); llabel(,C,); dot;
  }
  line right_ elen then down epsilon; "out" above;
  resistor(down_ elen); llabel(,R_{load},);
  line down epsilon then to Neutral then up epsilon
.PE
