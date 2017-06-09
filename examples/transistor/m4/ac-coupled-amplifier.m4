.PS

cct_init

elen = 0.75
epsilon = 1e-3

G: ground; dot; "0" rjust
  source(up_ elen,AC); llabel(,V_{in},); dot; "in" rjust
  capacitor(right_ elen); llabel(,C_{1},); dot; "2" rjust above
  { resistor(down_ to (Here,G)); rlabel(,R_{2}) }
  { R1: resistor(up_ elen_*1.5); llabel(,R_{1}); dot; "5" above }

  line right_ elen_/2; up_ # Q1 direction
Q1: bi_tr(,,,E) with .B at Here; llabel(,,Q_1)

Q1E: Q1.E - (0,elen_/8) # shift a little bit
  # resistor(down_ from Q1.E to (Q1.E,G)); rlabel(,R_{E})
  line down from Q1.E to Q1E; dot; "3" ljust
  resistor(down_ to (Q1.E,G)); rlabel(,R_{E})

Q1C: Q1.C + (0,elen_/8) # shift a little bit
  dot(at Q1C); "4" ljust above
  capacitor(right_ elen from Q1C); llabel(,C_{2})
  dot; "out" ljust
  resistor(down_ to (Here,G)); rlabel(,R_{L})
  line down epsilon then to G

  resistor(up_ from Q1.C to (Q1.C,R1.end)); llabel(,R_{C})
  line up epsilon then left to (G,R1.end) then down epsilon
  reversed(`source', down_ elen,V); llabel(,V_{pwr},)
  ground
.PE
