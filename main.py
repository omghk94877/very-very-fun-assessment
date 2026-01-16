import random
import pygame
import sprite
import surfacekeeper

class Main:
    def __init__(self, size=(1000,600), screen=None, level=1, game_state=None, app=None):
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode(size)
            pygame.display.set_caption("Monster Smash - Game")
            self.owns_display = True
        else:
            self.screen = screen
            self.owns_display = False
        
        #D - Display configuration
        self.size = size
        self.level = level
        self.game_state = game_state
        self.app = app
        self.won = False
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
        # Pause state
        self.paused = False
        # Font for UI
        self.font = pygame.font.SysFont(None, 36)
        #L - Loop
        self.loop()
        #Close the game window if we own it
        if self.owns_display:
            pygame.quit()

    def entities(self):
        # play a random background music file (if available)
        bgm_files = [
            "src/Sounds/8bitsong.wav",
            "src/Sounds/music1.mp3",
            "src/Sounds/music2.mp3",
            "src/Sounds/music3.mp3"
        ]
       
        pygame.mixer.init()
        self.bgm = random.choice(bgm_files)
        self.music = pygame.mixer.music.load(self.bgm)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        
        

        
        

        background_image = pygame.image.load("src/Images/map/Battleground1.png")
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
        portal_x = 8530  # Portal position
        safe_portal_distance = 300  # No obstacles within this distance of portal
        for i in range(16):
            rock = sprite.Rock(self.background, player=self.player)
            # Ensure rock is not near portal
            while abs(rock.world_x - portal_x) < safe_portal_distance:
                rock = sprite.Rock(self.background, player=self.player)
            self.obstacles.add(rock)
            self.all_sprites.add(rock)

        self.portal = sprite.Portal(self.player, self.background)
        self.all_sprites.add(self.portal)

        #group to hold enemies
        self.enemies = pygame.sprite.Group()
        
        # Spawn regular enemies (keep other enemies behavior unchanged)
        for i in range(15):
            enemy = sprite.Enemy(self.player, self.background)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # create boss and add to active sprites (boss is not added to `self.enemies`
        # so regular bullets/blades won't auto-delete it; we handle boss hits separately)
        # boss is added AFTER portal so it renders on top
        if self.level == 1:
            self.boss = sprite.Boss(self.player, self.background, all_sprites=self.all_sprites, required_hits=50)
            self.all_sprites.add(self.boss)
        elif self.level == 2:
            # Mini bosses for level 2
            self.mini_boss1 = sprite.Boss(self.player, self.background, all_sprites=self.all_sprites, required_hits=12)  # 1/4 health
            self.mini_boss1.rect.centerx = self.background.world_width // 4
            self.all_sprites.add(self.mini_boss1)
            self.mini_boss2 = sprite.Boss(self.player, self.background, all_sprites=self.all_sprites, required_hits=25)  # Giant bat placeholder
            self.mini_boss2.rect.centerx = 3 * self.background.world_width // 4
            self.all_sprites.add(self.mini_boss2)

        for i in range(5):
            spikes = sprite.Spike(self.background, player=self.player)
            # Ensure spikes are not near portal
            while abs(spikes.world_x - portal_x) < safe_portal_distance:
                spikes = sprite.Spike(self.background, player=self.player)
            self.obstacles.add(spikes)
            self.all_sprites.add(spikes)

        # don't add the Group object itself into all_sprites (we already added each enemy)
        # self.all_sprites.add(self.enemies)

        self.intro.start()
        #currently equipped weapon: 'flame' or '
        # dian'
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
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif self.paused:
                        if event.key == pygame.K_r:
                            self.paused = False
                        elif event.key == pygame.K_q:
                            if self.game_state:
                                self.game_state.save()
                            self.keepGoing = False
                    elif not self.game_over and not self.paused:
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
                            blade_exists = any(isinstance(s, (sprite.BladeBasic, sprite.BladeFire, sprite.BladeObsidian)) for s in self.all_sprites.sprites())
                            if not blade_exists:
                                if getattr(self, 'weapon', 'flame') == 'obsidian':
                                    blade = sprite.BladeObsidian(self.player)
                                elif getattr(self, 'weapon', 'flame') == 'flame':
                                    blade = sprite.BladeFire(self.player)
                                else: 
                                    blade = sprite.BladeBasic(self.player)
                                self.all_sprites.add(blade)
                        elif event.key == pygame.K_q:
                            bullet = sprite.Bullet(self.player)
                            self.all_sprites.add(bullet)
                        elif event.key == pygame.K_SPACE:
                            self.intro.next_line()
                        elif event.key == pygame.K_c:
                            #toggle equipped weapon between flame and obsidian if unlocked
                            if self.game_state.obsidian_unlocked:
                                if getattr(self, 'weapon', 'flame') == 'flame':
                                    self.weapon = 'obsidian'
                                else:
                                    self.weapon = 'flame'
                                self.player.weapon = self.weapon
                elif event.type == pygame.KEYUP and not self.game_over and not self.paused:
                    #when releasing movement keys, return to standing image
                    if event.key in (pygame.K_a, pygame.K_d, pygame.K_w):
                        self.player.init_move()
                        self.background.stop()
            self.handle_input(dt)

    def handle_input(self, dt):
            #continuous input handling (handles holding keys, including in-air horizontal control)
            keys = pygame.key.get_pressed()
            if not self.game_over and not self.paused and keys[pygame.K_a]:
                #always allow the player to attempt a left move (move_left handles on_ground behavior)
                self.player.move_left()
                #scroll background (background moves, player stays put)
                if not self.background.at_left_edge:
                    self.background.player_move_left()
            elif not self.game_over and not self.paused and keys[pygame.K_d]:
                self.player.move_right()
                if not self.background.at_right_edge:
                    self.background.player_move_right()
            else:
                #no horizontal key held; stop background scroll when on ground
                #stop background scrolling
                self.background.stop()

            #update sprites depending on game state
            if not self.game_over and not self.paused:
                #normal gameplay: update everything and check collisions
                self.all_sprites.update(dt)
                self.check_collision()
            elif self.game_over:
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
            else:  # paused
                # freeze everything, just stop background
                self.background.stop()
                self.background.update(0)
            #R - Refresh the display (draw current sprite states)
            #draw all sprites (order is insertion order)
            self.all_sprites.draw(self.screen)

            # Draw death count
            if self.game_state:
                # skull image
                skull_text = "X " + str(self.game_state.death_count)
                death_surf = self.font.render(skull_text, True, (255, 255, 255))
                self.screen.blit(death_surf, (10, 10))

            # Draw pause menu
            if self.paused:
                # Semi-transparent overlay
                overlay = pygame.Surface(self.size, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                # Menu text
                resume_text = self.font.render("Resume (R)", True, (255, 255, 255))
                quit_text = self.font.render("Quit (Q)", True, (255, 255, 255))
                menu_title = self.font.render("Paused", True, (255, 255, 255))
                self.screen.blit(menu_title, (self.size[0]//2 - menu_title.get_width()//2, self.size[1]//2 - 100))
                self.screen.blit(resume_text, (self.size[0]//2 - resume_text.get_width()//2, self.size[1]//2 - 20))
                self.screen.blit(quit_text, (self.size[0]//2 - quit_text.get_width()//2, self.size[1]//2 + 20))

            pygame.display.flip()
            

    def check_collision(self):
            #collision handling only (drawing done by caller)
            for i in self.obstacles:
                if i.rect.colliderect(self.player.rect):
                    #trigger death and freeze game
                    self.player.death()
                    if self.game_state:
                        self.game_state.increment_death_count()
                        self.game_state.save()
                    self.game_over = True
                    #self.keepGoing = False
            
            #Check collisions between bullets and enemies: bullets kill enemies on contact
            for spr in list(self.all_sprites.sprites()):
                if isinstance(spr, (sprite.Bullet, sprite.BossBullet)):
                    hit_enemies = pygame.sprite.spritecollide(spr, self.enemies, True)
                    if hit_enemies:
                        spr.kill()
                        # Unlock obsidian after first enemy kill
                        if not self.game_state.obsidian_unlocked:
                            self.game_state.obsidian_unlocked = True
                            self.game_state.save()
                    # bullet hitting boss: boss takes one hit (50 required to die)
                    if getattr(self, 'boss', None) is not None and spr.rect.colliderect(self.boss.rect):
                        # count a hit and remove bullet
                        self.boss.take_hit()
                        spr.kill()
     
            #Check collisions between blades and enemies: blades kill enemies on contact
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, (sprite.BladeBasic, sprite.BladeFire, sprite.BladeObsidian)):
                    hit_enemies = pygame.sprite.spritecollide(blade, self.enemies, True)
                    if hit_enemies:
                        # Unlock obsidian after first enemy kill
                        if not self.game_state.obsidian_unlocked:
                            self.game_state.obsidian_unlocked = True
                            self.game_state.save()
                        # optionally keep blade alive until its timer; do not need to call blade.kill() here
                        pass
                    # blade hitting boss
                    if getattr(self, 'boss', None) is not None and blade.rect.colliderect(self.boss.rect):
                        self.boss.take_hit()
     
            # projectiles from boss kill player on contact
            for spr in list(self.all_sprites.sprites()):
                if isinstance(spr, (sprite.BigFireball, sprite.SmallFireball, sprite.TracingFireball, sprite.BossBullet)):
                    if spr.rect.colliderect(self.player.rect):
                        # player dies immediately on projectile hit
                        self.player.death()
                        if self.game_state:
                            self.game_state.increment_death_count()
                            self.game_state.save()
                        self.game_over = True
                        return
                    
            if self.player.rect.colliderect(self.portal.rect):
                if self.level == 1:
                    if not self.game_state.level1_completed:
                        self.game_state.level1_completed = True
                        self.game_state.save()
                        import surfacekeeper
                        self.app.change_screen(surfacekeeper.VisualNovel(self.app, "level1_end"))
                    else:
                        import surfacekeeper
                        self.app.change_screen(surfacekeeper.VisualNovel(self.app, "portal"))
                elif self.level == 2:
                    self.won = True
                    self.game_state.save()
                    self.game_over = True
                    self.keepGoing = False


            # blade cancels boss projectiles (blade destroys any boss fireball it touches)
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, (sprite.BladeBasic, sprite.BladeFire, sprite.BladeObsidian)):
                    for proj in list(self.all_sprites.sprites()):
                        if isinstance(proj, (sprite.BigFireball, sprite.SmallFireball, sprite.TracingFireball, sprite.BossBullet)):
                            if blade.rect.colliderect(proj.rect):
                                proj.kill()
                                
            #check for enemy and player
            for i in self.enemies:
                if i.rect.colliderect(self.player.rect):
                    self.player.death()
                    if self.game_state:
                        self.game_state.increment_death_count()
                        self.game_state.save()
                    self.game_over = True



if __name__ == "__main__":
    app = surfacekeeper.App(size=(1000, 600))
    app.run()