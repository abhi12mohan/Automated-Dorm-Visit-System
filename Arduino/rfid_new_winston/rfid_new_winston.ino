#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>
#include <WiFi.h>
#include <TFT_eSPI.h>
#include<math.h>
#include <string.h>
#include "mbedtls/aes.h"

mbedtls_aes_context aes;
 
char * key = "tmf63mnxpy3hf2cw"; // ecryption key
 
char input[16];
unsigned char output[16];

const int RST_PIN = 22; // Reset pin
const int SS_PIN = 21; // Slave select pin

byte readCard[10];
int UID[10];
int UIDInt = 0;
char UIDinter[10];
char UIDstr [100]; //This will hold the scanned ID

char Dorm[] = "Maseeh"; /// This is the dorm that this ESP is associated with (which front desk is this?)

char network[] = "MIT";
char password[] = "iesc6s08";


const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const int POSTING_PERIOD = 6000; //periodicity of getting a number fact.
const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

const int ledPin = 12;  // Pin for pinger

// setting PWM properties
const int freq = 5000;
const int ledChannel = 0; // PWM channel for speaker/pinger
const int resolution = 8;

const int ledPin1 = 25;  //Pin for green LED
const int ledChannel1 = 1; // PWM channel for green LED

const int ledPin2 = 32; //Pin for red LED
const int ledChannel2 = 2; // PWM channel for red LED

void setup() {
  
  //Sets PWM properties for each channel
  ledcSetup(ledChannel, freq, resolution);
  ledcSetup(ledChannel1,freq, resolution);
  ledcSetup(ledChannel2,freq, resolution);
  
  
  // attach each PWM channel to the corresponding pin to be controlled
  ledcAttachPin(ledPin, ledChannel);
  ledcAttachPin(ledPin1, ledChannel1);
  ledcAttachPin(ledPin2, ledChannel2);
  
  Serial.begin(9600); // Initialize serial communications with the PC
  while (!Serial); // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
  Serial.println("Scan PICC to see UID, SAK, type, and data blocks...");

  WiFi.begin(network); //attempt to connect to wifi
  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  //Serial.println(network, password);
  while (WiFi.status() != WL_CONNECTED && count < 12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.println(WiFi.localIP().toString() + " (" + WiFi.macAddress() + ") (" + WiFi.SSID() + ")");
    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect :/  Going to restart");

    
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }
}

void loop() {
  
  if (!mfrc522.PICC_IsNewCardPresent()) { //Checks to see if the RFID reader is reading a new card. If not, 
                                          //return to top of loop
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) { //Checks to see if the RFID reader is getting a reading. IF not, 
                                        //return to top of loop
    return;
  }
  
  Serial.println("Scanned card's UID:");
  for (int i = 0; i < mfrc522.uid.size; i++) { //Reads in Bytes from RFID scan
    readCard[i] = mfrc522.uid.uidByte[i];
    UID[i] = (int)readCard[i]; //converts bytes to ints and puts into UID array
  }
  
  memset(UIDinter, '\0', sizeof(UIDinter));
  memset(UIDstr, '\0', sizeof(UIDstr));
  
  for (int i = 0;  i < mfrc522.uid.size; i++) { 
    sprintf(UIDinter, "%d", UID[i]); // Converts all of the read in ints to strings
    strcat(UIDstr, UIDinter);// Appends these strings onto UIDstr
  }
  //UIDstr is now the full hashed integer ID
  
  memset(UIDinter, '\0', sizeof(UIDinter));
  while(strlen(UIDstr) < 16){ //Appends question marks onto the ID to pad for 16 characters
    
    sprintf(UIDinter, "?");
    strcat(UIDstr, UIDinter);
  }
  
  memset(input, '\0', sizeof(input));
  for (int i = 0;  i < strlen(UIDstr); i++){ //copies UIDstr into input
    input[i]=UIDstr[i];
  }
  
  Serial.println(UIDstr);
  Serial.println(input);

  
  //Encrypts input Using AES encryption. Outputs to output
  mbedtls_aes_init( &aes );
  mbedtls_aes_setkey_enc( &aes, (const unsigned char*) key, strlen(key) * 8 );
  mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, (const unsigned char*)input, output);
  mbedtls_aes_free( &aes );
  

  memset(UIDinter, '\0', sizeof(UIDinter));
  memset(UIDstr, '\0', sizeof(UIDstr));
  
  for (int i = 0; i < 16; i++) { //stores the hex representation from output into UIDstr
 
    sprintf(UIDinter, "%02x", (int)output[i]);
    strcat(UIDstr, UIDinter);
  }
  
  mfrc522.PICC_HaltA(); // stop reading from RFID
  
  sendID(); //Post the ID to the server
 
}



void sendID() {
  
  char body[500]; //for body
  sprintf(body, "studentID=%s&dorm=%s",UIDstr, Dorm ); //generate body
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer, "POST http://chasermit.pythonanywhere.com/access HTTP/1.1\r\n");
  strcat(request_buffer, "Host: chasermit.pythonanywhere.com\r\n");
  strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len);
  strcat(request_buffer, "\r\n"); //new line from header to body
  strcat(request_buffer, body); //body
  strcat(request_buffer, "\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("chasermit.pythonanywhere.com", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
   
  if (strstr(response_buffer, "True") != NULL){ //If the server returns "True"
    ledcWrite(ledChannel, 100); //buzzer outputs light noise
    ledcWrite(ledChannel1, 100); //green LED turned on
    delay(400); //outputs for 400 ms
  }
  
  else{ //If the server didn't return "True"
    ledcWrite(ledChannel, 200); //buzzer outputs higher frequency noise
    ledcWrite(ledChannel2, 100); // red LED activated
    delay(1500); // outputs for 1.5 seconds
  }

  //Sets all PWM channels to 0 output
  ledcWrite(ledChannel, 0);
  ledcWrite(ledChannel1, 0);
  ledcWrite(ledChannel2, 0);
}
