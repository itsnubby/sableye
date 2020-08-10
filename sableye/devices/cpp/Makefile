CC=gcc
CFLAGS=-I.
DEPS = i2c_protocol.h
OBJ = i2c_protocol.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

i2c_protocol: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm -f $(OBJ) i2c_protocol
