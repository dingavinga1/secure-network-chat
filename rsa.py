from Crypto.Util import number
import random

phi=lambda p, q: (p-1)*(q-1) #euler totient

def eGCD(a, b): #extended euclidean algorithm
    if a==0:
        return b, 0, 1
    
    gcd, x1, y1= eGCD(b%a, a)

    x=y1-(b//a)*x1
    y=x1

    return gcd, x, y

def generateKeys(bits):
    #generate two prime numbers of size (RSA_KEY_SIZE)//2
    p=number.getPrime(bits//2)
    q=number.getPrime(bits//2)

    n=p*q #calculate n

    Q=phi(p, q) #calculate totient

    gcd=0
    while(gcd!=1): #getting a valid value for e
        e=1+random.getrandbits(bits)%(Q-1)
        gcd, x, y=eGCD(e, Q)

    d=x%Q #getting inverse of e, part of private key


    return { #returning key pair
        'pub':(e, n),
        'priv':(d, n)
    }
    
encrypt=lambda message, pubKey:pow(message, pubKey[0], pubKey[1]) #encryption 
decrypt=lambda cipher, privKey:pow(cipher, privKey[0], privKey[1]) #decryption

pad=lambda message, limit:(str(message)).rjust(len(str(2**limit)),'0') #padding a message according to limit
unpad=lambda cipher:int(cipher) #unpadding a message

def encode(message): #my own encoding scheme for strings
    cipher=''
    for ch in message:
        cipher+=str(ord(ch)).rjust(3, '0') #assigning 3 characters to each character(ascii)
    return cipher

def decode(cipher): #decoder for the above encoding scheme
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

def encryptString(plainText, key, maxlen=len(str(2**(512)))): #function for encrypting a whole string keeping in mind M<n
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

def decryptString(sending, key): #decrypting entire encrypted string
    recv=sending.split(',')

    pt=''
    for stat in recv:
        ct=decrypt(int(stat), key)
        pt+=decode(str(ct))

    return pt