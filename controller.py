"""
controller.py — Handles all controller input detection and reading
Optimized for Cosmic Byte Ares (Xbox 360 protocol)
VID: 0x45e PID: 0x28e
"""

import pygame


class ControllerManager:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.controller = None
        self.dead_zone = 0.1
        self.sensitivity = 1.0
        self.button_map = {}

    def get_connected_controllers(self):
        """Returns list of connected controller names"""
        pygame.joystick.quit()
        pygame.joystick.init()
        controllers = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            controllers.append((i, joy.get_name()))
        return controllers

    def connect(self, index=0):
        """Connect to a controller by index"""
        try:
            self.controller = pygame.joystick.Joystick(index)
            self.controller.init()
            return True
        except Exception as e:
            print(f"Failed to connect controller: {e}")
            return False

    def disconnect(self):
        """Disconnect the current controller"""
        if self.controller:
            self.controller.quit()
            self.controller = None

    def get_axis(self, axis_id):
        """Get axis value with dead zone applied"""
        if not self.controller:
            return 0.0
        pygame.event.pump()
        value = self.controller.get_axis(axis_id)
        if abs(value) < self.dead_zone:
            return 0.0
        value = value * self.sensitivity
        return round(max(-1.0, min(1.0, value)), 3)

    def get_button(self, button_id):
        """Get button state (True = pressed)"""
        if not self.controller:
            return False
        pygame.event.pump()
        actual_button = self.button_map.get(button_id, button_id)
        try:
            return bool(self.controller.get_button(actual_button))
        except Exception:
            return False

    def get_all_axes(self):
        """Get all axis values"""
        if not self.controller:
            return []
        pygame.event.pump()
        axes = []
        for i in range(self.controller.get_numaxes()):
            axes.append((i, self.get_axis(i)))
        return axes

    def get_all_buttons(self):
        """Get all button states"""
        if not self.controller:
            return []
        pygame.event.pump()
        buttons = []
        for i in range(self.controller.get_numbuttons()):
            buttons.append((i, self.get_button(i)))
        return buttons

    def get_hat(self):
        """Get D-pad (hat) value"""
        if not self.controller:
            return (0, 0)
        pygame.event.pump()
        if self.controller.get_numhats() > 0:
            return self.controller.get_hat(0)
        return (0, 0)

    def get_controller_info(self):
        """Get controller name and stats"""
        if not self.controller:
            return None
        return {
            "name": self.controller.get_name(),
            "axes": self.controller.get_numaxes(),
            "buttons": self.controller.get_numbuttons(),
            "hats": self.controller.get_numhats(),
        }

    def set_dead_zone(self, value):
        self.dead_zone = max(0.0, min(1.0, value))

    def set_sensitivity(self, value):
        self.sensitivity = max(0.1, min(2.0, value))

    def remap_button(self, original, new):
        self.button_map[original] = new

    def reset_button_map(self):
        self.button_map = {}
