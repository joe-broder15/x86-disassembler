[BITS 32]
add dword [  eax*1 +  0x33333333 ], 0x12345678
add dword [  eax*2 +  0x33333333 ], 0x12345678
add dword [  eax*4 +  0x33333333 ], 0x12345678
add dword [  eax*8 +  0x33333333 ], 0x12345678
add dword [  eax*1 +  0x33 ], 0x12345678
add dword [  eax*2 +  0x33 ], 0x12345678
add dword [  eax*4 +  0x33 ], 0x12345678
add dword [  eax*8 +  0x33 ], 0x12345678
add dword [ dword eax + eax*1 +  0x33333333 ], 0x12345678
add dword [ dword eax + eax*2 +  0x33333333 ], 0x12345678
add dword [ dword eax + eax*4 +  0x33333333 ], 0x12345678
add dword [ dword eax + eax*8 +  0x33333333 ], 0x12345678
add dword [ byte eax + eax*1 +  0x33 ], 0x12345678
add dword [ byte eax + eax*2 +  0x33 ], 0x12345678
add dword [ byte eax + eax*4 +  0x33 ], 0x12345678
add dword [ byte eax + eax*8 +  0x33 ], 0x12345678