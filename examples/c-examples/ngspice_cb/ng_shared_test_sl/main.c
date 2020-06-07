#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef _MSC_VER
#include <stdbool.h>
#include <pthread.h>
#else
#define bool int
#define true 1
#define false 0
#define strdup _strdup
#endif
#include <signal.h>
#if defined(__MINGW32__) || defined(_MSC_VER)
#include <windows.h>  // for Sleep
#else
#include <unistd.h>
#include <ctype.h>
#endif
#include "../include/sharedspice.h"

bool no_bg = true;
int vecgetnumber = 0;
double v2dat;
static bool has_break = false;
int testnumber = 0;
void alterp(int sig);
static bool errorflag = false;

#ifndef _MSC_VER
pthread_t mainthread;
#endif // _MSC_VER

int
ng_getchar(char* outputreturn, int ident, void* userdata);

int
ng_getstat(char* outputreturn, int ident, void* userdata);

int
ng_exit(int, bool, bool, int ident, void*);

int
ng_thread_runs(bool noruns, int ident, void* userdata);

int
ng_initdata(pvecinfoall intdata, int ident, void* userdata);

int
ng_data(pvecvaluesall vdata, int numvecs, int ident, void* userdata);

int
cieq(register char *p, register char *s);

int main()
{
    int ret, i;
    char *curplot, *vecname;
    char ** circarray;
    char **vecarray;
    
#ifndef _MSC_VER
    mainthread = pthread_self();
#endif // _MSC_VER    
    
    ret = ngSpice_Init(ng_getchar, ng_getstat, ng_exit,  ng_data, ng_initdata, ng_thread_runs, NULL);

    printf("Init thread returned: %d\n", ret);


    testnumber = 1;
    printf("\n**  Test no. %d with sourcing input file **\n\n", testnumber);

    /* load a ngspice input file with a tran simulation running for 15s */
 #if defined(__CYGWIN__)
    ret = ngSpice_Command("source /cygdrive/d/Spice_general/ngspice_sh/examples/shared-ngspice/adder_mos.cir");
#elif __MINGW32__
    ret = ngSpice_Command("source D:\\Spice_general\\ngspice_sh\\examples\\shared-ngspice\\adder_mos.cir");
#else
//    ret = ngSpice_Command("source ../../examples/adder_mos.cir");
    ret = ngSpice_Command("source adder_mos.cir");
#endif

//    ret = ngSpice_Command("source D:\\Spice_general\\ngspice_sh\\examples\\shared-ngspice\\adder_mos.cir");
    /* start the background thread and simulation with 'run' */
    ret = ngSpice_Command("bg_run");
#if defined(__MINGW32__) || defined(_MSC_VER)
    Sleep (5000);
#else
    usleep (5000000);
#endif
    ret = ngSpice_Command("bg_halt");
    /* print all vectors in current plot */
    for (i = 3; i > 0; i--) {
        printf("Pause for %d seconds\n", i);
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (1000);
#else
        usleep (1000000);
#endif
    }

    ret = ngSpice_Command("bg_resume");

    /* wait for 1s while simulation continues */
#if defined(__MINGW32__) || defined(_MSC_VER)
    Sleep (1000);
#else
    usleep (1000000);
#endif
    /* read current plot while simulation continues */
    curplot = ngSpice_CurPlot();
    printf("\nCurrent plot is %s\n\n", curplot);

    vecarray = ngSpice_AllVecs(curplot);
    /* get length of first vector */
    if (vecarray) {
        char plotvec[256];
        pvector_info myvec;
        int veclength;
        vecname = vecarray[0];
        sprintf(plotvec, "%s.%s", curplot, vecname);
        myvec = ngGet_Vec_Info(plotvec);
        veclength = myvec->v_length;
        printf("\nActual length of vector %s is %d\n\n", plotvec, veclength);
    }


    /* continue the main thread until bg thread is finished */
    for (;;) {
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
        if (no_bg)
            break;
    }
    ret = ngSpice_Command("write test1.raw V(5)");
goto test3;
    testnumber = 2;
    printf("\n**  Test no. %d with error during circuit parsing **\n\n", testnumber);

    /* create a circuit that fails due to missing include */
    ret = ngSpice_Command("circbyline fail test");
    ret = ngSpice_Command("circbyline V1 1 0 1");
    ret = ngSpice_Command("circbyline R1 1 0 1");
    ret = ngSpice_Command("circbyline .include xyz");
    ret = ngSpice_Command("circbyline .dc V1 0 1 0.1");
    ret = ngSpice_Command("circbyline .end");
test3:
    testnumber = 3;
    printf("\n**  Test no %d with flag for stopping background thread  **\n\n", testnumber);
   /* create an RC circuit, uase transient simulation */
    circarray = (char**)malloc(sizeof(char*) * 7);
    circarray[0] = strdup("test array");
    circarray[1] = strdup("V1 1 0 1");
    circarray[2] = strdup("R1 1 2 1");
    circarray[3] = strdup("C1 2 0 1 ic=0");
    circarray[4] = strdup(".tran 10u 3 uic");
    circarray[5] = strdup(".end");
    circarray[6] = NULL;

    has_break = false;

    ret = ngSpice_Circ(circarray);
    ret = ngSpice_Command("bg_run");

    for(i = 0; i < 6; i++)
        free(circarray[i]);
    free(circarray);

    /* wait until simulation stops */
    for (;;) {
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
        if (has_break) {
            ret = ngSpice_Command("bg_halt");
            ret = ngSpice_Command("listing");
            ret = ngSpice_Command("alter c1=2");
            ret = ngSpice_Command("bg_resume");
        }
        if (no_bg)
            break;
    }

    /* wait until simulation finishes */
    for (;;) {
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
        if (no_bg)
            break;
    }
    ret = ngSpice_Command("write test3.raw V(2)");

#ifndef _MSC_VER

    /* using signal SIGTERM by sending to main thread, alterp() then is run from the main thread,
      (not on Windows though!)  */
    testnumber = 4;
    printf("\n**  Test no %d with interrupt signal **\n\n", testnumber);
    has_break = false;
    (void) signal(SIGTERM, alterp);
    ret = ngSpice_Command("bg_run");
    for (;;) {
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
        if (no_bg)
            break;
    }
    ret = ngSpice_Command("echo alter command issued");
    ret = ngSpice_Command("alter c1=1");
    ret = ngSpice_Command("bg_resume");

    /* wait until simulation finishes */
    for (;;) {
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
        if (no_bg)
            break;
    }
    ret = ngSpice_Command("write test4.raw V(2)");
    printf("rawfile testout2.raw created\n");
#endif
    return 0;

    return ret;
}

int
ng_getchar(char* outputreturn, int ident, void* userdata)
{
    printf("%s\n", outputreturn);
    return 0;
}


int
ng_getstat(char* outputreturn, int ident, void* userdata)
{
    printf("%s\n", outputreturn);
    return 0;
}

int
ng_thread_runs(bool noruns, int ident, void* userdata)
{
    no_bg = noruns;
    if (noruns)
        printf("bg not running\n");
    else
        printf("bg running\n");

    return 0;
}

/* Callback function called from bg thread in ngspice once per accepted data point */
int
ng_data(pvecvaluesall vdata, int numvecs, int ident, void* userdata)
{
    int *ret;

    v2dat = vdata->vecsa[vecgetnumber]->creal;
    if (!has_break && (v2dat > 0.5)) {
//        printf("Data V(2) value: %f\n", v2dat);
    /* using signal SIGTERM by sending to main thread, alterp() then is run from the main thread,
      (not on Windows though!)  */
#ifndef _MSC_VER
        if (testnumber == 4)
            pthread_kill(mainthread, SIGTERM);
#endif
        has_break = true;
        printf("Pause requested, setpoint reached\n");
    /* leave bg thread for a while to allow halting it from main */
#if defined(__MINGW32__) || defined(_MSC_VER)
        Sleep (100);
#else
        usleep (100000);
#endif
//        ret = ((int * (*)(char*)) ngSpice_Command_handle)("bg_halt");
    }
    return 0;
}


/* Callback function called from bg thread in ngspice once upon intialization
   of the simulation vectors)*/
int
ng_initdata(pvecinfoall intdata, int ident, void* userdata)
{
    int i;
    int vn = intdata->veccount;
    for (i = 0; i < vn; i++) {
        printf("Vector: %s\n", intdata->vecs[i]->vecname);
        /* find the location of V(2) */
        if (cieq(intdata->vecs[i]->vecname, "V(2)"))
            vecgetnumber = i;
    }
    return 0;
}


/* Callback function called from bg thread in ngspice if fcn controlled_exit()
   is hit. Do not exit, but unload ngspice. */
int
ng_exit(int exitstatus, bool immediate, bool quitexit, int ident, void* userdata)
{

    if(quitexit) {
        printf("DNote: Returned form quit with exit status %d\n", exitstatus);
        exit(exitstatus);
    }
    if(immediate) {
        printf("DNote: Unloading ngspice inmmediately is not possible\n");
        printf("DNote: Can we recover?\n");
    }

    else {
        printf("DNote: Unloading ngspice is not possible\n");
        printf("DNote: Can we recover? Send 'quit' command to ngspice.\n");
        errorflag = true;
        ngSpice_Command("quit 5");
//        raise(SIGINT);
    }

    return exitstatus;
}

/* Funcion called from main thread upon receiving signal SIGTERM */
void
alterp(int sig) {
    ngSpice_Command("bg_halt");
}


/* Case insensitive str eq. */
/* Like strcasecmp( ) XXX */

int
cieq(register char *p, register char *s)
{
    while (*p) {
        if ((isupper(*p) ? tolower(*p) : *p) !=
            (isupper(*s) ? tolower(*s) : *s))
            return(false);
        p++;
        s++;
    }
    return (*s ? false : true);
}
