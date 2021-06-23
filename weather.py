#!/usr/bin/python2
# -*- coding: utf-8 -*-
import codecs
import sys
import json
import urllib2
from datetime import date, datetime
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
ICON_BASE = 127779
SUNNY = unichr(ICON_BASE + 0) + unichr(0xfe0f)
LIGHT_CLOUD = unichr(ICON_BASE + 1) + unichr(0xfe0f)
CLOUDY = unichr(ICON_BASE + 2) + unichr(0xfe0f)
SHOWERS = unichr(ICON_BASE + 3) + unichr(0xfe0f)
RAIN = unichr(ICON_BASE + 4) + unichr(0xfe0f)
SNOW = unichr(ICON_BASE + 5) + unichr(0xfe0f)
STORM = unichr(ICON_BASE + 6) + unichr(0xfe0f)
WIND = unichr(ICON_BASE + 7) + unichr(0xfe0f)
FOG = unichr(ICON_BASE + 8) + unichr(0xfe0f)
ICON_MAP = {
    1: SUNNY,
    2: LIGHT_CLOUD,
    3: CLOUDY,
    4: CLOUDY,
    5: CLOUDY,
    5: CLOUDY,
    6: SHOWERS,
    7: SHOWERS,
    8: SHOWERS,
    9: SHOWERS,
    10: SHOWERS,
    11: CLOUDY + SNOW,
    12: STORM,
    13: STORM,
    14: RAIN,
    15: RAIN,
    16: SNOW,
    17: RAIN,
    18: RAIN + SNOW,
    19: SNOW,
    20: RAIN + RAIN,
    21: SNOW + RAIN,
    22: SNOW + SNOW,
    23: STORM,
    24: STORM,
    25: STORM + STORM,
    26: SUNNY,
    27: SUNNY,
    28: FOG,
    29: SHOWERS,
    30: LIGHT_CLOUD,
    31: LIGHT_CLOUD,
    32: SHOWERS,
    33: RAIN,
    34: SNOW,
    35: CLOUDY,
}
def get_icon(meteo_nr):
  return ICON_MAP.get(meteo_nr, '?')

def get_day(dateStr):
  y, m, d = [int(s) for s in dateStr.split('-')]
  return date(y, m, d).strftime('%a')

def rain_between(start, end, weather):
  hours_of_detailed_rain = len(weather['graph']['precipitation10m'])/6
  rain = []
  for i in range(hours_of_detailed_rain):
    rain.append(sum(weather['graph']['precipitation10m'][i*6:(i+1)*6])/6.0)
  rain += weather['graph']['precipitation1h']
  return sum(rain[start:end])

def leave_at(weather):
  now = datetime.now()
  now = now.hour*6+(now.minute-1)/10+1
  if now > 17*6+4:
    return " go home!"
  detailed_rain = weather['graph']['precipitation10m']
  if len(detailed_rain) < 18*6:
    return ""
  if sum(detailed_rain[now:18*6+1]) == 0:
    return ""
  best_leaving = sorted([(sum(detailed_rain[t:t+2]), -t) for t in range(max(16*6+4, now), 18*6-1)])
  return " leave@%d:%d0:%.1f" % (-best_leaving[0][1]/6, -best_leaving[0][1]%6, best_leaving[0][0]/6)

def main(argv):
  weather = readWeather()
  rain = ""
  now = datetime.now().hour
  if rain_between(now, now+24, weather) > 0:
      rain += " "
      rain += unichr(0x2614)
      rain += " %.1fmm "%rain_between(now, now+24, weather)

      next_days_rain = [(hour, rain_between(hour, hour+1, weather), rain_between(hour+1, now+24, weather)) for hour in range(now, now+24)] 
      max_rain = max(x[1] for x in next_days_rain)
      for hour, hour_rain, remaining_rain in next_days_rain:
          # insert vertical bars at 8am, noon, 6pm and midnight (latter thicker)
          if hour == 24:
              rain +="<span background='#ccc'>"+unichr(0x2006)+"</span>"
          elif hour % 24 in (8, 12, 18):
              rain +="<span background='#ccc'>"+unichr(0x200a)+"</span>"
          # colour is absolute and based off the MeteoSwiss app's scale
          if hour_rain <= 0.2: 
              rain += "<span color='#808080'>"
          elif hour_rain <= 1: 
              rain += "<span color='#9b7d95'>"
          elif hour_rain <= 2:   
              rain += "<span color='#0000fe'>"
          elif hour_rain <= 4:   
              rain += "<span color='#058c2d'>"
          elif hour_rain <= 6:
              rain += "<span color='#05ff05'>"
          elif hour_rain <= 10:
              rain += "<span color='#ffff00'>"
          elif hour_rain <= 20:
              rain += "<span color='#ffc801'>"
          elif hour_rain <= 40:
              rain += "<span color='#ff7d01'>"
          elif hour_rain <= 60:
              rain += "<span color='#ff1901'>"
          else:
              rain += "<span color='#af00db'>"
          # bar graph height is relative to max rain over the next 24h, but never smaller than one step = 0.1mm
          STEPS = 7
          rain += unichr(min(0x2588, int((hour_rain / max(0.1 * STEPS, max_rain)) * STEPS)+0x2582)) if hour_rain else unichr(0x2581)
          rain += "</span>"
          if not remaining_rain:
              break
  #if rain_between(now, 32, weather) > 0:
  #  rain += " "
  #  rain += unichr(0x2614)
  #  if rain_between(max(8, now), 12, weather):
  #    rain += " morn:%.1f" % rain_between(max(8, now), 12, weather)
  #  if rain_between(max(12, now), 18, weather):
  #    rain += " arvo:%.1f" % rain_between(max(12, now), 18, weather)
  #  if rain_between(max(18, now), 24, weather):
  #    rain += " even:%.1f" % rain_between(max(18, now), 24, weather)
  #  if rain_between(24, 32, weather):
  #    rain += " night:%.1f" % rain_between(24, 32, weather)

  print(u'{currentIcon} {currentTemp}°C (≤ {todayMax}){rain}'.format(
            currentIcon=get_icon(weather['currentWeather']['icon']),
            currentTemp=weather['currentWeather']['temperature'],
            todayMax=weather['forecast'][0]['temperatureMax'],
            rain=rain
  ))
  print(u'{currentIcon} {currentTemp}°C (≤ {todayMax}){rain}'.format(
            currentIcon=get_icon(weather['currentWeather']['icon']),
            currentTemp=weather['currentWeather']['temperature'],
            todayMax=weather['forecast'][0]['temperatureMax'],
            rain=" ".join(rain.split(" ")[:2])
  ))
def readWeather():
  PLZ = 8055
  return json.load(
      urllib2.urlopen(
          'https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz=%d00' % PLZ))
if __name__ == '__main__':
  main(sys.argv)
