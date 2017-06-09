.PS
cct_init

elen = 0.75
epsilon = 1e-3

G: ground; dot
  source(up_ elen,AC); llabel(,V_{base},)
  line up epsilon then right epsilon
  resistor(right_ elen); llabel(,R_{b},)

Q1: bi_tr(up_,,,E) with .B at Here; llabel(,,Q_1)

line down from Q1.E to (Q1.E, G) then right to G then up epsilon

resistor(up_ 1.25*elen from Q1.C); rlabel(,R_{c})
Top: Here
line up epsilon then left to (G,Top) then down epsilon
reversed(`source', down_ elen,V); llabel(,V_{collector},)
ground

.PE
