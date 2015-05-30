.PS
cct_init(SIdefaults)
linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2
epsilon = 1e-3
Origin: Here
  line right_ elen*1/2;
  {
    # simpler way ?
    arrow right arrowht from Origin + (elen*1/4,0) "$I_{in}$" above
  }
  {
    dot;
    resistor(down_ elen,,E); rlabel(,R_1,)
    dot;
  }
  line right_ elen*1/2 then down epsilon
  resistor(down_ elen,,E); llabel(,R_2,); b_current(I_{out})
  line down epsilon then left_ elen
.PE
