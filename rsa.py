from Crypto.Util import number
import random

phi=lambda p, q: (p-1)*(q-1)

def eGCD(a, b):
    if a==0:
        return b, 0, 1
    
    gcd, x1, y1= eGCD(b%a, a)

    x=y1-(b//a)*x1
    y=x1

    return gcd, x, y

def generateKeys(bits):
    p=number.getPrime(bits//2)
    q=number.getPrime(bits//2)

    n=p*q

    Q=phi(p, q)

    gcd=0
    while(gcd!=1):
        e=1+random.getrandbits(bits)%(Q-1)
        gcd, x, y=eGCD(e, Q)

    d=x%Q


    return {
        'pub':(e, n),
        'priv':(d, n)
    }
    
encrypt=lambda message, pubKey:pow(message, pubKey[0], pubKey[1])
decrypt=lambda cipher, privKey:pow(cipher, privKey[0], privKey[1])

pad=lambda message, limit:(str(message)).rjust(len(str(2**limit)),'0')
unpad=lambda cipher:int(cipher)

def encode(message):
    cipher=''
    for ch in message:
        cipher+=str(ord(ch)).rjust(3, '0')
    return cipher

def decode(cipher):
    pt=''
    i=0
    if len(cipher)%3==1:
        pt+=chr(int(cipher[i]))
        i+=1
    elif len(cipher)%3==2:
        pt+=chr(int(cipher[i:i+2]))
        i+=2
    else:
        pt+=chr(int(cipher[i:i+3]))
        i+=3
    while i<len(cipher):
        pt+=chr(int(cipher[i:i+3]))
        i+=3
    return pt

def encryptString(plainText, key, maxlen=len(str(2**(512)))):
    sending=''
    x=0
    for i in range(0, len(plainText)-maxlen, maxlen):
        pt=encode(plainText[i:i+maxlen])
        cipher=encrypt(int(pt), key)
        sending+=str(cipher)+','
        x+=maxlen
    pt=encode(plainText[x:])

    cipher=encrypt(int(pt), key)
    sending+=str(cipher)
    return sending

def decryptString(sending, key):
    recv=sending.split(',')

    pt=''
    for stat in recv:
        ct=decrypt(int(stat), key)
        pt+=decode(str(ct))

    return pt