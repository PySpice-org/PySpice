.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
define(`bigdiode',
  `resized(2., `diode', $1)')
Ground: Here
  ground; dot
  source(up_ elen, AC); llabel(,V_{in},); dot; "in" above
  capacitor(right_ elen); llabel(,C1,); dot; "1" above
  bigdiode(down_ elen); rlabel(,D1,)
  { line left_ elen }
  capacitor(right_ elen); rlabel(,C2,); dot; "2" below
   bigdiode(up_ elen); llabel(,D2,)
  { line left_ elen }
  capacitor(right_ elen); llabel(,C3,); dot; "3" above
  bigdiode(down_ elen); rlabel(,D3,)
  { line left_ elen }
  capacitor(right_ elen); rlabel(,C4,); dot; "4" below
  bigdiode(up_ elen); llabel(,D4,)
  { line left_ elen }
.PE
