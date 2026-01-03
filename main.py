

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
        self.story = sprite.Story()

        # position player in center of screen
        self.player.rect.center = self.screen.get_rect().center

        # group to hold all active sprites (player, blades, bullets, etc.)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.story)
        self.story.start()

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
                    # WASD controls: 
                    # A = left, 
                    # D = right, 
                    # W = up/jump, 
                    # S has no effect currently
                    # Escape to quit
                    # E = blade attack
                    # Q = shooting bullet
                    # Space to read text
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
                        # create a blade and add to the central all_sprites group
                        blade = sprite.Blade(self.player)
                        self.all_sprites.add(blade)
                    elif event.key == pygame.K_q:
                        bullet = sprite.Bullet(self.player)
                        self.all_sprites.add(bullet)
                    elif event.key == pygame.K_SPACE:
                        self.story.next_line()
                    
                elif event.type == pygame.KEYUP:
                    # when releasing movement keys, return to standing image
                    if event.key in (pygame.K_a, pygame.K_d, pygame.K_w):
                        self.player.init_move()

            # update all sprites once (player, blades, bullets)
            self.all_sprites.update(dt)

            # R - Refresh the display
            self.screen.blit(self.background, (0, 0))

            # draw all sprites (order is insertion order)
            self.all_sprites.draw(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    Main()