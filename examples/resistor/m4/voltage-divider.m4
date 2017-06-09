.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
Origin: Here
  ground; dot;
  source(up_ elen, V); llabel(,V_{in},); dot; "in" rjust
  resistor(right_ elen); llabel(,R_1,) dot; "out" ljust
  resistor(down_ elen); llabel(,R_2,)
  line down epsilon then to Origin then up epsilon
.PE
