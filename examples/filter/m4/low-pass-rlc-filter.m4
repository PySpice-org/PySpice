
.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
Origin: Here
  ground; dot;
  source(up_ elen, AC); llabel(,V_{in},); dot; "in" above
  resistor(right_ dimen_); llabel(,R_1,)
  inductor(right_ dimen_); llabel(,L_1,) dot; "out" ljust
  capacitor(down_ elen); llabel(,C_1,)
  line down epsilon then to Origin then up epsilon
.PE
