#include <AFMotor.h>
#include <Servo.h>
#include <ArduinoJson.h>

Servo servo1;



// Define the pins where the servos are connected

const int servo1Pin = 9;
const int servo2Pin = 10;

void setup() {
  Serial.begin(9600);
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  Serial.println("System initialized");

}

// Pump motor forward for 'time' milliseconds
void pump(int motor_int, int time) {
  AF_DCMotor motor(motor_int);
  motor.run(FORWARD);
  motor.setSpeed(255);
  Serial.print("PUMP: Motor ");
  Serial.print(motor_int);
  Serial.print(" running FORWARD for ");
  Serial.print(time);
  Serial.println(" ms");
  delay(time);
}

// Pause motor for 'time' milliseconds
void pump_pause(int motor_int, int time) {
  AF_DCMotor motor(motor_int);
  motor.run(RELEASE);
  Serial.print("PAUSE: Motor ");
  Serial.print(motor_int);
  Serial.print(" paused for ");
  Serial.print(time);
  Serial.println(" ms");
  delay(time);
}

// Stop motor immediately
void pump_stop(int motor_int) {
  AF_DCMotor motor(motor_int);
  motor.run(RELEASE);
  Serial.print("STOP: Motor ");
  Serial.println(motor_int);
}

// Placeholder: change the splitter
void change_splitser() {
  Serial.println("Splitter changed");
}

// Ensure water goes to soap path
void water_to_soap(char port_status) {
  if (port_status == '0') { // splitter is on water
    Serial.println("Changing from water to soap");
    change_splitser();
  } else if (port_status == '1') {
    Serial.println("Already set to soap, no change needed");
  }
}

// Ensure soap goes to water path
void soap_to_water(char port_status) {
  if (port_status == '0') {
    Serial.println("Already set to water, no change needed");
  } else if (port_status == '1') {
    Serial.println("Changing from soap to water");
    change_splitser();
  }
}

void turn_servo(Servo &servo, int angle){
  servo.write(angle);
  Serial.print("Servo turned ");
  Serial.print(angle);
  Serial.println(" degrees.");
}

void stepper_test(){
  motor.setSpeed(10);  // rpm
  motor.step(512, FORWARD, DOUBLE); // 512 steps = ~1/4 rev
  motor.step(512, BACKWARD, DOUBLE); // go back
  motor.release();
}

void loop() {
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();

    // Log received byte with timestamp
    Serial.print("Received byte: '");
    Serial.print(incomingByte);
    Serial.print("' at millis()=");
    Serial.println(millis());

    if (incomingByte == '0') {
      water_to_soap(incomingByte);
      pump(4, 5000); // motor 4, 5000 ms
      pump_stop(4);
    } 
    else if (incomingByte == '1') {
      soap_to_water(incomingByte);
      pump(4, 5000);
      pump_stop(4);
    } 
    else if (incomingByte == '2'){
      turn_servo(servo1, 120);
      turn_servo(servo2, 120);
      delay(2000);
      turn_servo(servo1, -90);
      turn_servo(servo2, -90);
      delay(2000);
      turn_servo(servo1, 1);
      turn_servo(servo2, 1);
      delay(2000);
      servo1.detach();
      servo2.detach();
      }
    else if (incomingByte == '4') {
        Serial.println("Stepper test!");

        servo1.write(50);
        servo2.write(50);

    } 
    else {
      Serial.print("Unknown byte received: ");
      Serial.println(incomingByte);
    }
  }
}
