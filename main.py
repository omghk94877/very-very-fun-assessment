import random
import pygame
import sprite

class Main:
    def __init__(self, size= (1000,600)):
        pygame.init()
        #D - Display configuration
        self.size = size
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Hello, world!")
        #E - Entities
        self.entities()
        #A - Action (broken into ALTER steps)
        #A - Assign values to key variables
        self.clock = pygame.time.Clock()
        #game state flag: when True, freeze most updates (allow death animation)
        self.game_over = False
        # respawn timer (ms). When game_over becomes True this is set and counts down.
        self.respawn_timer = None
        self.respawn_delay = 2000  # ms to wait before respawn
        #L - Loop
        self.loop()
        #Close the game window , set the X
        pygame.quit()

    def entities(self):
        # play a random background music file (if available)
        bgm_files = [
            "smt/Sounds/8bitsong.wav",
            "smt/Sounds/music1.mp3",
            "smt/Sounds/music2.mp3",
            "smt/Sounds/music3.mp3"
        ]
        try:
            # ensure mixer is initialized (pygame.init usually does this, but be safe)
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.bgm = random.choice(bgm_files)
            pygame.mixer.music.load(self.bgm)
            pygame.mixer.music.play(-1)
        except Exception:
            # audio failure shouldn't stop the game; continue silently
            pass

        background_image = pygame.image.load("smt/Images/Battleground1.png")
        background_image = pygame.transform.scale(background_image, (10000, 600))
        
        #Create background sprite for scrolling effect
        self.background = sprite.Background(background_image, screen_width=1920)

        #create a player from sprite module so we can render it
        self.player = sprite.Player()
        self.intro = sprite.Intro()

        #position player in center of screen
        self.player.rect.center = self.screen.get_rect().center
        #set ground level so player lands at the same vertical position after a jump
        self.player.ground_y = self.player.rect.bottom

        #group to hold all active sprites (player, blades, bullets, etc.)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.background)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.intro)

        #obstacles live in world coordinates (move with background)
        self.obstacles = pygame.sprite.Group()
        for i in range(8):
            rock = sprite.Rock(self.background, player=self.player)
            self.obstacles.add(rock)
            self.all_sprites.add(rock)


        #group to hold enemies
        self.enemies = pygame.sprite.Group()
        
        # Spawn regular enemies (keep other enemies behavior unchanged)
        for i in range(9):
            enemy = sprite.Enemy(self.player, self.background, all_sprites=self.all_sprites)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Spawn a single boss placed near the end of the map
        boss = sprite.Enemy(self.player, self.background, force_type=2, all_sprites=self.all_sprites)
        self.enemies.add(boss)
        self.all_sprites.add(boss)

        for i in range(5):
            spikes = sprite.Spike(self.background, player=self.player)
            self.obstacles.add(spikes)
            self.all_sprites.add(spikes)

        # don't add the Group object itself into all_sprites (we already added each enemy)
        # self.all_sprites.add(self.enemies)

        self.intro.start()
        #currently equipped weapon: 'flame' or 'obsidian'
        self.weapon = 'flame'
        self.player.weapon = self.weapon

    def loop(self):
        self.keepGoing = True
        while self.keepGoing:
            #T - Timer to set the frame rate, dt in milliseconds
            dt = self.clock.tick(30)    
            #E - Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keepGoing = False
                elif event.type == pygame.KEYDOWN:
                    #Escape always quits; other controls disabled after death
                    if event.key == pygame.K_ESCAPE:
                        self.keepGoing = False
                    elif not self.game_over:
                        #WASD controls: A/D/W movement, S stop/init_move
                        if event.key == pygame.K_a:
                            self.player.move_left()
                            #Only scroll background if not at left edge and player is on the ground
                            if not self.background.at_left_edge and getattr(self.player, 'on_ground', True):
                                self.background.player_move_left()
                        elif event.key == pygame.K_d:
                            self.player.move_right()
                            #Only scroll background if not at right edge and player is on the ground
                            if not self.background.at_right_edge and getattr(self.player, 'on_ground', True):
                                self.background.player_move_right()
                        elif event.key == pygame.K_w:
                            self.player.move_up()
                            self.background.stop()
                        elif event.key == pygame.K_s:
                            self.player.init_move()

                        #combat / UI keys
                        elif event.key == pygame.K_e:
                            blade_exists = any(isinstance(s, (sprite.Blade, sprite.Other_blade)) for s in self.all_sprites.sprites())
                            if not blade_exists:
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
                            #toggle equipped weapon between flame and obsidian
                            if getattr(self, 'weapon', 'flame') == 'flame':
                                self.weapon = 'obsidian'
                            else:
                                self.weapon = 'flame'
                            self.player.weapon = self.weapon
                elif event.type == pygame.KEYUP and not self.game_over:
                    #when releasing movement keys, return to standing image
                    if event.key in (pygame.K_a, pygame.K_d, pygame.K_w):
                        self.player.init_move()
                        self.background.stop()
            self.handle_input(dt)

    def handle_input(self, dt):
            #continuous input handling (handles holding keys, including in-air horizontal control)
            keys = pygame.key.get_pressed()
            if not self.game_over and keys[pygame.K_a]:
                #always allow the player to attempt a left move (move_left handles on_ground behavior)
                self.player.move_left()
                #scroll background (background moves, player stays put)
                if not self.background.at_left_edge:
                    self.background.player_move_left()
            elif not self.game_over and keys[pygame.K_d]:
                self.player.move_right()
                if not self.background.at_right_edge:
                    self.background.player_move_right()
            else:
                #no horizontal key held; stop background scroll when on ground
                #stop background scrolling
                self.background.stop()

            #update sprites depending on game state
            if not self.game_over:
                #normal gameplay: update everything and check collisions
                self.all_sprites.update(dt)
                #update background scrolling
                #self.background.update()
                self.check_collision()
            else:
                #freeze everything except allow the player's death animation to advance
                #stop background so world does not move
                self.background.stop()
                #advance only the player animation so death anim can play
                self.player.update(dt)
                #keep background rect stable
                self.background.update(0)
                # start respawn timer if not already started
                if self.respawn_timer is None:
                    self.respawn_timer = self.respawn_delay
                else:
                    self.respawn_timer -= dt
                    if self.respawn_timer <= 0:
                        # respawn: recreate entities (will rebuild enemies/obstacles/player)
                        # keep window/clock intact
                        self.entities()
                        self.game_over = False
                        self.respawn_timer = None
                #still draw below
            #R - Refresh the display (draw current sprite states)
            #draw all sprites (order is insertion order)
            self.all_sprites.draw(self.screen)

            pygame.display.flip()
            

    def check_collision(self):
            #collision handling only (drawing done by caller)
            for i in self.obstacles:
                if i.rect.colliderect(self.player.rect):
                    #trigger death and freeze game
                    self.player.death()
                    self.game_over = True
                    #self.keepGoing = False
                    

            #Check collisions between bullets and enemies (apply damage)
            for bullet in list(self.all_sprites.sprites()):
                if isinstance(bullet, sprite.Bullet) or isinstance(bullet, sprite.BossBullet):
                    hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                    if hit_enemies:
                        for e in hit_enemies:
                            e.take_damage(getattr(bullet, 'damage', 0))
                        bullet.kill()

            #Check collisions between blades and enemies (apply damage)
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, sprite.Blade) or isinstance(blade, sprite.Other_blade):
                    hit_enemies = pygame.sprite.spritecollide(blade, self.enemies, False)
                    if hit_enemies:
                        for e in hit_enemies:
                            e.take_damage(getattr(blade, 'damage', 0))

            #check for enemy and player
            for i in self.enemies:
                if i.rect.colliderect(self.player.rect):
                    self.player.death()
                    self.game_over = True


if __name__ == "__main__":
    Main()