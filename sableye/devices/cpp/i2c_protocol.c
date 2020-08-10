/**************************************************************
 * i2c_protocol.c                                             *
 *   ) 0 o .                                                  *
 * v0.1                                                       *
 * I2C communications library.                                *
 **************************************************************/
//#include <linux/i2c-dev.h>
//#include <i2c/smbus.h>
//#include "i2c_protocol.h"
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>


// globals.
int ALLOW_DEBUG = -1;


// helper functions.
char * from_int_to_str(int num_int) {
  // TODO: allow for more than single digits.
  static char num_str[3];
  if (num_int >= 0 && num_int <= 9) {
    num_int += 0x30;
    num_str[0] = (char) num_int;
    return num_str;
  } else {
    printf("ERROR: Invalid address!\n");
    return num_str;
  }
}

char *get_i2c_bus_name(int adapter_num) {
  int file;
  static char i2c_bus_name[12] = "/dev/i2c-";
  char *adapter_num_str = "";
  
  adapter_num_str = from_int_to_str(adapter_num);
  strcat(i2c_bus_name, adapter_num_str);
  return i2c_bus_name;
}


// module defs.
// Set SDA LOW, then SCL LOW.
int send_start(void) {
  printf("SDA | SCL\n");
  static int sda = 1;
  static int scl = 1;
  printf("%d | %d\n", sda, scl);
  sda = 0;
  printf("%d | %d\n", sda, scl);
  scl = 0;
  printf("%d | %d\n", sda, scl);
}

// Set SDA LOW, then SCL HIGH.
int send_stop(void) {
  static int sda = 0;
  static int scl = 0;
  printf("%d | %d\n", sda, scl);
  scl = 1;
  printf("%d | %d\n", sda, scl);
  sda = 1;
  printf("%d | %d\n", sda, scl);
}

// Send bit to slave, move SCL.
int send_bit(uint8_t bit) {
  printf("%d", bit);
}

int i2c_address_out(uint16_t *addr, int addr_len, char rw) {
//  int fail = 0;
//  static int sda = 0;
//  static int scl = 0;
//
//  uint16_t frame_size = 7;
//  uint16_t *addr_ext = '11110';
//  uint16_t bit = 1;
//  int index = 0;
//  for (bit = addr[index]; index < addr_len; index++;) { 
//    send_bit(bit);
//  }
//  send_bit(rw_bit);
//
//
//
//
//  if (addr_len == 7) {
//    fail = send_address_w7(addr);
//  } else if (addr_len == 10) {
//    fail = send_address_w10(addr);
//  }
//  else {
//    fail = 1;
//  }
  printf("Hi nub");
}
int i2c_open_bus(char *i2c_bus_name) {
  int i2c_fp = -1;
  if ((i2c_fp = open(i2c_bus_name, O_RDWR)) < 0) {
    if ((i2c_fp = open("/dev/null", O_RDWR)) < 0 || ALLOW_DEBUG < 0) {
      char err[200];
      sprintf(err, "open('%s') in i2c_open_bus", i2c_bus_name);
      perror(err);
      exit(1);
    }
  }
  return i2c_fp;
}

void i2c_close_bus(int i2c_fp) {
  close(i2c_fp);
}

void i2c_open_addr(int i2c_fp, int i2c_addr) {
  if (ioctl(i2c_fp, I2C_SLAVE, i2c_addr) < 0 && ALLOW_DEBUG < 0) {
    char err[200];
    sprintf(err, "ioctl('%s, I2C_SLAVE, %s') in i2c_open_addr", i2c_fp, i2c_addr);
    perror(err);
    exit(1);
  }
}

void i2c_send_request();    // TODO : nubby, 8/10/2020  ) 0 o .

int main(void) {
  int i2c_bus_num = 1, i2c_fp = -1, i2c_addr = 0x43;
  char *i2c_bus_name = get_i2c_bus_name(i2c_bus_num);

  i2c_fp = i2c_open_bus(i2c_bus_name);
  i2c_open_addr(i2c_fp, i2c_addr);
  i2c_close_bus(i2c_fp);
}

