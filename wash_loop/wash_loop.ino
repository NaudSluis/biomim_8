// This file contains the code for the Arduino. Those include, water pumps and servo's.

#include <AFMotor.h>
#include <Servo.h>
#include <ArduinoJson.h>

// Pins on Arduino
const int servo1Pin = 9;
const int servo2Pin = 10;

// Servo
Servo servo1;
Servo servo2;

// Motors
AF_DCMotor motor1(1);  // M1
AF_DCMotor motor2(2);  // M2
AF_DCMotor motor3(3);  // M3
AF_DCMotor motor4(4);  // M4

void setup() {
  Serial.begin(9600);
  Serial.println("System initialized");
}

void pump(AF_DCMotor &motor_one, AF_DCMotor &motor_two, int time) {
  // Run a pump for x amount of time
  // param motor: specify motor
  // param time: amount of time in miliseconds
  motor_one.setSpeed(255);
  motor_two.setSpeed(255);
  motor_one.run(FORWARD);
  motor_two.run(FORWARD);
  delay(time);
  motor_one.run(RELEASE);
  motor_one.run(RELEASE);
}

void turn_servo_const() {
  // Turn the constant servo for 2.5 seconds one way, then 2.5 the other
  servo1.attach(servo1Pin);
  servo1.write(0);
  delay(2500);
  servo1.write(180);
  delay(2500);
  servo1.detach();
}

void turn_servo_degree_forward() {
  // Turn degree servo to 180 degree
  servo2.attach(servo2Pin);
  servo2.write(4m0);
  delay(2500);
  servo2.detach();
}

void turn_servo_degree_backward() {
  // Turn degree servo to 0 degree
  servo2.attach(servo2Pin);
  servo2.write(0);
  delay(2500);
  servo2.detach();
}

void loop() {
  // Gets command from Pi and does the corresponding action
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("Received command: ");
    Serial.println(command);

    if (command == "pump_soap") {
      pump(motor1, motor2, 30000);
    }
    else if (command == "pump_water") {
      pump(motor3, motor4, 30000);
    }
    else if (command == "rotate") {
      turn_servo_const();
    }
    else if (command == "forward") {
      turn_servo_degree_forward();
    }
    else if (command == "backward") {
      turn_servo_degree_backward();
    }
    else {
      Serial.println("Unknown command");
    }
  }
}
