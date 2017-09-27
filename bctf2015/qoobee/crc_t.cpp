//#include "crc32.h"
#include <stdio.h>
#include <stdlib.h>

unsigned long crc32_table[256] = {0};

void init_crc32_table()
{
  for (int i = 0; i != 256; i++)
  {
    unsigned long crc = i;
    for (int j = 0; j != 8; j++)
    {
      if (crc & 1)
        crc = (crc >> 1) ^ 0xEDB88320;
      else
        crc >>= 1;
    }
    crc32_table[i] = crc;
  }
}

unsigned long crc32(char* buf, unsigned long len)
{
  unsigned long oldcrc32 = 0xFFFFFFFF;
  for (unsigned long i = 0; i != len; ++i)
  {
    unsigned long t = (oldcrc32 ^ buf[i]) & 0xFF;
    oldcrc32 = ((oldcrc32 >> 8) & 0xFFFFFF) ^ crc32_table[t];
  }
  return ~oldcrc32;
}

int main(int argc, char **argv)
{
    unsigned long malloc_a;
    unsigned long start_main_a;
    unsigned long middle;
    unsigned long ret;
    char buf[12];
    
    unsigned long ans = atol(argv[1]);
	unsigned long libc = atol(argv[2]);
	//printf("arg: 0x%x", ans);
    
    init_crc32_table();
    for (middle = 0x0; middle <= 0xffff; middle++)
    {
        buf[0] = middle & 0xff;
        buf[1] = (middle >> 8) & 0xff;
        buf[2] = (libc >> 32) & 0xff;
        buf[3] = (libc >> 40) & 0xff;
        buf[4] = 0; 
        buf[5] = 0;
        buf[6] = 0x40;
        buf[7] = 0xff;
        
        buf[8] = 0xff;
        buf[9] = 0xff;
        buf[10] = 0xff;
        buf[11] = 0xff;
        
        ret = crc32(buf, 12);
        
        //printf("%x\n", ret & 0xffffffff);
        if ((ret & (unsigned long)0xffffffff) == (unsigned long)ans)
        {
            printf("0x%lx\n", middle);
			//printf("%lx\n", start_main_a);
            //printf("find!\n");
            return 0;
        }
    }
}
