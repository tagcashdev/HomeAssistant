import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class PersonAutomation(hass.Hass):

  def initialize(self):
    self.mainDoor = 'sensor.fibaro_door_window_sensor_2_door_state_2'

    self.hanles_person = {}

    self.listen_state(self.callback_presence_state_change, "group.presence", new = "not_home")
    self.listen_state(self.callback_main_door, self.mainDoor, new = "22", duration = 300)

    self.listen_event(self.callback_notify_button_clicked_turn_off_lights, "mobile_app_notification_action", action = "turn_off_lights")

  def callback_presence_state_change(self, entity, attribute, old, new, kwargs):
    self.log("callback_presence_state_change called")
    self.check_main_door(self.mainDoor)
    self.check_lights()
    self.check_medias()
    self.check_doors()

  def callback_main_door(self, entity, attribute, old, new, kwargs):
    self.log("callback_main_door - called")
    self.check_main_door(entity)

  def callback_notify_button_clicked_turn_off_lights(self, event_name, data, kwargs):
    self.log("Notification button clicked : Turning off lights") 
    self.call_service("light/turn_off" , entity_id = "light.toutes_les_ampoules")

  def check_lights(self):
    self.log("check_lights called")
    lights = self.get_state('light.toutes_les_ampoules', attribute = "entity_id")
    lightsOn = []
    cntLightsOn = 0

    for light in lights:
      if self.get_state(light) == 'on':
        # force refresh state when manual turn off lights
        self.call_service('light/turn_on', entity_id=light)
        if self.get_state(light) == 'on':
          cntLightsOn += 1
          lightsOn.append(self.get_state(light, attribute = "friendly_name"))

    if cntLightsOn >= 1:
      strLightsOn = ", ".join(lightsOn)
      self.fire_event("NOTIFIER",
                action = "send_to_no_present",
                title = "Attention",
                message = "Les lumières : " + strLightsOn + " sont allumées alors que personne n'est présent",
                callback = [{
                        "title" : "Éteindre les lumières",
                        "event" : "turn_off_lights"}],
                tag = "home_empty_and_lights_on",
                until =  [{
                        "entity_id" : "group.presence",
                        "new_state" : "home"}])

  def check_medias(self):
    self.log("check_medias called")
    medias = ['media_player.family_room', 'media_player.luca_s_room']
    mediasOn = []
    cntMediasOn = 0

    for media in medias:
      if self.get_state(media) == 'playing' or self.get_state(media) == 'on':
        cntMediasOn += 1
        mediasOn.append(self.get_state(media, attribute = "friendly_name"))

    if cntMediasOn >= 1:
      strMediasOn = ", ".join(mediasOn)
      self.log(strMediasOn + " sont allumées")
      self.fire_event("NOTIFIER",
                action = "send_to_no_present",
                title = "Attention",
                message = strMediasOn + " sont allumées",
                tag = "home_empty_and_medias_on")

  def check_main_door(self, mainDoor):
    self.log("check_main_door - called")
    # check mainDoor independently 
    if self.get_state(mainDoor, attribute = "value") == 22:
      self.log("Porte principal est ouverte !")
      self.fire_event("NOTIFIER",
          action = "send_to_all",
          title = "Attention",
          message = "Porte principal est ouverte !")

  def check_doors(self):
    forecast = self.get_state("weather.sullens_hourly", attribute = "forecast")
    rainHours = []
    cnt = 0
    for f in forecast:
      if f['condition'] in ['rainy'] :
        rainHours.append(self.parse_time(f['datetime'].replace("T", " ").replace("+00:00", ""),'HH:MM'))
      cnt += 1

    self.log("check_doors called")
    windows = ['sensor.fibaro_door_window_sensor_2_door_state_4', 'sensor.fibaro_door_window_sensor_2_door_state_3']
    doors = []
    wdoors = ['sensor.fibaro_door_window_sensor_2_door_state']

    windowsDoors = []
    windowsDoors.extend(windows)
    windowsDoors.extend(doors)
    windowsDoors.extend(wdoors)

    windowsDoorsOpen = []
    cntWindowsDoorsOpen = 0

    for wd in windowsDoors:
      if self.get_state(wd, attribute = "value") == 22:
        cntWindowsDoorsOpen += 1
        windowsDoorsOpen.append(self.get_state(wd, attribute = "friendly_name").replace(": Access Control - Door state", ""))

    if cntWindowsDoorsOpen >= 1:
      strWindowsDoorsOpen = ", ".join(windowsDoorsOpen)
      rainMessage = strWindowsDoorsOpen + " sont ouverts, la prévision météo annonce de la pluie à partir de " + rainHours[0].strftime("%H:%M")
      if rainHours is not None:
        self.fire_event("NOTIFIER",
          action = "send_to_af",
          title = "Attention",
          message = rainMessage,
          tag = "home_empty_and_window_open")
      else:
        self.log(strWindowsDoorsOpen + " sont ouverts")
        self.fire_event("NOTIFIER",
          action = "send_to_af",
          title = "Attention",
          message = strWindowsDoorsOpen + " sont ouverts",
          tag = "home_empty_and_window_open")