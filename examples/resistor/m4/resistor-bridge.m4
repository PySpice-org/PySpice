.PS
cct_init(SIdefaults)

linethick_(.5)
define(`dimen_', 10)
epsilon = 1e-3

Left: dot; "2" rjust
{
  Point_(45); resistor(,); dlabel(0,4,,,R_1)
  Top: dot; "1" rjust; Point_(-45); resistor(,); dlabel(0,4,,,R_2)
  Right: dot; "3" ljust; resistor(from Right to Left); llabel(,R_5,)
}
{
  Point_(-45); resistor(,); dlabel(0,-4,,,R_3)
  Bottom: dot; "0" rjust; Point_(45); resistor(,); dlabel(0,-4,,,R_4)
}

small_length = dimen_/4
move to Top; line up small_length then left dimen_*2 then down epsilon
STop: Here
move to Bottom; line down small_length; dot; ground
line to (STop, Here) then up epsilon
SBot: Here
source(from SBot to STop, V); dlabel(0,6,,,V_{in})

.PE
