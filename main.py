"""
Date:
Name:
Description:

"""
import random
import pygame
import sprite
import surfacekeeper

class Main(surfacekeeper.ScreenManager):
    def __init__(self, app, level=1, game_state=None):
        super().__init__(app)
        self.level = level
        self.game_state = game_state
        self.screen = self.app.screen
        self.clock = self.app.clock
        self.size = self.app.size
        self.won = False
        #E - Entities
        self.entities()
        # Action requested by game loop after exit (used to request VN, restart, etc.)
        self.next_action = None
        #game state flag: when True, freeze most updates (allow death animation)
        self.game_over = False
        # respawn timer (ms). When game_over becomes True this is set and counts down.
        self.respawn_timer = None
        self.respawn_delay = 2000  # ms to wait before respawn
        # Pause state
        self.paused = False
        # Font for UI
        self.font = pygame.font.SysFont(None, 36)
        self.weapon = 'basic'

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

        # Create portal only when appropriate. Skip portal in level 1 while
        # the boss is still active (i.e., level1 not yet completed).
        if self.level != 1 or (self.game_state and getattr(self.game_state, 'level1_completed', False)):
            self.portal = sprite.Portal(self.player, self.background)
            self.all_sprites.add(self.portal)

        #group to hold enemies
        self.enemies = pygame.sprite.Group()
        
        # Spawn regular enemies (increase count on level 2)
        enemy_count = 15 if self.level == 1 else 30
        hard_mode = self.game_state.hard_mode if self.game_state else False
        for i in range(enemy_count):
            enemy = sprite.Enemy(self.player, self.background, hard_mode=hard_mode)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # create boss and add to active sprites (boss is not added to `self.enemies`
        # so regular bullets/blades won't auto-delete it; we handle boss hits separately)
        # boss is added AFTER portal so it renders on top
        if self.level == 1 and not (self.game_state and self.game_state.level1_completed):
            hard_mode = self.game_state.hard_mode if self.game_state else False
            self.boss = sprite.Boss(self.player, self.background, all_sprites=self.all_sprites, hard_mode=hard_mode)
            self.all_sprites.add(self.boss)
        elif self.level == 2:
            # Mini bosses for level 2
            self.mini_boss1 = sprite.Boss(self.player, self.background, all_sprites=self.all_sprites, hard_mode=hard_mode)  # 1/4 health
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
                            blade_exists = any(isinstance(s, (sprite.Blade, sprite.OtherBlade, sprite.ObsidianBlade)) for s in self.all_sprites.sprites())
                            if not blade_exists:
                                if self.weapon == 'basic':
                                    blade = sprite.Blade(self.player)
                                elif self.weapon == 'flame':
                                    blade = sprite.OtherBlade(self.player)
                                elif self.weapon == 'obsidian':
                                    if self.player.obsidian_blade.cooldown <= 0:
                                        if self.player.obsidian_blade.use():
                                            self.all_sprites.add(self.player.obsidian_blade.shield)
                                        # don't add blade if shield activated; continue processing events
                                        continue
                                    else:
                                        blade = sprite.ObsidianBlade(self.player)
                                self.all_sprites.add(blade)
                        elif event.key == pygame.K_q:
                            bullet = sprite.Bullet(self.player)
                            self.all_sprites.add(bullet)
                        elif event.key == pygame.K_SPACE:
                            self.intro.next_line()
                        elif event.key == pygame.K_c:
                            # toggle weapon: basic -> flame -> obsidian (if level1 cleared) -> basic
                            if self.weapon == 'basic':
                                self.weapon = 'flame'
                            elif self.weapon == 'flame':
                                # Allow obsidian if level1 completed OR we're on level 2
                                if (self.game_state and getattr(self.game_state, 'level1_completed', False)) or self.level >= 2:
                                    self.weapon = 'obsidian'
                                else:
                                    self.weapon = 'basic'
                            elif self.weapon == 'obsidian':
                                self.weapon = 'basic'
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
                self.check_shield_collision()
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

            # Draw ability cooldown
            if hasattr(self.player, 'obsidian_blade') and self.player.obsidian_blade.cooldown > 0:
                cooldown_text = "Ability Cooldown"
                cooldown_surf = self.font.render(cooldown_text, True, (255, 0, 0))
                self.screen.blit(cooldown_surf, (10, 40))

            # Draw pause menu
            if self.paused:
                # Semi-transparent overlay
                overlay = pygame.Surface(self.size, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                # Menu text
                resume_text = self.font.render("Resume (R)", True, (255, 255, 255))
                quit_text = self.font.render("Back to Menu (Q)", True, (255, 255, 255))
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
                    # don't auto-kill enemies; they may require multiple hits
                    hit_enemies = pygame.sprite.spritecollide(spr, self.enemies, False)
                    if hit_enemies:
                        for e in hit_enemies:
                            try:
                                dead = e.take_hit()
                            except Exception:
                                # fallback: remove enemy immediately
                                e.kill()
                                dead = True
                        spr.kill()
                    # bullet hitting boss: boss takes one hit (50 required to die)
                    if getattr(self, 'boss', None) is not None and spr.rect.colliderect(self.boss.rect):
                        # count a hit and remove bullet
                        if self.boss.take_hit():
                            # boss died — mark level complete, save, request VN then stop loop
                            if self.game_state:
                                self.game_state.level1_completed = True
                                self.game_state.save()
                            # request visual novel 'boss_defeat' to play after loop
                            self.next_action = ('visual_novel', 'boss_defeat')
                            self.keepGoing = False
                        spr.kill()
     
            #Check collisions between blades and enemies: blades kill enemies on contact
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, (sprite.Blade, sprite.OtherBlade, sprite.ObsidianBlade)):
                    # blades should hit but not necessarily kill immediately
                    hit_enemies = pygame.sprite.spritecollide(blade, self.enemies, False)
                    if hit_enemies:
                        for e in hit_enemies:
                            try:
                                _ = e.take_hit()
                            except Exception:
                                e.kill()
                        # optionally keep blade alive until its timer; do not need to call blade.kill() here
                        pass
                    # blade hitting boss
                    if getattr(self, 'boss', None) is not None and blade.rect.colliderect(self.boss.rect):
                        if self.boss.take_hit():
                            # boss died — mark level complete, save, request VN then stop loop
                            if self.game_state:
                                self.game_state.level1_completed = True
                                self.game_state.save()
                            self.next_action = ('visual_novel', 'boss_defeat')
                            self.keepGoing = False
     
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
                    
            if getattr(self, 'portal', None) and self.player.rect.colliderect(self.portal.rect):
                # Player touched the portal: save state and play portal story then go to main menu.
                if self.game_state:
                    try:
                        self.game_state.save()
                    except Exception:
                        pass
                self.next_action = ('visual_novel', 'portal')
                self.keepGoing = False
                return


            # blade cancels boss projectiles (blade destroys any boss fireball it touches)
            for blade in list(self.all_sprites.sprites()):
                if isinstance(blade, (sprite.Blade, sprite.OtherBlade)):
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
            
            if getattr(self, 'portal', None) and self.player.rect.colliderect(self.portal.rect):
                # Ensure touching portal always plays portal story then goes to main menu during gameplay.
                if self.game_state:
                    try:
                        self.game_state.save()
                    except Exception:
                        pass
                self.next_action = ('visual_novel', 'portal')
                self.keepGoing = False
                return

    def check_shield_collision(self):
        shield = getattr(self.player.obsidian_blade, 'shield', None)
        if shield and shield.alive():
            projectiles = [s for s in self.all_sprites.sprites() if isinstance(s, (sprite.Bullet, sprite.BossBullet, sprite.SmallFireball, sprite.BigFireball, sprite.TracingFireball))]
            for proj in projectiles:
                if pygame.sprite.collide_rect(shield, proj):
                    shield.block_attack()
                    proj.kill()
                    break



if __name__ == "__main__":
    app = surfacekeeper.App(size=(1000, 600))
    app.run()