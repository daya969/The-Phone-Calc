import pygame
import os
import time
import RPi.GPIO as GPIO
from subprocess import Popen

DEAD_BUTTON = 17
PLUS_BUTTON = 27
EQUAL_BUTTON = 22
MINUS_BUTTON = 23

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (155, 165, 150)
FONT_COLOR = (20, 20, 20)

class PhantomSystem:
    def __init__(self):
        os.system("setterm -cursor off")
        os.system("clear")
        os.system("rfkill unblock wifi")
        os.system("rfkill unblock bluetooth")
        
        pygame.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        self.font = pygame.font.SysFont("monospace", 50, bold=True)
        
        GPIO.setmode(GPIO.BCM)
        for p in [DEAD_BUTTON, PLUS_BUTTON, EQUAL_BUTTON, MINUS_BUTTON]:
            GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
        self.active = False
        self.val = "0"
        self.proc = None

    def ui(self, t):
        self.screen.fill(BG_COLOR)
        label = self.font.render(t, True, FONT_COLOR)
        self.screen.blit(label, (SCREEN_WIDTH - label.get_width() - 15, 70))
        pygame.display.flip()

    def boot_otg(self):
        usb = "/dev/sda1"
        mnt = "/mnt/usb"
        if os.path.exists(usb):
            if not os.path.exists(mnt): os.makedirs(mnt)
            os.system(f"mount {usb} {mnt}")
            if os.path.exists(f"{mnt}/start_android.sh"):
                return f"{mnt}/start_android.sh"
        return None

    def kill(self):
        if self.active:
            os.system("amixer set Master mute")
            if self.proc: self.proc.terminate()
            self.active = False
            self.val = "67"

    def start(self):
        os.system("amixer set Master 100%")
        os.system("amixer cset numid=3 1")
        self.active = True
        script = self.boot_otg()
        if script:
            self.proc = Popen(["sh", script])
        else:
            self.proc = Popen(["chromium-browser", "--kiosk", "https://discord.com"])

    def run(self):
        while True:
            if GPIO.input(DEAD_BUTTON) == GPIO.LOW:
                time.sleep(0.05)
                if GPIO.input(PLUS_BUTTON) == GPIO.LOW and GPIO.input(EQUAL_BUTTON) == GPIO.LOW:
                    if not self.active: self.start()
                else:
                    self.kill()

            if GPIO.input(DEAD_BUTTON) == GPIO.LOW and GPIO.input(MINUS_BUTTON) == GPIO.LOW:
                self.active = False
                self.val = "0"

            if not self.active:
                self.ui(self.val)
            time.sleep(0.1)

if __name__ == "__main__":
    app = PhantomSystem()
    try:
        app.run()
    except:
        GPIO.cleanup()
        pygame.quit()

