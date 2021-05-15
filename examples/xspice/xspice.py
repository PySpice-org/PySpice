#skip#

# https://github.com/xesscorp/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb

#  N_1 --- A1/adc --- A2/buf --- A3/dac ---
#  |                                       |
#  V1                                      R1
#  |                                       |
#  0                                    ---

# .title Test
# V1 N_1 0 DC 0V AC 1V SIN(1.65V 1.65V 100MegHz 0s 0Hz)
# A1 [N_1] [N_2] adc
# A2 N_2 N_3 buf
# A3 [N_3] [N_4] dac
# R1 N_4 0 1kOhm
# .model adc adc_bridge (fall_delay=1e-09s in_high=0.1V in_low=0.05V rise_delay=1e-09s)
# .model buf d_buffer (fall_delay=1e-09s input_load=1e-12s rise_delay=1e-09s)
# .model dac dac_bridge (out_high=3.3V out_low=1.0V)

# waveforms = sim.transient(step_time=0.1@u_ns, end_time=50@u_ns)

####################################################################################################

# cf. chapter 12

# Ngspice includes a library of predefined ‘Code Models’ that can be placed within any circuit
# description in a manner similar to that used to place standard device models.  Code model instance
# cards always begin with the letter ‘A’, and always make use of a .MODEL card to describe the code
# model desired. Section 28 of this document goes into greater detail as to how a code model similar
# to the predefined models may be developed, but once any model is created and linked into the
# simulator it may be placed using one instance card and one .MODEL card (note here we conform to
# the SPICE custom of referring to a single logical line of information as a ‘card’). As an example,
# the following uses a predefined ‘gain’ code model taking as an input some value on node 1,
# multiplies it by a gain of 5.0, and outputs the new value to node 2. Note that, by convention,
# input ports are specified first on code models. Output ports follow the inputs.

# Example:
# a1 1 2 amp
# .model amp gain(gain=5.0)

# In this example the numerical values picked up from single-ended (i.e. ground referenced) input
# node 1 and output to single-ended output node 2 will be voltages, since in the Interface
# Specification File for this code model (i.e., gain), the default port type is specified as a
# voltage (more on this later). However, if you didn’t know this, the following modifications to the
# instance card could be used to insure it:

# Example:
# a1 %v(1) %v(2) amp
# .model amp gain(gain =5.0)

# The specification %v preceding the input and output node numbers of the instance card indicate to
# the simulator that the inputs to the model should be single-ended voltage values. Other
# possibilities exist, as described later.  Some of the other features of the instance and .MODEL
# cards are worth noting. Of particu- lar interest is the portion of the .MODEL card that specifies
# gain=5.0. This portion of the card assigns a value to a parameter of the ‘gain’ model. There are
# other parameters that can be assigned values for this model, and in general code models will have
# several. In addition to numeric values, code model parameters can take non-numeric values (such as
# TRUE and FALSE), and even vector values. All of these topics will be discussed at length in the
# following pages. In general, however, the instance and .MODEL cards that define a code model will
# follow the abstract form described below. This form illustrates that the number of inputs and
# outputs and the number of parameters that can be specified is rel- atively open-ended and can be
# interpreted in a variety of ways (note that angle-brackets ‘<’ and ‘>’ enclose optional inputs):

# Example:

# AXXXXXXX <%v, %i, %vd, %id, %g, %gd, %h, %hd, or %d>
# + <[> <~><%v, %i, %vd, %id, %g, %gd, %h, %hd, or %d>
# + <NIN1 or +NIN1 -NIN1 or "null">
# + <~>... <NIN2.. <]> >
# + <%v ,%i, %vd , %id, %g, %gd, %h, %hd, %d or %vnam>
# + <[> <~> <%v, %i, %vd, %id, %g, %gd, %h, %hd,
#       or %d> <NOUT1 or +NOUT1 -NOUT1>
# + <~>... <NOUT2.. <]>>
# + MODELNAME

# .MODEL MODELNAME MODELTYPE <( PARAMNAME1 = <[> VAL1 <VAL2... <]>> PARAMNAME2.. > )>

# Square brackets ([ ]) are used to enclose vector input nodes.
# In addition, these brackets are used to delineate vectors of parameters.

# The literal string ‘null’, when included in a node list, is interpreted as no connection at that
# input to the model. ‘Null’ is not allowed as the name of a model’s input or output if the model
# only has one input or one output. Also, ‘null’ should only be used to indicate a missing
# connection for a code model; use on other XSPICE component is not interpreted as a missing
# connection, but will be interpreted as an actual node name.

# The tilde, ‘~’, when prepended to a digital node name, specifies that the logical value of that
# node be inverted prior to being passed to the code model. This allows for simple inversion of
# input and output polarities of a digital model in order to handle logically equivalent cases and
# others that frequently arise in digital system design.

# The following example defines a NAND gate, one input of which is inverted:

# a1 [~1 2] 3 nand1
# .model nand1 d_nand(rise_delay=0.1 fall_delay=0.2)

# The optional symbols %v, %i, %vd, etc. specify the type of port the simulator is to expect for the
# subsequent port or port vector. The meaning of each symbol is given in Table 12.1.

# The symbols described in Table 12.1 may be omitted if the default port type for the model is
# desired. Note that non-default port types for multi-input or multi-output (vector) ports must be
# specified by placing one of the symbols in front of EACH vector port. On the other hand, if all
# ports of a vector port are to be declared as having the same non-default type, then a symbol may
# be specified immediately prior to the opening bracket of the vector. The following examples should
# make this clear:

# Port Type Modifiers
# Modifier Interpretation
# %v       represents a single-ended voltage port - one node name or number is expected for each port.
# %i       represents a single-ended current port - one node name or number is expected for each port.
# %g       represents a single-ended voltage-input, current-output (VCCS) port - one node name or number
#          is expected for each port. This type of port is automatically an input/output.
# %h       represents a single-ended current-input, voltage-output (CCVS) port - one node name or number
#          is expected for each port. This type of port is automatically an input/output.
# %d       represents a digital port - one node name or number is expected for each port.
#          This type of port may be either an input or an output.
# %vnam    represents the name of a voltage source, the current through which is taken as an input.
#          This notation is provided primarily in order to allow models defined using SPICE2G6 syntax
#          to operate properly in XSPICE.
# %vd      represents a differential voltage port - two node names or numbers are expected for each port.
# %id      represents a differential current port - two node names or numbers are expected for each port.
# %gd      represents a differential VCCS port - two node names or numbers are expected for each port.
# %hd      represents a differential CCVS port - two node names or numbers are expected for each port.

# Example 1: - Specifies two differential voltage connections, one to nodes 1 & 2, and one to nodes 3 & 4.
#   %vd [1 2 3 4]

# Example 2: - Specifies two single-ended connections to node 1 and at node 2, and one differential
#              connection to nodes 3 & 4.
#   %v [1 2 %vd 3 4]

# Example 3: - Identical to the previous example...parenthesis are added for additional clarity.
#   %v [1 2 %vd(3 4)]

# Example 4: - Specifies that the node numbers are to be treated in the default fashion for the
#              particular model.  If this model had ‘%v” as a default for this port, then this
#              notation would represent four single-ended voltage connections.
#   [1 2 3 4]

# The parameter names listed on the .MODEL card must be identical to those named in the code model
# itself. The parameters for each predefined code model are described in detail in Sections 12.2
# (analog), 12.3 (Hybrid, A/D) and 12.4 (digital). The steps required in order to specify parameters
# for user-defined models are described in Chapter 28.

# 12.1.2 Examples

# The following is a list of instance card and associated .MODEL card examples showing use of
# predefined models within an XSPICE deck:

# a1 1 2 amp
# .model amp gain(in_offset=0.1 gain=5.0 out_offset=-0.01)

# a2 %i[1 2] 3 sum1
# .model sum1 summer(in_offset=[0.1 -0.2] in_gain=[2.0 1.0] out_gain=5.0 out_offset=-0.01)

# a21 %i[1 %vd(2 5) 7 10] 3 sum2
# .model sum2 summer(out_gain=10.0)

# a5 1 2 limit5
# .model limit5 limit(in_offset=0.1 gain=2.5 out_lower_limit=-5.0 out_upper_limit=5.0 limit_range=0.10 fraction=FALSE)

# a7 2 %id(4 7) xfer_cntl1
# .model xfer_cntl1 pwl(x_array=[-2.0 -1.0 2.0 4.0 5.0] y_array=[-0.2 -0.2 0.1 2.0 10.0] input_domain=0.05 fraction=TRUE)

# a8 3 %gd(6 7) switch3
# .model switch3 aswitch(cntl_off=0.0 cntl_on=5.0 r_off=1e6 r_on=10.0 log=TRUE)
