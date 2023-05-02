'''
##  RSA Cool ##
p: 0xf5621a5fd44994f720c1b971fea84f63
q: 0xdfb85e3d22c0b59271884df021a57123
e: 0xf36698ed9d9fedd7
enc: 0x448040a0a4757a630c4d8401fb3c0518ab0bce9a02085329536244c91727775c
'''

import gmpy2
import binascii

p = gmpy2.mpz(0xf5621a5fd44994f720c1b971fea84f63)
q = gmpy2.mpz(0xdfb85e3d22c0b59271884df021a57123)
e = gmpy2.mpz(0xf36698ed9d9fedd7)
c = gmpy2.mpz(0x448040a0a4757a630c4d8401fb3c0518ab0bce9a02085329536244c91727775c)

phi_n = (p - 1) * (q - 1)
d = gmpy2.invert(e, phi_n)  # Figure out the multiplicative inverse of e modulo phi_n (i.e. the private key). 
m = hex(pow(c, d, p*q))  # Figure out c^d modulo n, then change to hex. Note that n = p * q.

print "private key:", hex(d)
print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])