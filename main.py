

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
        self.background.fill((225, 225, 225))

        # create a player from sprite module so we can render it
        self.player = sprite.Player()

        # position player in center of screen
        self.player.rect.center = self.screen.get_rect().center

        # group to hold all active sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        # group to hold active blades (used elsewhere in the loop)
        self.blades = pygame.sprite.Group()
        # group to hold active bullets
        self.bullets = pygame.sprite.Group()

    def loop(self):
        keepGoing = True
        while keepGoing:
            # T - Timer to set the frame rate, dt in milliseconds
            dt = self.clock.tick(30)
            # E - Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    # WASD controls: A = left, D = right, W = up/jump, S = back to stand
                    if event.key == pygame.K_a:
                        self.player.move_left()
                    elif event.key == pygame.K_d:
                        self.player.move_right()
                    elif event.key == pygame.K_w:
                        self.player.move_up()
                    elif event.key == pygame.K_s:
                        self.player.init_move()
                    elif event.key == pygame.K_ESCAPE:
                        keepGoing = False
                    elif event.key == pygame.K_e:
                        # create a blade and add to blades group so it gets updated and drawn
                        blade = sprite.Blade(self.player)
                        # keep blades separate so we can update/draw them easily
                        self.blades.add(blade)
                        # also add to all_sprites for completeness (optional)
                        self.all_sprites.add(blade)
                    elif event.key == pygame.K_q:
                        bullet = sprite.Bullet(self.player)
                        # add to bullets group so it's updated/drawn each frame
                        self.bullets.add(bullet)
                        # also add to all_sprites if you want a central list
                        self.all_sprites.add(bullet)
                    
                elif event.type == pygame.KEYUP:
                    # when releasing movement keys, return to standing image
                    if event.key in (pygame.K_a, pygame.K_d, pygame.K_w):
                        self.player.init_move()
            # update blades
            if hasattr(self, 'blades'):
                self.blades.update(dt)

            # update bullets
            if hasattr(self, 'bullets'):
                self.bullets.update(dt)

            # R - Refresh the display
            self.screen.blit(self.background, (0, 0))
            # draw player
            if hasattr(self, 'player') and self.player.image:
                self.screen.blit(self.player.image, self.player.rect)
            # draw blades
            if hasattr(self, 'blades'):
                self.blades.draw(self.screen)

            # draw bullets
            if hasattr(self, 'bullets'):
                self.bullets.draw(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    Main()