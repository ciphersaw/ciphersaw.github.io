'''
##  RSA Cooler  ##
public key:
n = 0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409
e = 0xe9a44960483b5ca224cfd18818944eaae47de3a158debbc7886b74d7e11165e2e4158c86add4ccc5317256e5323596c9947513766645aefdac4f0375a0296743

encrypted message:
c = 0x636f86fb2b1991d4788092563adf87d14b975e9c7ab7279b10f4741f515788bba2e6e788d6f6c165f4daf65eabee93cebfc55a1d651b1dfb1190174ab338d959775658cf1c6d42b0fe6b7b1abaf5a9aa4ca239367bfcbe88b304c99d5e5f8aac019ec74b11662a5deba523c2f93b7c68a731c019578e3ac64db64cfd3533e91b

public key:
n = 0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409
e = 0xd9b47cdd777deb3e94cfa3d416aa91b04f9391af0504a83de03e9e0c49faae8b79cf7c99f575af99ed2e9e5a7edb09219c4f79cf961092f9919ab33bc3c9a74f

encrypted message:
0x53b601daa8f93166495a69fa747f8553bb8317cfe6dc3f7fec8c8511e209f9288038405fdee399f3ed68ab25dcd91be8bb2ef2ecac1173318b5d2bba932afdcab2d4e5b46987a0f774a29204ce481f79ea422943118f2eaf6c6820b501d9da8d3fbbcea464a2d158a39de6bae6ab845555e4646ae556d7b1e00567b00d41b06c
'''

import gmpy2
import binascii

# Extended Euclid Algorithm
def extendedGCD(a, b):  
    # a*xi + b*yi = ri
    if b == 0:
        return (1, 0, a)
    # a*x1 + b*y1 = a
    x1 = 1
    y1 = 0
    # a*x2 + b*y2 = b
    x2 = 0
    y2 = 1
    while b != 0:
        q = a / b
        # ri = r(i-2) % r(i-1)
        r = a % b
        a = b
        b = r
        # xi = x(i-2) - q*x(i-1)
        x = x1 - q*x2
        x1 = x2
        x2 = x
        # yi = y(i-2) - q*y(i-1)
        y = y1 - q*y2
        y1 = y2
        y2 = y
    return (x1, y1, a)

n = gmpy2.mpz(0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409)
e1 = gmpy2.mpz(0xe9a44960483b5ca224cfd18818944eaae47de3a158debbc7886b74d7e11165e2e4158c86add4ccc5317256e5323596c9947513766645aefdac4f0375a0296743)
e2 = gmpy2.mpz(0xd9b47cdd777deb3e94cfa3d416aa91b04f9391af0504a83de03e9e0c49faae8b79cf7c99f575af99ed2e9e5a7edb09219c4f79cf961092f9919ab33bc3c9a74f)
c1 = gmpy2.mpz(0x636f86fb2b1991d4788092563adf87d14b975e9c7ab7279b10f4741f515788bba2e6e788d6f6c165f4daf65eabee93cebfc55a1d651b1dfb1190174ab338d959775658cf1c6d42b0fe6b7b1abaf5a9aa4ca239367bfcbe88b304c99d5e5f8aac019ec74b11662a5deba523c2f93b7c68a731c019578e3ac64db64cfd3533e91b)
c2 = gmpy2.mpz(0x53b601daa8f93166495a69fa747f8553bb8317cfe6dc3f7fec8c8511e209f9288038405fdee399f3ed68ab25dcd91be8bb2ef2ecac1173318b5d2bba932afdcab2d4e5b46987a0f774a29204ce481f79ea422943118f2eaf6c6820b501d9da8d3fbbcea464a2d158a39de6bae6ab845555e4646ae556d7b1e00567b00d41b06c)

x, y, r = extendedGCD(e1, e2)
m = hex(pow(c1, x, n) * pow(c2, y, n) % n)

print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])