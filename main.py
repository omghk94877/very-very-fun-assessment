

import pygame
import sprite

class Main:
    def __init__(self):
        pygame.init()
        # D - Display configuration
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("Hello, world!")
        # E - Entities
        self.entities()
        # A - Action (broken into ALTER steps)
        # A - Assign values to key variables
        self.clock = pygame.time.Clock()
        # L - Loop
        self.loop()
        # Close the game window , set the X
        pygame.quit()

    def entities(self):
        """Set background for game"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 255))

    def loop(self):
        keepGoing = True
        while keepGoing:
            # T - Timer to set the frame rate
            self.clock.tick(30)
            # E - Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                    # R - Refresh the display
                    self.screen.blit(self.background, (0, 0))
                    pygame.display.flip()