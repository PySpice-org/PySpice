.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
dnl Xsection(i, 1 to don't show dot, 1 to show A node)
define(`Vsection', `
  ifelse(eval($2!=1), 1, `dot')
  ifelse(eval($3==1), 1, `dot; "A" above')
  resistor(down_ elen,,E); llabel(,R_`$1',)
  reversed(`source', down_ elen,V); llabel(,V_`$1',)
  ifelse(eval($2!=1), 1, `dot')
 ')
define(`Isection', `
  ifelse(eval($2!=1), 1, `dot')
  ifelse(eval($3==1), 1, `dot; "A" above')
  resistor(down_ elen,,E); llabel(,R_`$1',)
  reversed(`source', down_ elen,I); llabel(,I_`$1',)
  ifelse(eval($2!=1), 1, `dot')
 ')

Origin: Here
  for_(1, 3, 1, `
    ifelse(eval(m4x!=1), 1, `line up epsilon then right_ elen')
    { Vsection(m4x, m4x, 0) }
  ')
  line dotted right_ elen
  { Vsection(i, 0, 0) }
  line dotted right_ elen
  Isection(k, 1, 1)
line down epsilon then to (Origin.x, Here.y) then up epsilon
.PE
