#include <AFMotor.h>
#include <Servo.h>
#include <ArduinoJson.h>

const int servo1Pin = 9;

// Servo
Servo servo1;

AF_DCMotor motor1(1);  // M1
AF_DCMotor motor2(2);  // M2

void setup() {
  Serial.begin(9600);
  Serial.println("System initialized");

  servo1.attach(servo1Pin);
  servo1.write(0);
}

void pump(AF_DCMotor &motor, int time) {
  motor.setSpeed(255);
  motor.run(FORWARD);
  delay(time);
  motor.run(RELEASE);
}

void turn_servo(int angle) {
  servo1.write(angle);
  delay(500);
  servo1.write(0);
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
