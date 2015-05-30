.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
T: Here
  source(up_ elen, V); llabel(,V_{th},)
  line up_ epsilon then right_ epsilon
  resistor(right_ elen,,E); llabel(,R_{th},)
  dot; "A" above
  resistor(down_ elen,,E); llabel(,R_{load},)
  dot; "B" below
Tse: Here
  line to T then up epsilon
[
N: Here
  source(up_ elen, I); llabel(,I_{no},)
  line up_ epsilon then right_ elen/2
  {dot; resistor(down_ elen,,E); llabel(,R_{no},); dot}
  line right_ elen
  dot; "A" above
  resistor(down_ elen,,E); llabel(,R_{load},)
  dot; "B" below
  line to N then up epsilon
] with .sw at Tse + (elen*3/2,0)
.PE
