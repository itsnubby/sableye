/* v4l2_tools.cpp - Camera communications.
 * modified: 4/10/2020
 *  ) 0 o .
 */
#include <sys/ioctl.h>
#include <stdio.h>
#include <iostream>
using namespace std;


int connect(const char *camera_address) {
  printf("Connecting to camera at : %s\n", camera_address);
  return 0;
}

int capture_frame(int device_p) {
  printf("Capturing a frame.\n");
  return 0;
}


int main() {
  const char *camera_address = "/dev/video1";
  connect(camera_address);
  return 0;
}
