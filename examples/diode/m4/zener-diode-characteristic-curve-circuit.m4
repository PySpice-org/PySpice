.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
define(`bigdiode',
  `resized(2., `diode', $1, S)')
Origin: Here
  ground; dot;
  source(up_ elen, V); llabel(,V_{in},); dot; "in" above
  resistor(right_ elen); llabel(,R_1,) dot; "out" above
  bigdiode(down_ elen); llabel(,Dz_1,)
  line down epsilon then to Origin then up epsilon
.PE
