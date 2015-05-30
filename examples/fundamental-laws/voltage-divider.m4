.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
Origin: Here
  dot; "in" above
  resistor(right_ elen,,E); llabel(,R_1,); dot; "out" above
  resistor(down_ elen,,E); llabel(,R_2,)
  line down epsilon then left_ elen; dot
.PE
