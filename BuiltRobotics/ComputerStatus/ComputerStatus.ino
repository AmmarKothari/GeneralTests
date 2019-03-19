/*
  LiquidCrystal Library - Serial Input

 Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
 library works with all LCD displays that are compatible with the
 Hitachi HD44780 driver. There are many of them out there, and you
 can usually tell them by the 16-pin interface.

 This sketch displays text sent over the serial port
 (e.g. from the Serial Monitor) on an attached LCD.

 The circuit:
 * LCD RS pin to digital pin 12
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)

 Library originally added 18 Apr 2008
 by David A. Mellis
 library modified 5 Jul 2009
 by Limor Fried (http://www.ladyada.net)
 example added 9 Jul 2009
 by Tom Igoe
 modified 22 Nov 2010
 by Tom Igoe

 This example code is in the public domain.

 http://www.arduino.cc/en/Tutorial/LiquidCrystalSerial
 */

// include the library code:
#include <LiquidCrystal.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
String status;

int PRINT_LINES = 2;
int MAX_CHARS_PER_LINE = 16;
int MAX_STR_LEN = PRINT_LINES * MAX_CHARS_PER_LINE;
bool no_device_detected = true;

void setup() {
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // initialize the serial communications:
  Serial.begin(9600);
}

void get_serial(){
  // when characters arrive over the serial port...
  if (Serial.available()) {
    // wait a bit for the entire message to arrive
    delay(100);
    // read all the available characters
    while (Serial.available() > 0) {
      // display each character to the LCD
      status = Serial.readString();
    }
  }
}

void print_32_chars(String print_str) {
  // prints two lines of characters
  for (int line=0; line < PRINT_LINES; line++) {
    lcd.setCursor(0, line);
    lcd.print(print_str.substring(line*MAX_CHARS_PER_LINE,(line+1)*MAX_CHARS_PER_LINE));
  };
};

String pad_to_32_chars(String orig_str) {
  // pads string to be 32 chars for printing
  while (orig_str.length() < MAX_STR_LEN) {
    orig_str.concat(" ");
  };
  return orig_str;
};

// ---------------------------
// Printing Methods
// ---------------------------

void streaming_print() {
  for (int let_i=MAX_STR_LEN; let_i < status.length(); let_i++) {
    print_32_chars(status.substring(let_i-MAX_STR_LEN, let_i));
    delay(500);
  }
  delay(1000);
}

void sectional_print() {
  for (int let_i=MAX_STR_LEN; let_i < status.length(); let_i++) {
    print_32_chars(status.substring(let_i-MAX_STR_LEN, let_i));
    delay(500);
  }
  delay(1000);
  
}



void print_status() {
  if (status.length() <= MAX_STR_LEN) {
    status = pad_to_32_chars(status);
    print_32_chars(status);
  }
  else {
    streaming_print();
  }
}
void loop() {
  if (no_device_detected) {
    Serial.write("Computer Status Device\n");
  }
  get_serial();

  print_status();
}
