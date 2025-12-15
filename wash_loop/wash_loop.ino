#include <AFMotor.h>
#include <Servo.h>
#include <ArduinoJson.h>

// Define the pins where the servos are connected

const int servo1Pin = 9;

void setup() {
  Serial.begin(9600);
  Serial.println("System initialized");

}

// Pump motor forward for 'time' milliseconds
void pump(int motor_int, int time) {

  AF_DCMotor motor(motor_int);

  motor.setSpeed(255);
  motor.run(FORWARD);
  delay(time);
  motor.run(RELEASE);
}

void turn_servo(int angle){

  servo.attach(servo1Pin);
  servo.write(angle);
  servo.write(0);
  servo.detach();

}

void loop() {

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("Received command: ");
    Serial.println(command);

    if (command == "pump_soap") {
      pump(motor1, 5000);
    } 
    else if (command == "pump_water") {
      pump(motor2, 5000);
    } 
    else if (command == "rotate") {
      turn_servo(180);
    } 
    else {
      Serial.println("Unknown command");
    }
  }
}