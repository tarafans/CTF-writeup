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
	//printf("arg: 0x%x", ans);
    
    init_crc32_table();
    for (middle = 0x0; middle <= 0xf000000; middle++)
    {
        malloc_a = (unsigned long)0x7f * (unsigned long)0x10000000 + (unsigned long)middle;
        malloc_a = (unsigned long)malloc_a * (unsigned long)0x1000 + (unsigned long)0x750;
        start_main_a = malloc_a - 0x82750 + 0x21dd0;
        
        buf[0] = malloc_a & 0xff;
        buf[1] = (malloc_a >> 8) & 0xff;
        buf[2] = (malloc_a >> 16) & 0xff;
        buf[3] = (malloc_a >> 24) & 0xff;
        buf[4] = (malloc_a >> 32) & 0xff;
        buf[5] = (malloc_a >> 40) & 0xff;
        buf[6] = (malloc_a >> 48) & 0xff;
        buf[7] = (malloc_a >> 56) & 0xff;
        
        buf[8] = (start_main_a) & 0xff;
        buf[9] = (start_main_a >> 8) & 0xff;
        buf[10] = (start_main_a >> 16) & 0xff;
        buf[11] = (start_main_a >> 24) & 0xff;
        
        ret = crc32(buf, 12);
        
        //printf("%x\n", ret & 0xffffffff);
        if ((ret & (unsigned long)0xffffffff) == (unsigned long)ans)
        {
            printf("0x%lx\n", malloc_a);
			//printf("%lx\n", start_main_a);
            //printf("find!\n");
            return 0;
        }
    }
}
