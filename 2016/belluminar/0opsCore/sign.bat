"C:\Program Files\Microsoft SDKs\Windows\v6.0\Bin\x64\makecert.exe" -r -pe -ss PrivateCertStore -n "CN=0opsCert" 0opsCert.cer
"C:\Program Files\Microsoft SDKs\Windows\v6.0\Bin\signtool.exe" sign /a /s PrivateCertStore /i 0opsCert c:/0opsCore.sys
