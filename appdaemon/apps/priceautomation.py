import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class PriceAutomation(hass.Hass):

  def initialize(self):
    self.log("Hello from AppDaemon : PriceAutomation")
    self.listen_state(self.callback_offpeak_price, "schedule.hc", new = "on")
    self.listen_state(self.callback_peak_price, "schedule.hc", new = "off")

  def callback_offpeak_price(self, entity, attribute, old, new, kwargs):
    self.energy_price = self.get_entity("input_number.energy_price")
    self.energy_price.set_state(state="0.14")

  def callback_peak_price(self, entity, attribute, old, new, kwargs):
    self.energy_price = self.get_entity("input_number.energy_price")
    self.energy_price.set_state(state="0.22")