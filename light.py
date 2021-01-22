from lifxlan import LifxLAN
from suntime import Sun
from datetime import datetime
import pytz
import sys

LATITUDE=41.263923
LONGITUDE=13.632816

def light_on():
    lifx = LifxLAN(1)
    lights = lifx.get_lights()
    print("\nFound {} light(s)\n".format(len(lights)))
    lights[0].set_power("on")

def light_off():
    lifx = LifxLAN(1)
    lights = lifx.get_lights()
    print("\nFound {} light(s)\n".format(len(lights)))
    lights[0].set_power("off")

def schedule_light_on(cron,time):
    job = cron.new(
        command='/home/pi/Desktop/PycharmProjects/catDetector/venv/bin/python3.7 /home/pi/Desktop/PycharmProjects/catDetector/light.py on > /home/pi/Desktop/light_on_backup.log 2>&1')
    job.minute.on(50)
    job.hour.on(12)
    cron.write()

def schedule_light_off(cron,time):
    job = cron.new(
        command='/home/pi/Desktop/PycharmProjects/catDetector/venv/bin/python3.7 /home/pi/Desktop/PycharmProjects/catDetector/light.py off > /home/pi/Desktop/light_off_backup.log 2>&1')
    job.minute.on(time.minute)
    job.hour.on(time.hour)
    cron.write()

def get_light_status():
    lifx = LifxLAN(1)
    lights = lifx.get_lights()
    return lights[0].get_power()

def get_times():
    utc = pytz.UTC
    now = utc.localize(datetime.now())
    sun=Sun(LATITUDE,LONGITUDE)
    return now,sun.get_local_sunset_time(),sun.get_local_sunrise_time()

if __name__== "__main__":
    if sys.argv[1]=='on':
        light_on()
    else:
        light_off()