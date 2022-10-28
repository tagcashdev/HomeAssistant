import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class OffpeakAutomation(hass.Hass):

  def initialize(self):
    self.log("Hello from AppDaemon : OffpeakAutomation")
    
    self.handles = {}
    self.lucaSleep = self.get_state("input_datetime.heure_dodo")
    self.vl = 0.2

    self.handles["sleep_changed"] = self.listen_state(self.callback_sleep_changed,"input_datetime.heure_dodo")
    self.handles["luca_sleep_time"] = self.run_daily(self.callback_lucaSleepTime, self.lucaSleep)
    self.handles["off_peak_time"] = self.run_daily(self.callback_offpeak_automation, "22:00:00")

    self.handles["luca_sleep_1"] = self.listen_state(self.callback_luca_sleep_1, "input_boolean.luca_1", new = "on")
    self.handles["luca_sleep_2"] = self.listen_state(self.callback_luca_sleep_2, "input_boolean.luca_2", new = "on")
    self.handles["luca_sleep_3"] = self.listen_state(self.callback_luca_sleep_3, "input_boolean.luca_3", new = "on")

    self.handles["notify_button_clicked_play_dishwasher_offpeak"] = self.listen_event(self.callback_notify_button_clicked_play_dishwasher_offpeak, "mobile_app_notification_action", action = "play_dishwasher_offpeak")

  def callback_offpeak_automation(self, start):
    if self.get_state("binary_sensor.011030387805000808_bsh_common_status_doorstate") == "off":
      self.fire_event("NOTIFIER",
          action = "send_to_present",
          icon = "mdi:dishwasher",
          title = "✅ Lave-Vaiselle",
          callback = [{
                  "title" : "Lancer le programme",
                  "event" : "play_dishwasher_offpeak"}],
          message = "Le lave-vaisselle est prêt à être lancer",
          tag = "at_home_and_dishwasher_ready")
    else:
      self.fire_event("NOTIFIER",
          action = "send_to_present",
          icon = "mdi:dishwasher-alert",
          title = "⚠️ Lave-Vaiselle",
          message = "Oups, la porte du lave-vaisselle est ouverte, veuillez fermer la porte et lancer manuellement le programme",
          tag = "at_home_and_dishwasher_error")

  def callback_notify_button_clicked_play_dishwasher_offpeak(self, event_name, data, kwargs):
    self.call_service('switch/turn_on', entity_id = "switch.011030387805000808_bsh_common_setting_powerstate")
    self.call_service('home_connect_alt/select_program', program_key = "Dishcare.Dishwasher.Program.Eco50")

  def callback_lucaSleepTime(self, start):
    self.log("lucaSleepTime") 
    # Vérifier si présence
    if self.get_state("group.presence") == "home":
      self.call_service('light/turn_on', entity_id = "light.ampoule_sonos_salon")
      if self.get_state("media_player.lg") == "on":
        self.call_service('webostv/button', entity_id = "media_player.lg", button = "PAUSE")

  def callback_luca_sleep_1(self, entity, attribute, old, new, kwargs):
    self.turn_on("light.ampoule_color_chambre_ii")
    self.turn_off("input_boolean.autolight")
    self.turn_on("light.ampoule_color_chambre_ii",  color_name = "blue")

  def callback_luca_sleep_2(self, entity, attribute, old, new, kwargs):
    self.turn_off("input_boolean.luca_1");
    self.turn_on("light.ampoule_color_chambre_ii",  color_name = "blue", brightness_pct = 1)
    self.call_service("media_player/media_play", entity_id = "media_player.luca_s_room")
    self.call_service("media_player/volume_set", entity_id = "media_player.luca_s_room", volume_level = self.vl)

  def callback_luca_sleep_3(self, entity, attribute, old, new, kwargs):
    self.vl = 0.1
    self.turn_off("input_boolean.luca_2");
    self.turn_off("light.ampoule_color_chambre_ii")
    self.turn_on("input_boolean.autolight")
    self.call_service("media_player/volume_set", entity_id = "media_player.luca_s_room", volume_level = self.vl)
    self.luca_sleep_end_loop("run_in5")

  def luca_sleep_end_loop(self, kwargs):
    self.log("loop")
    self.log("vl: "+str(round(self.vl,2)))
    tvl = self.vl
    self.log("tvl: "+str(round(tvl,2)))
    if tvl <= 0.0:
      self.log("stop")
      self.turn_off("input_boolean.luca_3");
      self.call_service("media_player/media_pause", entity_id = "media_player.luca_s_room")
      self.cancel_timer(self.handles["luca_sleep_end_loop"])
    else:
      self.log("else: " + str(self.vl))
      self.call_service("media_player/volume_set", entity_id = "media_player.luca_s_room", volume_level = self.vl)
      self.handles["luca_sleep_end_loop"] = self.run_in(self.luca_sleep_end_loop, 12)

    pr = tvl - 0.01
    self.vl = round(pr, 2)

  def callback_sleep_changed(self, entity, attribute, old, new, kwargs):
    self.time_changed(handle_key = "luca_sleep_time", newtime = "input_datetime.heure_dodo", callbfunc = self.callback_lucaSleepTime)

  def time_changed(self, handle_key, newtime, callbfunc):
    self.cancel_timer(self.handles[handle_key])
    newtime = self.get_state(newtime)
    self.handles[handle_key] = self.run_daily(callbfunc, newtime)