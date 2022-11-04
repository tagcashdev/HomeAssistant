import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
import math

class LightsAutomation(hass.Hass):
    def initialize(self):        
        lights = [
            "light.ampoule_chambre_i_2", 
            "light.ampoule_color_chambre_ii",
            "light.ampoule_sonos_chambre_ii",
            "light.ampoule_sonos_salon", 
            "light.ampoule_salon", 
            "light.ampoule_2_cuisine", 
            "light.ampoule_cuisine",
            "light.ampoule_plafond_couloir",
            "light.ampoule_plafond_2_couloir",
            "light.ampoule_plafond_3_couloir"
        ]
        self.log("Hello from AppDaemon : LightsAutomation")
        self.listen_state(self.callback_motion, "binary_sensor.motion_sensor_motion_detection", new = "on")
        self.listen_state(self.callback_autoLight, lights, new = "on")

    def callback_motion(self, entity, attribute, old, new, kwargs):
        if self.get_state("input_boolean.automotionlight") == "on":
            illuminance = float(self.get_state('sensor.motion_sensor_illuminance'))
            if illuminance < 10:
                self.call_service('light/turn_on', entity_id="light.ampoule_plafond_couloir")
                self.call_service('light/turn_on', entity_id="light.ampoule_plafond_2_couloir")
                self.call_service('light/turn_on', entity_id="light.ampoule_plafond_3_couloir")
                self.run_in(self.turn_off_motion_delay, 5)
            else:
                self.run_in(self.turn_off_motion_delay, 5)

    def turn_off_motion_delay(self, kwargs):
        if self.get_state("binary_sensor.motion_sensor_motion_detection") == "on":
            self.run_in(self.turn_off_motion_delay, 10)  
        else:
            self.call_service('light/turn_off', entity_id="light.ampoule_plafond_couloir")
            self.call_service('light/turn_off', entity_id="light.ampoule_plafond_2_couloir")
            self.call_service('light/turn_off', entity_id="light.ampoule_plafond_3_couloir")

    def callback_autoLight(self, entity, attribute, old, new, kwargs):
        if self.get_state("input_boolean.autolight") == "on":
            # sunrise : lever du soleil
            self.log("sunrise : lever du soleil = " + str(self.sunrise()))
            # sunset  : coucher du soleil
            self.log("sunset : coucher du soleil = " + str(self.sunset()))
            
            b = 100

            if self.now_is_between("18:00:00", "06:59:59"):
                k = 2000
            if self.now_is_between("07:00:00", "07:29:59") or self.now_is_between("17:30:00", "17:59:59"):
                k = 2975
            if self.now_is_between("07:30:00", "07:59:59") or self.now_is_between("17:00:00", "17:29:59"):
                k = 2750
            if self.now_is_between("08:00:00", "08:29:59") or self.now_is_between("16:30:00", "16:59:59"):
                k = 3125
            if self.now_is_between("08:30:00", "08:59:59") or self.now_is_between("16:00:00", "16:29:59"):
                k = 3500
            if self.now_is_between("09:00:00", "09:29:59") or self.now_is_between("15:30:00", "15:59:59"):
                k = 4250
            if self.now_is_between("09:30:00", "09:59:59") or self.now_is_between("15:00:00", "15:29:59"):
                k = 4625
            if self.now_is_between("10:00:00", "10:29:59") or self.now_is_between("14:30:00", "14:59:59"):
                k = 5000
            if self.now_is_between("10:30:00", "10:59:59") or self.now_is_between("14:00:00", "14:29:59"):
                k = 5375
            if self.now_is_between("11:00:00", "11:29:59") or self.now_is_between("13:30:00", "13:59:59"):
                k = 5750
            if self.now_is_between("11:30:00", "11:59:59") or self.now_is_between("13:00:00", "13:29:59"):
                k = 6125
            if self.now_is_between("12:00:00", "12:59:59"):
                k = 6500

            if self.now_is_between("sunset - 00:07:00", "sunset + 00:07:59") or self.now_is_between("sunrise + 01:16:00", "sunrise + 01:23:59"):
                b = 90
            if self.now_is_between("sunset + 00:08:00", "sunset + 00:22:59") or self.now_is_between("sunrise + 01:08:00", "sunrise + 01:23:59"):
                b = 80
            if self.now_is_between("sunset + 00:23:00", "sunset + 00:37:59") or self.now_is_between("sunrise + 00:53:00", "sunrise + 01:07:59"):
                b = 70
            if self.now_is_between("sunset + 00:38:00", "sunset + 00:44:59") or self.now_is_between("sunrise + 00:45:00", "sunrise + 00:52:59"):
                b = 60
            if self.now_is_between("sunset + 00:45:00", "sunset + 00:52:59") or self.now_is_between("sunrise + 00:38:00", "sunrise + 00:44:59"):
                b = 50
            if self.now_is_between("sunset + 00:53:00", "sunset + 01:07:59") or self.now_is_between("sunrise + 00:23:00", "sunrise + 00:37:59"):
                b = 40
            if self.now_is_between("sunset + 01:08:00", "sunset + 01:15:59") or self.now_is_between("sunrise + 00:08:00", "sunrise + 00:22:59"):
                b = 30
            if self.now_is_between("sunset + 01:16:00", "sunset + 01:23:59") or self.now_is_between("sunrise - 00:07:00", "sunrise + 00:07:59"):
                b = 20
            if self.now_is_between("sunset + 01:24:00", "sunrise - 00:06:59"):
                b = 10

            self.log("kelvin : " + str(k))
            self.log("brightness_pct : " + str(b))
            self.autolight(entity, k, b)
                
            self.turn_on(entity_id = entity, kelvin = k, brightness_pct = round(b))

    def autolight(self, entity, kelvin, brightness_pct):
        if self.get_state("input_boolean.autolight") == "on":
            self.log("autolight on")
            self.log("called entity : " + entity)
            self.log("kwargs kelvin: " + str(kelvin))
            self.log("kwargs brightness_pct: " + str(brightness_pct))
        else:
            self.log("autolight off")