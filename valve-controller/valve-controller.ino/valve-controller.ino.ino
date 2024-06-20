#include <Servo.h>
Servo s;
int pos;
void setup() {
  Serial.begin(9600);
  s.attach(3);
}
void loop() {
  s.write(pos);
  if (Serial.available()) {
    pos = Serial.parseInt();
  }
}