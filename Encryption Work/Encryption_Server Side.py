from Crypto.Cipher import AES
import base64
import binascii

key = bytes('tmf63mnxpy3hf2cw',encoding ='utf-8')

cipher = AES.new(key, AES.MODE_ECB)


ciphertext = "67f4f89c24873f6d602dfa6361f2b663" #cipher.encrypt(b'Tech tutorials x')
# msg = bytes(ciphertext, encoding = 'utf-8') #converts mg to Byte type
#print(str(msg))

# print(binascii.unhexlify(mg))

decipher = AES.new(key, AES.MODE_ECB)
# print(binascii.hexlify(decipher.decrypt(msg)))

decrypted = decipher.decrypt(binascii.unhexlify(ciphertext)).decode("utf-8")

#Taking off padding
while decrypted[-1] == '?':
    decrypted = decrypted[:-1]

print(decrypted) #This print is for testing but can be commented out. Decrypted is the plaintext
