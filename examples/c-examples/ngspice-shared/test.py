#skip#

####################################################################################################

import time

import numpy as np

from cffi import FFI

####################################################################################################

ffi = FFI()

####################################################################################################

ffi.cdef("""
typedef struct ngcomplex
{
  double cx_real;
  double cx_imag;
} ngcomplex_t;

typedef struct vector_info
{
  char *v_name;
  int v_type;
  short v_flags;
  double *v_realdata;
  ngcomplex_t *v_compdata;
  int v_length;
} vector_info, *pvector_info;

typedef struct vecvalues
{
  char *name;
  double creal;
  double cimag;
  bool is_scale;
  bool is_complex;
} vecvalues, *pvecvalues;

typedef struct vecvaluesall
{
  int veccount;
  int vecindex;
  pvecvalues *vecsa;
} vecvaluesall, *pvecvaluesall;

typedef struct vecinfo
{
  int number;
  char *vecname;
  bool is_real;
  void *pdvec;
  void *pdvecscale;
} vecinfo, *pvecinfo;

typedef struct vecinfoall
{
  char *name;
  char *title;
  char *date;
  char *type;
  int veccount;
  pvecinfo *vecs;
} vecinfoall, *pvecinfoall;

typedef int (SendChar) (char *, int, void *);
typedef int (SendStat) (char *, int, void *);
typedef int (ControlledExit) (int, bool, bool, int, void *);
typedef int (SendData) (pvecvaluesall, int, int, void *);
typedef int (SendInitData) (pvecinfoall, int, void *);
typedef int (BGThreadRunning) (bool, int, void *);
typedef int (GetVSRCData) (double *, double, char *, int, void *);
typedef int (GetISRCData) (double *, double, char *, int, void *);
typedef int (GetSyncData) (double, double *, double, int, int, int, void *);

int ngSpice_Init (SendChar *, SendStat *, ControlledExit *, SendData *, SendInitData *, BGThreadRunning *, void *);
int ngSpice_Init_Sync (GetVSRCData *, GetISRCData *, GetSyncData *, int *, void *);

int ngSpice_Command (char *);
pvector_info ngGet_Vec_Info (char *);
int ngSpice_Circ (char **);
char *ngSpice_CurPlot (void);
char **ngSpice_AllPlots (void);
char **ngSpice_AllVecs (char *);
bool ngSpice_running (void);
bool ngSpice_SetBkpt (double);
""")

####################################################################################################

ngspice_shared_path = '/usr/local/stow/ngspice-26/lib/libngspice.so'
ngspice_shared = ffi.dlopen(ngspice_shared_path)

####################################################################################################

@ffi.callback("int (char *, int, void *)")
def send_char_callback(message, ngspice_id, user_data):
    print('>>> send_char_callback', ffi.string(message), ngspice_id)
    return 0
#send_char_callback = ffi.NULL

@ffi.callback("int (char *, int, void *)")
def send_stat_callback(message, ngspice_id, user_data):
    print('>>> send_stat_callback', ffi.string(message), ngspice_id)
    return 0
#send_stat_callback = ffi.NULL

@ffi.callback("int (int, bool, bool, int, void *)")
def exit_callback(exit_status, immediate_unloding, quit_exit, ngspice_id, user_data):
    print("exit_callback", exit_status, immediate_unloding, quit_exit, ngspice_id)
    return exit_status

@ffi.callback("int (pvecvaluesall, int, int, void *)")
def send_data_callback(data, number_of_vectors, ngspice_id, user_data):
    print(">>> send_data [{}]".format(data.vecindex))

    for i in range(int(number_of_vectors)):
        actual_vector_value = data.vecsa[i]
        print("    Vector: {} {} +i {}".format(ffi.string(actual_vector_value.name),
                                               actual_vector_value.creal,
                                               actual_vector_value.cimag))

    return 0
#send_data_callback = ffi.NULL

@ffi.callback("int (pvecinfoall, int, void *)")
def send_init_data_callback(data,  ngspice_id, user_data):
    print(">>> send_init_data")
    number_of_vectors = data.veccount
    for i in range(number_of_vectors):
        print("  Vector:", ffi.string(data.vecs[i].vecname))

    return 0
#send_init_data_callback = ffi.NULL

@ffi.callback("int (double *, double, char *, int, void *)")
def get_vsrc_data(voltage, time, node, ngspice_id, user_data):
    print(">>> get_vsrc_data @{} node {}".format(time, ffi.string(node)))
    voltage[0] = 1.
    return 0

####################################################################################################

rc = ngspice_shared.ngSpice_Init(send_char_callback,
                                 send_stat_callback,
                                 exit_callback,
                                 send_data_callback,
                                 send_init_data_callback,
                                 ffi.NULL,
                                 ffi.NULL)
print('ngSpice_Init returned', rc)

ngspice_id = ffi.new('int *', 0)
rc = ngspice_shared.ngSpice_Init_Sync(get_vsrc_data, ffi.NULL, ffi.NULL, ngspice_id, ffi.NULL)
print("ngSpice_Init_Sync returned: ", rc)

time_step = '100u'

circuit = [
    ".title rc circuit",
    # "V1 1 0 1",
    "V1 1 0 dc 0 external",
    "R1 1 2 1",
    "C1 2 0 1 ic=0",
    ".tran {} 3 uic".format(time_step),
    ".end",
]

# for line in circuit:
#     rc = ngspice_shared.ngSpice_Command(('circbyline ' + line).encode('utf8'))
# print('ngSpice_Command', rc)

circuit_lines_keepalive = [ffi.new("char[]", line.encode('utf8')) for line in circuit] + [ffi.NULL]
circuit_array = ffi.new("char *[]", circuit_lines_keepalive)
rc = ngspice_shared.ngSpice_Circ(circuit_array)
print('ngSpice_Circ', rc)

rc = ngspice_shared.ngSpice_Command('bg_run'.encode('utf8'))
print('ngSpice_Command returned', rc)

time.sleep(.1) # required before to test if the simulation is running
while (ngspice_shared.ngSpice_running()):
    time.sleep(.1)
print("Simulation is done")

all_plots = ngspice_shared.ngSpice_AllPlots()
i = 0
while (True):
    if all_plots[i] == ffi.NULL:
        break
    else:
        print(ffi.string(all_plots[i]))
    i += 1

plot_name = 'tran1'
all_vectors = ngspice_shared.ngSpice_AllVecs(plot_name.encode('utf8'))
i = 0
while (True):
    if all_vectors[i] == ffi.NULL:
        break
    else:
        vector_name = ffi.string(all_vectors[i])
        name = '.'.join((plot_name, vector_name.decode('utf8')))
        vector_info = ngspice_shared.ngGet_Vec_Info(name.encode('utf8'))
        length = vector_info.v_length
        print("vector[{}] {} type {} flags {} length {}".format(i,
                                                                vector_name,
                                                                vector_info.v_type,
                                                                vector_info.v_flags,
                                                                length))
        if vector_info.v_compdata == ffi.NULL:
            print("  real data")
            # for k in range(length):
            #     print("  [{}] {}".format(k, vector_info.v_realdata[k]))
            real_array = np.frombuffer(ffi.buffer(vector_info.v_realdata, length*8), dtype=np.float64)
            print(real_array)
        else:
            print("  complex data")
            for k in range(length):
                value = vector_info.v_compdata[k]
                print("  [{}] {} + i {}".format(k, value.cx_real, value.cx_imag))
    i += 1
