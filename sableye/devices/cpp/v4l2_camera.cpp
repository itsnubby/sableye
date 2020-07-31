#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>


uint8_t *buffer;


static int xioctl(int fd, int request, void *arg) {
  int r;

  do r = ioctl (fd, request, arg);
  while (-1 == r && EINTR == errno);

  return r;
}

struct v4l2_capability caps = {0};
if (-1 == xioctl(fd, VIDIOC_QUERYCAP, &caps)) {
  perror("querying capabilities for video device");
  return 1;
}

int main() {
  int fd;
  char *ports  = [];
  find_ports(ports);    // move to separate file?
  
  for port in ports {
    fd = open(port, 0_RDWR);
    if (fd == -1) {
      // capture device not found.
      perror("opening video device");
      return 1;
    }

    if (print_caps(fd)) {
      return 1;
    }

    if (init_mmap(fd)) {
      return 1;
    }

    if (capture_image(fd)) {
      return 1;
    }

    close (fd);
    return 0;
  }
}
