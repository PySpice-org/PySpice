.PS
cct_init(SIdefaults)
ifdef(`m4pco',`resetrgb')

linethick_(.5)
define(`dimen_', 10)
elen = dimen_*3/2

Origin: Here
  T: source(up_ elen, AC) ; llabel(,V_{in},); "in" above
  bridge_len = dimen_/2
  W: T.centre + (dimen_/2,0)
  N: W + (bridge_len,  bridge_len)
  S: W + (bridge_len, -bridge_len)
  E: S + (bridge_len,  bridge_len)
    diode(from W to N)
    diode(from S to E)
  R: resistor(from E + (dimen_,0) down_ dimen_); llabel(+,R_{load},-) # ; "out" above
  C: capacitor(down_ R.start.y - R.end.y from 0.5 between E and R.start, C+); rlabel(,C,)

  setrgb(1,0,0) # red
    dot(at T.end)
    dot(at C.start)
    line from T.end to (N,T.end) then to N; dot
    diode(to E); dot
    line from E to R.start; dot
  resetrgb

  setrgb(0,1,0) # green
    dot(at C.end)
    dot(at R.end)
    ground
    line to (W,Here) then to W; dot
    diode(to S); dot
    line to (Here,T.start) then to T.start; dot
  resetrgb

.PE
