'''
##  RSA Coolest  ##
public key:
n = 0xba298d721fadbadb15dabd393db296c13610b33bfeb3aea844815439df3b025bcc6a7085a21eeb3b904a17071c01f05229873518828a8eb8a9129cff611f3481
e = 0x3
encrypted message:
0x7d4f6c0953ec517212b6c778da72245820a749254d21b62d09e36b44e073f858114f174b71cee25104b4d3b0abbf7eb31f031201bf40846290344c865c4b9cf8

public key:
n = 0xe37a3cab324cc0a5ea1030b498f3838f674e6ee9b4e441900c604e4d095b04c70cd32a7c4a5be0b463e3fd94594b3bd25ada9bc9ca17a80d72b7928e233f726d
e = 0x3
encrypted message:
0xc09aea0a9b6e10d7db7a5c2071b46f5801896c536152badb81db37848ef373cf6c6842737a87c12f6aba1d39bdf5d2aaf40e919628a64e4cd78a42c2cdde651a

public key:
n = 0xd8b6924687baaffe1c205ac0474fd5b5f894cb97abb3d427df0e47f30c7f035c07586430679ab65c5bbdccbc53cea9c95c466f3171d24efb85433bd05bc36c5d
e = 0x3
encrypted message:
0x6e3591536b9aadcdb412d6b05a755d603d0272434cc27447a8877707861363c8408b47da377474924db89a3e104717855613cbea16ad439c98b6e7bfdb7ae14f
'''

import gmpy2
import binascii

n1 = gmpy2.mpz(0xba298d721fadbadb15dabd393db296c13610b33bfeb3aea844815439df3b025bcc6a7085a21eeb3b904a17071c01f05229873518828a8eb8a9129cff611f3481)
n2 = gmpy2.mpz(0xe37a3cab324cc0a5ea1030b498f3838f674e6ee9b4e441900c604e4d095b04c70cd32a7c4a5be0b463e3fd94594b3bd25ada9bc9ca17a80d72b7928e233f726d)
n3 = gmpy2.mpz(0xd8b6924687baaffe1c205ac0474fd5b5f894cb97abb3d427df0e47f30c7f035c07586430679ab65c5bbdccbc53cea9c95c466f3171d24efb85433bd05bc36c5d)
e  = gmpy2.mpz(0x3)
c1 = gmpy2.mpz(0x7d4f6c0953ec517212b6c778da72245820a749254d21b62d09e36b44e073f858114f174b71cee25104b4d3b0abbf7eb31f031201bf40846290344c865c4b9cf8)
c2 = gmpy2.mpz(0xc09aea0a9b6e10d7db7a5c2071b46f5801896c536152badb81db37848ef373cf6c6842737a87c12f6aba1d39bdf5d2aaf40e919628a64e4cd78a42c2cdde651a)
c3 = gmpy2.mpz(0x6e3591536b9aadcdb412d6b05a755d603d0272434cc27447a8877707861363c8408b47da377474924db89a3e104717855613cbea16ad439c98b6e7bfdb7ae14f)

# Chinese Remainder Theorem with three equations
N  = n1 * n2 * n3
N1 = N / n1
N2 = N / n2
N3 = N / n3
b1 = gmpy2.invert(N1, n1)
b2 = gmpy2.invert(N2, n2)
b3 = gmpy2.invert(N3, n3)
m_pow_e = (c1*b1*N1 + c2*b2*N2 + c3*b3*N3) % N

m, boolean = gmpy2.iroot(m_pow_e, e)  # Figure out the cubic root of m_pow_e
m = hex(m)

print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])