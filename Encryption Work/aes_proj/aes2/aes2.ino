#include <AES.h>
//#include "printf.h"
 
AES aes ;
 
unsigned int keyLength [3] = {128, 192, 256}; // key length: 128b, 192b or 256b
 
byte *key = (unsigned char*) "01234567890123456789012345678901"; // encryption key

byte plain[] = "TEST TEST TEST TEST"; // plaintext to encrypt
 
unsigned long long int myIv = 36753565; // CBC initialization vector; real iv = iv x2 ex: 01234567 = 0123456701234567

void setup ()
{
  Serial.begin(115200) ;
}
 
void loop () 
{
    aesTest(128);
    delay(2000);

}
 
void aesTest (int bits)
{
  aes.iv_inc();
  
  byte iv [N_BLOCK] ;
  int plainPaddedLength = sizeof(plain) + (N_BLOCK - ((sizeof(plain)-1) % 16)); // length of padded plaintext [B]
  byte cipher [plainPaddedLength]; // ciphertext (encrypted plaintext)
  byte check [plainPaddedLength]; // decrypted plaintext
  
  aes.set_IV(myIv);
  aes.get_IV(iv);
 
  Serial.print("- encryption time [us]: ");
  unsigned long ms = micros ();
  aes.do_aes_encrypt(plain,sizeof(plain),cipher,key,bits,iv);
  Serial.println(micros() - ms);
 
  aes.set_IV(myIv);
  aes.get_IV(iv);
  
  Serial.print("- decryption time [us]: ");
  ms = micros ();
  aes.do_aes_decrypt(cipher,aes.get_size(),check,key,bits,iv); 
  Serial.println(micros() - ms);
  
  Serial.print("- plain:   ");
  aes.printArray(plain,(bool)true); //print plain with no padding
 
  Serial.print("- cipher:  ");
  aes.printArray(cipher,(bool)false); //print cipher with padding
 
  Serial.print("- check:   ");
  aes.printArray(check,(bool)true); //print decrypted plain with no padding
  
  Serial.print("- iv:      ");
  aes.printArray(iv,16); //print iv
  printf("\n===================================================================================\n");
}
