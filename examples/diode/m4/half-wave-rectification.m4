.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
define(`bigdiode',
  `resized(2., `diode', $1)')
Origin: Here
  ground; dot
  source(up_ elen, AC); llabel(,V_{in},); dot; "in" above
  bigdiode(right_ elen); llabel(,D,); dot
  { capacitor(down_ elen, C+); llabel(,C,) dot }
  line right_ dimen_; dot; "out" above
  resistor(down_ elen); llabel(,R,); b_current(i)
  line to Origin
.PE
