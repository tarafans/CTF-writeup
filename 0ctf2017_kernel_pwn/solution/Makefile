CFLAGS := -static
LFLAGS := -lutil -lpthread
ALL := exploit

all: $(ALL)

exploit: exploit.c
	$(CC) $(CFLAGS) -o $@ $< $(LFLAGS)

clean:
	rm -rf $(ALL)

.PHONY: all clean
