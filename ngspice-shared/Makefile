all: test test-external-source

FLAGS = -std=c99 -Wall -I /usr/local/stow/ngspice-26/share/ngspice/include -L /usr/local/stow/ngspice-26/lib -lngspice -lpthread -lgomp

test: test.c
	${CC} ${FLAGS} -o $@ $<

test-external-source: test-external-source.c
	${CC} ${FLAGS} -o $@ $<

# End
