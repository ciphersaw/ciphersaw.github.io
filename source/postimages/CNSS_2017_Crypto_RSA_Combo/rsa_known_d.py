'''
## Easy RSA ##
p: 0xddb9fe428c938abdce551751b299feed367c97b52b17062d
q: 0x265ad78c77eab2c5ab9b69fb44a11624818bed56c003d2c5e6d29f7
e: 0x1fffffffffffffff
d: 0x9737352a92d198aaeddb8db9cc5cb81a788aa7d0ec0ec9bac7f6ffece7ff928c8db6a47656dffb0421ef9ca595665b6b55d35f
c: 0x1c0aa41505131e967d3db09227ef9572337a5e79f07484428efd6262eddee2fb67b6e6e6b5506871891ece1949eabf7a03cafdb
'''

import gmpy2
import binascii

p = gmpy2.mpz(0xddb9fe428c938abdce551751b299feed367c97b52b17062d)
q = gmpy2.mpz(0x265ad78c77eab2c5ab9b69fb44a11624818bed56c003d2c5e6d29f7)
d = gmpy2.mpz(0x9737352a92d198aaeddb8db9cc5cb81a788aa7d0ec0ec9bac7f6ffece7ff928c8db6a47656dffb0421ef9ca595665b6b55d35f)
c = gmpy2.mpz(0x1c0aa41505131e967d3db09227ef9572337a5e79f07484428efd6262eddee2fb67b6e6e6b5506871891ece1949eabf7a03cafdb)

m = hex(pow(c, d, p*q))  # Figure out c^d modulo n, then change to hex. Note that n = p * q.
print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])