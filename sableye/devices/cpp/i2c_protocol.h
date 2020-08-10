/**************************************************************
 * i2c_protocol.h                                             *
 *   ) 0 o .                                                  *
 * v0.1                                                       *
 * I2C communications library.                                *
 **************************************************************/
#ifndef I2C_PROTOCOL_HEADER
#define I2C_PROTOCOL_HEADER

extern int ALLOW_DEBUG;   // > 0 == DEBUG allowed.

// Open and return I2C bus.
int open_i2c_bus(int adapter_num);

// Set SDA LOW, then SCL LOW.
int send_start(void);

// Set SDA LOW, then SCL HIGH.
int send_stop(void);

// Communicate with an address.
// + uint16_t *addr : 7-bit or 10-bit slave address.
// + int addr_len   : bit length of slave address; [7, 10].
// + rw             : for W = 0, for R = 1.
int send_address(uint16_t *addr, int addr_len, char rw);

// Wait 9 clock pulses for an ACK.
int await_ack(void);

// Split message into data frames and write to SDA.
int send_message(char *msg);

// Read/Store data frames.
char *read_message(void);


#endif
