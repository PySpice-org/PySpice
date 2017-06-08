.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
Origin: Here
  ground; dot;
  source(up_ elen, AC); llabel(,V_{in},); dot; "in" above
  inductor(right_ dimen_); llabel(,L_1,)
  capacitor(right_ dimen_); llabel(,C_1,) dot; "out" ljust
  resistor(down_ elen); llabel(,R_1,)
  line down epsilon then to Origin then up epsilon
.PE
