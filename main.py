

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
        background_image = pygame.image.load("smt/Images/Battleground1.png")
        background_image = pygame.transform.scale(background_image, (2840, 1080))
        
        # Create background sprite for scrolling effect
        self.background = sprite.Background(background_image, screen_width=1920)

        # create a player from sprite module so we can render it
        self.player = sprite.Player()
        self.intro = sprite.Intro()

        # position player in center of screen
        self.player.rect.center = self.screen.get_rect().center

        # group to hold all active sprites (player, blades, bullets, etc.)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.intro)

        # obstacles live in world coordinates (move with background)
        self.obstacles = pygame.sprite.Group()
        for i in range(5):
            obs = sprite.Obstacle(self.background)
            self.obstacles.add(obs)
            self.all_sprites.add(obs)
        
        # group to hold enemies
        self.enemies = pygame.sprite.Group()
        
        # Spawn initial enemy (pass background reference)
        enemy = sprite.Enemy(self.player, self.background)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
        self.intro.start()
        # currently equipped weapon: 'flame' or 'obsidian'
        self.weapon = 'flame'
        self.player.weapon = self.weapon

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
                    # c = change weapon
                    if event.key == pygame.K_a:
                        self.player.move_left()
                        # Only scroll background if not at left edge, otherwise player moves
                        if not self.background.at_left_edge:
                            self.background.player_move_left()
                        
                    elif event.key == pygame.K_d:
                        self.player.move_right()
                        # Only scroll background if not at right edge, otherwise player moves
                        if not self.background.at_right_edge:
                            self.background.player_move_right()
                    elif event.key == pygame.K_w:
                        self.player.move_up()
                    elif event.key == pygame.K_s:
                        self.player.init_move()
                    elif event.key == pygame.K_ESCAPE:
                        keepGoing = False

                    elif event.key == pygame.K_e:
                        # use currently equipped blade
                        if getattr(self, 'weapon', 'flame') == 'obsidian':
                            blade = sprite.Other_blade(self.player)
                        else:
                            blade = sprite.Blade(self.player)
                        self.all_sprites.add(blade)

                    elif event.key == pygame.K_q:
                        bullet = sprite.Bullet(self.player)
                        self.all_sprites.add(bullet)
                    elif event.key == pygame.K_SPACE:
                        self.intro.next_line()

                    elif event.key == pygame.K_c:
                        # toggle equipped weapon between flame and obsidian
                        if getattr(self, 'weapon', 'flame') == 'flame':
                            self.weapon = 'obsidian'
                        else:
                            self.weapon = 'flame'
                        self.player.weapon = self.weapon
                        
                    
                elif event.type == pygame.KEYUP:
                    # when releasing movement keys, return to standing image
                    if event.key in (pygame.K_a, pygame.K_d, pygame.K_w):
                        self.player.init_move()
                        self.background.stop()

            # update all sprites once (player, blades, bullets)
            self.all_sprites.update(dt)
            # update background scrolling
            self.background.update()
            
            # Check collisions between bullets and enemies
            for bullet in list(self.all_sprites.sprites()):
                if isinstance(bullet, sprite.Bullet):
                    hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, True)
                    if hit_enemies:
                        bullet.kill()
            
            # Check collisions between blades and enemies
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, sprite.Blade) or isinstance(blade, sprite.Other_blade):
                    hit_enemies = pygame.sprite.spritecollide(blade, self.enemies, True)
                    if hit_enemies:
                        pass

            # R - Refresh the display
            self.screen.blit(self.background.image, self.background.rect)

            # draw all sprites (order is insertion order)
            self.all_sprites.draw(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    Main()