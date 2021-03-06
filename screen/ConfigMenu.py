import screen
import data
import graphics
import pygame
import os

class ConfigMenu(object):

    def __init__(self, origin, camera=None):
        self.origin = origin

        self.configMenu_list = graphics.userInterface.Interface()

        self.resolutions_strings = ["1024x768", "1280x768", "1600x900", "1920x1080"]
        self.resolutions = [(1024, 768), (1280, 768), (1600, 900), (1920, 1080)]
        self.resolution_index = self.resolutions.index((data.config.WIDTH, data.config.HEIGHT))

        self.languages = os.listdir("../../lang")
        self.languages_strings = map(data.translate, self.languages)
        self.language_index = self.languages.index(data.config.LANG)

        self.configMenu_list.addButton(0, "arrow_back.png", data.config.WIDTH * 0.1, data.config.HEIGHT * 0.1, mask="arrow_leftMask.png")

        self.configMenu_list.addButton(1, "pointer_left.png", data.config.WIDTH * 0.48 - 70 + 100, data.config.HEIGHT * 0.7, mask="pointer_leftMask.png")
        self.configMenu_list.addButton(2, "pointer_right.png", data.config.WIDTH * 0.68 + 70 + 100, data.config.HEIGHT * 0.7, mask="pointer_rightMask.png")

        self.configMenu_list.addButton(3, "pointer_left.png", data.config.WIDTH * 0.48 - 70 + 100, data.config.HEIGHT * 0.85, mask="pointer_leftMask.png")
        self.configMenu_list.addButton(4, "pointer_right.png", data.config.WIDTH * 0.68 + 70 + 100, data.config.HEIGHT * 0.85, mask="pointer_rightMask.png")

        self.configMenu_list.addCheckBox("fullscreen", "checkbox.png", data.config.WIDTH * 0.58 + 100, data.config.HEIGHT * 0.55, checked=data.config.FULLSCREEN)

        self.configMenu_list.addSlider("musicVolume", "slider.png", "slidermask.png", (0, 100), data.config.MUSIC, data.config.WIDTH * 0.58 + 100 , data.config.HEIGHT * 0.3)
        self.configMenu_list.addSlider("musicSound", "slider.png", "slidermask.png", (0, 100), data.config.SOUND, data.config.WIDTH * 0.58 + 100, data.config.HEIGHT * 0.4)

        self.shadow = pygame.Surface((data.config.WIDTH, data.config.HEIGHT))
        self.shadow.set_alpha(224, pygame.RLEACCEL)

        self.camera = camera

        self.lastSound = data.config.SOUND

    def displayOutput(self, display):

        if self.origin is not screen.Menu:
            display.blit(self.shadow, (0, 0))
        else: display.blit(data.getResource("rocks.png"), (data.config.WIDTH * 0.5 - 960, data.config.HEIGHT * 0.5 - 540))

        self.configMenu_list.draw(display)

        graphics.drawText(display, data.translate("configurations"), data.config.WIDTH * 0.5, data.config.HEIGHT * 0.1, color=0xF0F0F0, size=40, formatting="center")
        graphics.drawText(display, data.translate("music"), data.config.WIDTH * 0.35 - 240, data.config.HEIGHT * 0.3, color=0xF0F0F0, size=30)
        graphics.drawText(display, data.translate("sound"), data.config.WIDTH * 0.35 - 240, data.config.HEIGHT * 0.4, color=0xF0F0F0, size=30)
        graphics.drawText(display, data.translate("fullscreen"), data.config.WIDTH * 0.35 - 240, data.config.HEIGHT * 0.55, color=0xF0F0F0, size=30)
        graphics.drawText(display, data.translate("resolution"), data.config.WIDTH * 0.35 - 240, data.config.HEIGHT * 0.7, color=0xF0F0F0, size=30)
        graphics.drawText(display, data.translate("language"), data.config.WIDTH * 0.35 - 240, data.config.HEIGHT * 0.85, color=0xF0F0F0, size=30)

        graphics.drawText(display, self.resolutions_strings[self.resolution_index], data.config.WIDTH * 0.58 + 100, data.config.HEIGHT * 0.7, color=0xF0F0F0, size=30, formatting="center")
        graphics.drawText(display, self.languages_strings[self.language_index], data.config.WIDTH * 0.58 + 100, data.config.HEIGHT * 0.85, color=0xF0F0F0, size=30, formatting="center")

    def respondToUserInput(self, event):
        for e in self.configMenu_list.handle(event):
            if e.type == graphics.userInterface.BUTTONCLICKED:
                if e.button == 0:

                    if self.camera:
                        self.camera.x += data.config.WIDTH / 2
                        self.camera.y += data.config.HEIGHT / 2

                    data.config.WIDTH, data.config.HEIGHT = self.resolutions[self.resolution_index]
                    data.config.FULLSCREEN = self.configMenu_list.boxChecked("fullscreen")
                    data.config.LANG = self.languages[self.language_index]

                    if self.camera:
                        self.camera.x -= data.config.WIDTH / 2
                        self.camera.y -= data.config.HEIGHT / 2

                    if data.config.FULLSCREEN:
                        pygame.display.set_mode(self.resolutions[self.resolution_index], pygame.FULLSCREEN)
                    else: pygame.display.set_mode(self.resolutions[self.resolution_index])

                    data.saveConfig()
                    data.loadLanguage()

                    return self.origin(self.camera)

                if e.button == 1:
                    self.resolution_index -= 1
                if e.button == 2:
                    self.resolution_index += 1
                if e.button == 3:
                    self.language_index -= 1
                if e.button == 4:
                    self.language_index += 1

                self.resolution_index = self.resolution_index % len(self.resolutions)
                self.language_index = self.language_index % 2

        data.config.MUSIC = self.configMenu_list.getSliderValue("musicVolume")
        data.config.SOUND = self.configMenu_list.getSliderValue("musicSound")

        if event.type == pygame.MOUSEBUTTONUP:
            if self.lastSound != data.config.SOUND:
                data.playSound("explosion.ogg")
                self.lastSound = data.config.SOUND

        pygame.mixer.music.set_volume(data.config.MUSIC / 100.0)

        return self

    def update(self):
        pass
