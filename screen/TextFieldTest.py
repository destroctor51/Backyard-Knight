import pygame
import graphics

class TextFieldTest(object):

    def __init__(self):
        self.tf = graphics.userInterface.TextField("textField.png", 380, 320)

        self.slider = graphics.userInterface.Slider("slider.png", "slidermask.png", (0, 100), 0, 400, 400)

        self.interface = graphics.userInterface.Interface()
        self.interface.addButton(0, "button.png", 50, 50)
        self.interface.addCheckBox("fu", "checkbox.png", 50, 400)
        pass

    def displayOutput(self, display):
        self.interface.draw(display)

        display.blit(self.tf.getIcon(), self.tf.getDrawPos())
        display.blit(self.slider.getIcon(), self.slider.getDrawPos())

        pass

    def respondToUserInput(self, event):
        for e in self.interface.handle(event):

            if e.type == graphics.userInterface.HOVER:
                if e.mode == graphics.userInterface.CLICKHOVER:
                    graphics.userInterface.cursor.setFairy()

                if e.mode == graphics.userInterface.NOHOVER:
                    graphics.userInterface.cursor.setDefault()

            if e.type == graphics.userInterface.BUTTONCLICKED:
                if e.button == 0: self.slider.active = not self.slider.active

        self.tf.updateHover()
        self.slider.updateHover()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.tf.clickDown()
            self.slider.clickDown()
        if event.type == pygame.MOUSEBUTTONUP:
            self.tf.clickUp()
            self.slider.clickUp()

        self.tf.inputText(event)

        return self

    def update(self):
        if self.interface.boxChecked("fu"):
            print self.slider.value
        pass
