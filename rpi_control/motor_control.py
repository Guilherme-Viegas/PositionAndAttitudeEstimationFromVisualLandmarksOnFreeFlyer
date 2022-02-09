#!/usr/bin/env python

#GPIO's with pwm port is 23, 24, 26
import RPi.GPIO as GPIO
import time

MOTOR_PIN_1 = 23
MOTOR_PIN_2 = 24
MOTOR_PIN_3 = 26

GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_PIN_1, GPIO.OUT)
GPIO.setup(MOTOR_PIN_2, GPIO.OUT)
GPIO.setup(MOTOR_PIN_3, GPIO.OUT)

motor_1 = GPIO.PWM(MOTOR_PIN_1, 50)
motor_2 = GPIO.PWM(MOTOR_PIN_2, 50)
motor_3 = GPIO.PWM(MOTOR_PIN_3, 50)

#Testing moving the motor 1
motor_1.start(0)
print("Starting 0")
time.sleep(10)

motor_1.ChangeDutyCycle(3)
print("3") # 30% duty cycle
time.sleep(10)
