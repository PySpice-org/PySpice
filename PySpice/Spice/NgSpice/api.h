/* Simplified Ngspice API for CFFI parser */

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

/* End */
