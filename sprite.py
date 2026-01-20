import pygame
import random
"""
This module defines the sprite classes for the game, including Player, Background, Enemy, Boss, and various projectile types.
It handles player animations, enemy behaviors, projectile mechanics, and background movement.

"""

class Player(pygame.sprite.Sprite):
    """
    Player is not really moving, instead it's the backgound moving. 
    player only moves when the background reach the edge
    """

    def __init__(self):
        """
        Initializes the player sprite with animations, sounds, and physics properties.
        
        """
        pygame.sprite.Sprite.__init__(self)
        #setting sound effect for player
        self.die_sound = pygame.mixer.Sound("src/Sounds/die.wav")
        self.jump_sound = pygame.mixer.Sound("src/Sounds/jump.wav")
        self.jump_sound.set_volume(0.3)

        #images of different actions
        # Use simple Surfaces so code can run without external image files
        # load animation frames (some are lists of frames)
        self.stand = [pygame.image.load("src/Images/player_animation/frame_03_delay-0.08s.gif")]

        self.move_l = [
            pygame.image.load("src/Images/player_animation/frame_40_delay-0.08s.gif"),
            pygame.image.load("src/Images/player_animation/frame_41_delay-0.08s.gif"),
        ]

        self.move_r = [
            pygame.image.load("src/Images/player_animation/frame_14_delay-0.08s.gif"),
            pygame.image.load("src/Images/player_animation/frame_15_delay-0.08s.gif"),
        ]

        # single-frame surfaces for jump/attack/die (wrap as lists for uniform handling)
        jump_surf = pygame.image.load("src/Images/player_animation/frame_jump_delay-0.08s.gif")
        
        attack_surf = pygame.Surface((60, 40))
        attack_surf.fill((255, 128, 0))
        self.die = [pygame.image.load("src/Images/player_animation/death1.gif"),
                    pygame.image.load("src/Images/player_animation/death2.gif"),
                    pygame.image.load("src/Images/player_animation/death3.gif"),
            ]

        self.jump = [jump_surf]
        self.attack_img = [attack_surf]

        # scale all loaded frames to the player's size (60x100)
        def _scale_list(frames, size=(60, 100)):
            return [pygame.transform.scale(f, size) for f in frames]

        # scale all animations
        self.stand = _scale_list(self.stand)
        self.move_l = _scale_list(self.move_l)
        self.move_r = _scale_list(self.move_r)
        self.jump = _scale_list(self.jump)
        # attack uses a slightly different size
        self.attack_img = _scale_list(self.attack_img, (60, 40))
        self.die = _scale_list(self.die)

        # animation mapping and runtime state
        self.animations = {
            'stand': self.stand,
            'move_l': self.move_l,
            'move_r': self.move_r,
            'jump': self.jump,
            'attack': self.attack_img,
            'die': self.die,
        }

        # initial animation state
        self.current_anim = 'stand'
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 120  # ms per frame

        # starting image is the first frame of the standing animation
        self.image = self.animations[self.current_anim][self.frame_index]

        # facing: used by Blade to determine spawn direction
        self.facing = 'right'

        #setting rect for collision
        self.rect = self.image.get_rect()

        #displacement
        self.dx = 0
        self.dy = 0
        # vertical physics
        self.vy = 0.0  # vertical speed in pixels/ms
        self.gravity = 0.0015  # pixels per ms^2
        self.on_ground = True
        # ground y coordinate (pixels) - should be set by caller after positioning player
        self.ground_y = None

        self.obsidian_blade = ObsidianAbility(self)

    def move_left(self):
        """
        Moves the player to the left.
        change the animation to left-walk
        """
        # switch to left-walk animation
        self.set_animation('move_l')
        self.facing = 'left'
        # no direct horizontal movement of the player; background scrolls instead

    def move_right(self):
        """
        moves the player to the right.
        change the animation to right-walk
        """
        # switch to right-walk animation
        self.set_animation('move_r')
        self.facing = 'right'
        # no direct horizontal movement of the player; background scrolls instead

    def move_up(self):
        """
        Jumps the player upward.
        play the sound effect
        """
        # jump only when on ground
        if not self.on_ground:
            return
        # switch to jump animation
        self.jump_sound.play()

        self.set_animation('jump')
        # initiate jump: negative vy moves up
        self.vy = -0.8
        self.on_ground = False
        # record background start position so we can restore it on landing
        if hasattr(self, 'background') and self.background is not None:
            self._bg_start_y = self.background.rect.y
        

    def death(self):
        """
        Player the death animation and sound.
        """
        self.die_sound.play()
        self.set_animation('die')
        # don't kill the sprite here; animation/state can handle further logic
        

    def attack(self):
        #generate blade
        self.set_animation('attack')
        Blade(owner=self)

    def init_move(self):
        """
        Change the animation back to standing when stop pressing keys
        """
        self.set_animation('stand')

    def set_animation(self, name):
        """Switch to a named animation (list of frames). Resets frame index/timer and preserves sprite center."""
        if name == self.current_anim:
            return
        if name not in self.animations:
            return
        center = self.rect.center
        self.current_anim = name
        self.frame_index = 0
        self.frame_timer = 0
        self.image = self.animations[self.current_anim][self.frame_index]
        # preserve on-screen center
        self.rect = self.image.get_rect(center=center)
        

    def update(self, dt=0):
        """
        Update the player sprite.
        dt: time delta in milliseconds since last update
        """
        # advance animation frames
        if dt:
            self.frame_timer += dt
            frames = self.animations.get(self.current_anim, [])
            if frames:
                if self.frame_timer >= self.frame_duration:
                    # advance by however many frame durations have passed
                    advance = self.frame_timer // self.frame_duration
                    self.frame_timer = self.frame_timer % self.frame_duration
                    self.frame_index = (self.frame_index + advance) % len(frames)
                    # preserve center when swapping image
                    center = self.rect.center
                    self.image = frames[self.frame_index]
                    self.rect = self.image.get_rect(center=center)

        # accept optional dt (milliseconds) so this sprite can be updated by a group with a dt arg
        if dt and not self.on_ground:
            # integrate gravity
            self.vy += self.gravity * dt
            # vertical displacement this frame
            dy = int(self.vy * dt)

            # move the background opposite to player vertical motion so the player appears to move
            if hasattr(self, 'background') and self.background is not None:
                self.background.rect.y -= dy

                # landing detection: only consider landed when we're descending (vy >= 0)
                # and the background has returned to (or passed) its start y
                if hasattr(self, '_bg_start_y') and self.vy >= 0 and self.background.rect.y <= self._bg_start_y:
                    self.background.rect.y = self._bg_start_y
                    self.vy = 0.0
                    self.on_ground = True
                    # optionally reset to standing animation
                    # self.init_move()
            else:
                # fallback: move player rect if no background reference
                self.rect.y += dy
                if self.ground_y is not None and self.rect.bottom >= self.ground_y:
                    self.rect.bottom = self.ground_y
                    self.vy = 0.0
                    self.on_ground = True
                    # self.init_move()

        self.obsidian_blade.update(dt)

    def take_hit(self):
        """Register a hit on this enemy. Return True if enemy died."""
        try:
            self.hits += 1
            if self.hits >= getattr(self, 'required_hits', 1):
                self.kill()
                return True
            return False
        except Exception:
            # fallback: kill immediately
            self.kill()
            return True

class Background(pygame.sprite.Sprite):
    """Represents the scrolling background in the game. The background moves left/right in response to player movement,
    and enforces boundaries to prevent scrolling beyond the level limits.
    """
    def __init__(self, image, screen_width=1920):
        """
        This method initializes the Background sprite with the given image and screen width.
        image: pygame.Surface representing the background image
        screen_width: width of the game screen in pixels
        """
        super().__init__()

        #background, get from the parameter from main
        self.image = image
        self.rect = self.image.get_rect()
        
        #speed
        self.dx = 0
        self.dy = 0
        
        # Screen and boundary info
        self.screen_width = screen_width
        self.image_width = image.get_width()
        # Left boundary is 0, right boundary is when image right edge meets screen right edge
        self.min_x = -(self.image_width - self.screen_width)  # negative value
        self.max_x = 0
        
        # Track if at boundary
        self.at_left_edge = False
        self.at_right_edge = False


    def player_move_left(self):
        """
        if player move left, background move right
        """
        self.dx = 20

    def player_move_right(self):
        """
        if player move right, background move left
        """  
        self.dx = -20

    def stop(self):
        self.dx = 0

    def update(self, dt=0):
        # Apply movement
        self.rect.x += self.dx
        
        # Enforce boundaries
        if self.rect.x > self.max_x:
            self.rect.x = self.max_x
            self.at_right_edge = True
        else:
            self.at_right_edge = False
            
        if self.rect.x < self.min_x:
            self.rect.x = self.min_x
            self.at_left_edge = True
        else:
            self.at_left_edge = False
        
        self.rect.y += self.dy


class Enemy(pygame.sprite.Sprite):
    """
    This class represents a basic enemy that spawns in the game world.
    Enemies can chase the player when within a certain radius and require a set number of hits to be defeated.
    """
    def __init__(self, player, background, screen_width=1920, hard_mode=False):
        super().__init__()
        self.player = player
        self.background = background
        self.screen_width = screen_width

        # Load and setup enemy image (no boss frames)
        self.frames_root = [
            pygame.image.load("src/Images/enemy/root/Root_monster_frame0.gif").convert_alpha(),
            pygame.image.load("src/Images/enemy/root/Root_monster_frame1.gif").convert_alpha(),
        ]
        self.frames_bat = [
            pygame.image.load("src/Images/enemy/bat/monster_bat1.gif").convert_alpha(),
            pygame.image.load("src/Images/enemy/bat/monster_bat2.gif").convert_alpha(),
        ]

        self.frames_tree = [
            pygame.image.load("src/Images/enemy/tree/monster_tree1.gif").convert_alpha(),
            pygame.image.load("src/Images/enemy/tree/monster_tree2.gif").convert_alpha(),

        ]
        

        # Only regular enemy types (0=root, 1=bat, 2=tree)
        self.enemy_type = random.randint(0, 2)

        if self.enemy_type == 0:
            self.frames = self.frames_root
            self.size = (60, 60)
        elif self.enemy_type == 1:
            self.frames = self.frames_bat
            self.size = (30, 30)
        elif self.enemy_type == 2:
            self.frames = self.frames_tree
            self.size = (80, 80)

        # Hit points: set based on difficulty mode
        self.required_hits = 2 if hard_mode else 1
        self.hits = 0
        self.hit_cooldown = 0  # ms cooldown between hits


        # frame timing
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 500

        self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)

        # World spawn range
        enemy_w = self.image.get_width()
        bg_w = max(1, self.background.image.get_width())
        max_x = max(0, bg_w - enemy_w)

        # compute player's world x (screen x - background offset)
        try:
            player_world_x = self.player.rect.x - self.background.rect.x
        except Exception:
            player_world_x = 0

        safe_distance = 200  # pixels; avoid spawning too close to player
        
        # Only spawn to the right of the player
        min_x = player_world_x + safe_distance
        
        # choose random spawn to the right of player
        if max_x > min_x:
            self.world_x = random.randint(min_x, max_x)
        else:
            # fallback if spawn range is invalid
            self.world_x = player_world_x + safe_distance

        # Ensure final on-screen x is to the right of the player's right edge by safe_distance
        try:
            player_screen_right = self.player.rect.right
            min_screen_x = player_screen_right + safe_distance
            min_world_x = min_screen_x - self.background.rect.x
            if self.world_x + self.background.rect.x < min_screen_x:
                # clamp into view to the right of player
                self.world_x = max(min_world_x, 0)
            if self.world_x > max_x:
                self.world_x = max_x
        except Exception:
            pass

        # vertical position relative to player
        self.world_y = self.player.rect.centery - (self.image.get_height() // 2)

        # Set initial screen position
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))
        # movement parameters (pixels per ms)
        self.speed = 0.03
        self.chase_radius = 500



    def update(self, dt=0):
        self.frame_timer += dt
        self.hit_cooldown = max(0, self.hit_cooldown - dt)

        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.frame_index = 0

            self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            
        try:
            # Regular enemies can chase
            if self.enemy_type != 2:
                player_world_x = self.player.rect.x - self.background.rect.x
                player_world_y = self.player.rect.y - self.background.rect.y
                dx = player_world_x - self.world_x
                dy = player_world_y - self.world_y
                if abs(dx) <= self.chase_radius and abs(dx) > 2:
                    direction = 5 if dx > 0 else -5
                    self.world_x += direction * self.speed * dt
                    # Only bats (type 1) can move vertically; roots (type 0) stay grounded
                    if self.enemy_type == 1 and abs(dy) <= self.chase_radius and abs(dy) > 2:
                        direction = 5 if dy > 0 else -5
                        self.world_y += direction * self.speed * dt
        except Exception:
            pass

       
        # update onscreen rect from world coords (existing)
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = self.world_y


    def take_hit(self):
        """Register a hit on this enemy. Return True if enemy died."""
        if self.hit_cooldown > 0:
            return False
        self.hit_cooldown = 500  # 500ms cooldown between hits
        self.hits += 1
        if self.hits >= self.required_hits:
            self.kill()
            return True
        return False


class Boss(pygame.sprite.Sprite):
    """Stationary boss that sits near the end of the world and spits varied fireballs.
    Optional `all_sprites` group can be provided so the boss will add projectiles there.
    Boss must be hit `required_hits` times by blade/bullet to die (not instant).
    """
    def __init__(self, player, background, screen_width=1920, all_sprites=None, hard_mode=False):
        super().__init__()
        self.player = player
        self.background = background
        self.screen_width = screen_width
        self.all_sprites = all_sprites

        # load boss frames (safe loads; if missing, create placeholder)
        try:
            self.frames = [
                pygame.image.load("src/Images/enemy/corc_boss/enemy_boss.gif").convert_alpha(),
                pygame.image.load("src/Images/enemy/corc_boss/enemy_boss2.gif").convert_alpha(),
            ]
        except Exception:
            # fallback: two colored surfaces
            f1 = pygame.Surface((200, 600), pygame.SRCALPHA); f1.fill((150, 30, 30))
            f2 = pygame.Surface((200, 600), pygame.SRCALPHA); f2.fill((180, 60, 60))
            self.frames = [f1, f2]

        # boss is larger
        self.size = (500, 220)
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 400
        self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)

        # world spawn: near the end but visible on screen
        enemy_w = self.image.get_width()
        bg_w = max(1, self.background.image.get_width())
        max_x = max(0, bg_w - enemy_w)
        # prefer near end but not off-screen: end_margin and visible clamp
        end_margin = 300
        # ensure visible on initial screen (background.rect.x likely 0)
        self.world_x = 8000
        # fallback if negative
        if self.world_x < 0:
            self.world_x = max(0, max_x - end_margin)

        # vertical position centered on player
        self.world_y = self.player.rect.centery - (self.image.get_height() // 2)

        # onscreen rect (include background vertical offset for consistent screen coords)
        self.rect = self.image.get_rect(topleft=(int(self.world_x + self.background.rect.x), int(self.world_y + getattr(self.background.rect, 'y', 0))))

        # boss stationary (no world_x change)
        self.speed = 0.0

        # hit requirement
        self.required_hits = 50 if hard_mode else 20
        self.hits = 0
        self.hit_cooldown = 0  # ms cooldown between hits


        # firing timers
        self.fire_timer = 0
        self.fire_cooldown = random.randint(900, 2000)  # ms
        # allowed projectile classes
        self._proj_choices = ('big', 'small', 'trace')

    def take_hit(self):
        """Called when bullet or blade hits the boss. Return True if boss died."""
        if self.hit_cooldown > 0:
            return False
        self.hit_cooldown = 500  # 500ms cooldown between hits
        self.hits += 1
        if self.hits >= self.required_hits:
            self.kill()
            return True
        return False

    def _spawn_projectile(self, kind):
        """Create a projectile instance for `kind` and add to all_sprites if available."""
        if kind == 'big':
            p = BigFireball(self)
        elif kind == 'small':
            p = SmallFireball(self)
        else:
            p = TracingFireball(self)
        if self.all_sprites is not None:
            self.all_sprites.add(p)
        return p

    def update(self, dt=0):
        # animation
        self.frame_timer += dt
        self.hit_cooldown = max(0, self.hit_cooldown - dt)
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)
            self.rect = self.image.get_rect(center=center)

        # firing logic: chooses random projectile type and fires toward player when cooldown elapses
        self.fire_timer += dt
        if self.fire_timer >= self.fire_cooldown:
            self.fire_timer = 0
            self.fire_cooldown = random.randint(900, 2000)
            kind = random.choice(self._proj_choices)
            self._spawn_projectile(kind)

        # ensure rect follows background offset (convert world -> screen coords)
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + getattr(self.background.rect, 'y', 0))


class BigFireball(pygame.sprite.Sprite):
    """Slow, large red fireball."""
    def __init__(self, owner, speed=100):
        super().__init__()
        self.owner = owner
        self.frames = [
            pygame.image.load("src/Images/weapon/fireball/firebal_0.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_1.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_2.gif"),
        ]
        # Scale frames to large size (big fireball)
        self.frames = [pygame.transform.scale(img, (80, 80)) for img in self.frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100
        # spawn just outside boss facing player (compute world coords)
        try:
            player_world_x = self.owner.player.rect.x - self.owner.background.rect.x
            dx = player_world_x - self.owner.world_x
            facing_right = dx >= 0
        except Exception:
            facing_right = True
        if facing_right:
            spawn_screen_x = self.owner.rect.right + 8
            vx_sign = 1
        else:
            spawn_screen_x = self.owner.rect.left - self.image.get_width() - 8
            vx_sign = -1
        spawn_screen_y = self.owner.rect.centery - (self.image.get_height() // 2)
        # convert to world coords
        self.world_x = float(spawn_screen_x - self.owner.background.rect.x)
        self.world_y = float(spawn_screen_y - self.owner.background.rect.y)
        # initial rect in screen coords
        self.rect.topleft = (int(self.world_x + self.owner.background.rect.x), int(self.world_y + self.owner.background.rect.y))

        # world velocity (px per ms)
        self.vx = (speed) / 1000.0 * vx_sign
        self.timer = 0
        self.count_time = 10000  # ms
        self.kind = 'big'

    def update(self, dt):
        # advance in world space so background motion doesn't alter apparent speed
        self.world_x += self.vx * dt
        self.rect.x = int(self.world_x + self.owner.background.rect.x)
        self.rect.y = int(self.world_y + self.owner.background.rect.y)
        self.timer += dt
        
        # animate frames
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]
        
        if self.timer >= self.count_time:
            self.kill()


class SmallFireball(pygame.sprite.Sprite):
    """Fast, small blue fireball."""
    def __init__(self, owner, speed=300):
        super().__init__()
        self.owner = owner
        size = 20
        self.frames = [
            pygame.image.load("src/Images/weapon/fireball/firebal_0.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_1.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_2.gif"),
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        try:
            player_world_x = self.owner.player.rect.x - self.owner.background.rect.x
            dx = player_world_x - self.owner.world_x
            facing_right = dx >= 0
        except Exception:
            facing_right = True
        if facing_right:
            spawn_screen_x = self.owner.rect.right + 6
            vx_sign = 1
        else:
            spawn_screen_x = self.owner.rect.left - size - 6
            vx_sign = -1
        spawn_screen_y = self.owner.rect.centery - (size // 2)
        # convert to world coords
        self.world_x = float(spawn_screen_x - self.owner.background.rect.x)
        self.world_y = float(spawn_screen_y - self.owner.background.rect.y)
        self.rect.topleft = (int(self.world_x + self.owner.background.rect.x), int(self.world_y + self.owner.background.rect.y))

        self.vx = (speed) / 1000.0 * vx_sign
        self.timer = 0
        self.count_time = 10000
        self.kind = 'small'

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100 

        self.timer = 0
        # Fireball lasts for 2 seconds
        self.count_time = 10000

    def update(self, dt):
        self.world_x += self.vx * dt
        self.rect.x = int(self.world_x + self.owner.background.rect.x)
        self.rect.y = int(self.world_y + self.owner.background.rect.y)
        self.timer += dt

        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.frame_index = 0

            self.image = self.frames[self.frame_index]
        if self.timer >= self.count_time:
            self.kill()


class TracingFireball(pygame.sprite.Sprite):
    """Slow yellow homing fireball that tracks player for ~3s."""
    def __init__(self, owner, speed=150):
        super().__init__()
        self.owner = owner
        self.frames = [
            pygame.image.load("src/Images/weapon/fireball/firebal_0.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_1.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_2.gif"),
        ]
        # Scale frames to medium size (tracing fireball)
        self.frames = [pygame.transform.scale(img, (50, 50)) for img in self.frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100
        # spawn toward player's side (screen coords -> world coords)
        try:
            player_world_x = self.owner.player.rect.x - self.owner.background.rect.x
            dx = player_world_x - self.owner.world_x
            facing_right = dx >= 0
        except Exception:
            facing_right = True
        if facing_right:
            spawn_screen_x = self.owner.rect.right + 8
        else:
            spawn_screen_x = self.owner.rect.left - self.image.get_width() - 8
        spawn_screen_y = self.owner.rect.centery - (self.image.get_height() // 2)
        self.world_x = float(spawn_screen_x - self.owner.background.rect.x)
        self.world_y = float(spawn_screen_y - self.owner.background.rect.y)
        self._pos = pygame.Vector2(self.world_x, self.world_y)
        # speed is px/ms in world space
        self.speed = speed / 1000.0
        self.timer = 0
        self.count_time = 3000
        self.kind = 'trace'
        self.rect.topleft = (int(self._pos.x + self.owner.background.rect.x), int(self._pos.y + self.owner.background.rect.y))

    def update(self, dt):
        try:
            player_world_x = self.owner.player.rect.x - self.owner.background.rect.x
            player_world_y = self.owner.player.rect.y - self.owner.background.rect.y
            target = pygame.Vector2(player_world_x, player_world_y)
            dir_vec = (target - self._pos)
            if dir_vec.length() > 0.1:
                dir_vec = dir_vec.normalize()
                self._pos += dir_vec * (self.speed * dt)
            else:
                self._pos.x += self.speed * dt
            self.world_x = float(self._pos.x)
            self.world_y = float(self._pos.y)
            self.rect.x = int(self.world_x + self.owner.background.rect.x)
            self.rect.y = int(self.world_y + self.owner.background.rect.y)
        except Exception:
            # fallback: move right slowly in world space
            self._pos.x += self.speed * dt
            self.world_x = float(self._pos.x)
            self.rect.x = int(self.world_x + self.owner.background.rect.x)

        # animate frames
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]

        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()


class OtherBlade(pygame.sprite.Sprite):
    def __init__(self, owner, time=300, offset=(0,0)):
        """Create a short-lived blade that appears outside the player and then disappears.
        The blade does not move after being spawned; it simply exists for `time` ms.
        """
        super().__init__()
        self.owner = owner
        self.offset = offset
        # thin rectangle to look like a blade
        self.frames = [
            pygame.image.load("src/Images/weapon/sword/fire/frame_0_delay-0.17s.gif").convert_alpha(),
            pygame.image.load("src/Images/weapon/sword/fire/frame_1_delay-0.17s.gif").convert_alpha(),
            pygame.image.load("src/Images/weapon/sword/fire/frame_2_delay-0.17s.gif").convert_alpha(),
        ]
        #transforming the images to correct size
        self.frames = [
            pygame.transform.scale(img, (40, 110)) for img in self.frames
        ]
        #transforming the images to correct rotation
        self.frames = [
            pygame.transform.rotate(img, -90) for img in self.frames
            ]
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100 

        # adjust frames for facing direction before picking initial image
        facing = getattr(self.owner, 'facing', 'right')
        if facing == 'left':
            # rotate by 180 to flip the -90 rotated frames to face left
            self.frames = [pygame.transform.rotate(img, 180) for img in self.frames]

        # pick current image after any rotation so sizes are correct
        self.image = self.frames[self.frame_index]

        if facing == 'right':
            x = self.owner.rect.right + 5 + self.offset[0]
        else:
            x = self.owner.rect.left - self.image.get_width() - 5 + self.offset[0]

        y = self.owner.rect.centery - (self.image.get_height() // 2) + self.offset[1]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.timer = 0
        self.count_time = 300
        # damage for obsidian variant (strong)
        self.damage = 80

    def update(self, dt):
        """Advance lifetime; blade does not move after spawning."""
        self.frame_timer += dt

        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.frame_index = 0

            self.image = self.frames[self.frame_index]

        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()

class Blade(pygame.sprite.Sprite):
    def __init__(self, owner, time=300, offset=(0,0)):
        """Create a short-lived blade that appears outside the player and then disappears.
        The blade does not move after being spawned; it simply exists for `time` ms.
        """
        super().__init__()
        self.owner = owner
        self.offset = offset
        # thin rectangle to look like a blade
        self.image = pygame.image.load("src/Images/weapon/sword/basic/Basic_sword.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.scale(self.image, (100, 35))
        facing = getattr(self.owner, 'facing', 'right')
        if facing == 'right':
            x = self.owner.rect.right + 5 + self.offset[0]
        elif facing == "left":
            self.image = pygame.transform.rotate(self.image, 180)
            x = self.owner.rect.left - self.image.get_width() - 5 + self.offset[0]
        y = self.owner.rect.centery - (self.image.get_height() // 2) + self.offset[1]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.timer = 0
        self.count_time = 300
        # normal blade damage (higher than bullet)
        self.damage = 40

    def update(self, dt):
        """Advance lifetime; blade does not move after spawning."""
        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, owner, speed=100, offset=(0,0)):
        """Create a bullet that moves in the direction the player is facing.
        """
        super().__init__()
        self.offset = offset
        self.owner = owner
        self.frames = [
            pygame.image.load("src/Images/weapon/arrow/TheArrow.png").convert_alpha(),
           
        ]
        # simple rectangle to represent bullet
        self.image = pygame.Surface((10, 5))
        self.image.fill((0, 0, 0))

        #transforming the images to correct size
        self.frames = [
            pygame.transform.scale(img, (60, 35)) for img in self.frames
        ]
        #transforming the images to correct rotation
        self.frames = [
            pygame.transform.rotate(img, -180) for img in self.frames
            ]
        # spawn just outside the player depending on facing

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100 

        # adjust frames for facing direction before picking initial image
        facing = getattr(self.owner, 'facing', 'right')
        if facing == 'right':
            # rotate by 180 to flip the -90 rotated frames to face left
            self.frames = [pygame.transform.rotate(img, 180) for img in self.frames]

        # pick current image after any rotation so sizes are correct
        self.image = self.frames[self.frame_index]

        if facing == 'left':
            x = self.owner.rect.right + 5 + self.offset[0]
        else:
            x = self.owner.rect.left - self.image.get_width() - 5 + self.offset[0]

        y = self.owner.rect.centery - (self.image.get_height() // 2) + self.offset[1]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.timer = 0
        self.count_time = 300

        facing = getattr(owner, 'facing', 'right')
        if facing == 'right':
            x = owner.rect.right + 5
        else:
            x = owner.rect.left - self.image.get_width() - 5
        y = owner.rect.centery - (self.image.get_height() // 2)

        self.rect = self.image.get_rect(topleft=(x, y))

        # convert requested speed 
        self._pos_x = float(self.rect.x)
        self.vx = (speed * 30) / 1000.0
        if facing != 'right':
            self.vx = -self.vx

        self.timer = 0
        # Bullet lasts for 1 seconds
        self.count_time = 2000
        # bullet damage
        self.damage = 15

    def update(self, dt):
        """Move the bullet using dt (milliseconds) and expire after count_time."""
        # advance animation timer
        self.frame_timer += dt
        # move with subpixel precision
        self._pos_x += self.vx * dt
        self.rect.x = int(self._pos_x)

        self.timer += dt

        if self.timer >= self.count_time:
            self.kill()


# new boss projectile
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, owner, speed=220):
        super().__init__()
        self.owner = owner
        self.frames = [
            pygame.image.load("src/Images/weapon/fireball/firebal_0.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_1.gif"),
            pygame.image.load("src/Images/weapon/fireball/firebal_2.gif"),
        ]
        # Scale frames to large size for boss bullet
        self.frames = [pygame.transform.scale(img, (60, 60)) for img in self.frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 100
        # spawn just outside the boss facing the player (compute world coords)
        try:
            player_world_x = self.owner.player.rect.x - self.owner.background.rect.x
            dx = player_world_x - self.owner.world_x
            facing_right = dx >= 0
        except Exception:
            facing_right = True

        if facing_right:
            spawn_screen_x = self.owner.rect.right + 8
            vx_sign = 1
        else:
            spawn_screen_x = self.owner.rect.left - self.image.get_width() - 8
            vx_sign = -1
        spawn_screen_y = self.owner.rect.centery - (self.image.get_height() // 2)

        self.world_x = float(spawn_screen_x - self.owner.background.rect.x)
        self.world_y = float(spawn_screen_y - self.owner.background.rect.y)
        self.rect.topleft = (int(self.world_x + self.owner.background.rect.x), int(self.world_y + self.owner.background.rect.y))

        # speed px/sec -> px/ms (world-space)
        self.vx = (speed) / 1000.0 * vx_sign
        self.timer = 0
        self.count_time = 5000
        # boss projectile does high damage
        self.damage = 80

    def update(self, dt):
        self.world_x += self.vx * dt
        self.rect.x = int(self.world_x + self.owner.background.rect.x)
        self.rect.y = int(self.world_y + self.owner.background.rect.y)
        self.timer += dt
        
        # animate frames
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[self.frame_index]
        
        if self.timer >= self.count_time:
            self.kill()


class Intro(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active = False
        self.sentences = [
            "Welcome back to the world!",
            "Root and bat monsters will approach toward you if u get too close.",
            "Be careful, some monsters disguise into a TREE.",
            "Dodge the fireballs carefully.",
            "Arrow might need some time to reload if you use it too frequently.",
            "if you see the boss, try your best to kill it!",
            "Good luck on your adventure!"
        ]
        
    def next_line(self):
        if not self.active:
            return

        self.index += 1
        
        # only render if index is valid
        if self.index < len(self.sentences):
            self.surface.fill((0, 0, 0, 160))
            text = self.sentences[self.index]
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(text_surf, (10, 10))

    def start(self):

        #active the text box, start with the first text
        self.active = True
        self.index = 0

        self.font = pygame.font.SysFont(None, 20)


        #text box
        self.surface = pygame.Surface((600, 80), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 160))
        self.image = self.surface
        self.rect = self.surface.get_rect(topleft=(200, 480))

        # Render the first line
        if self.sentences:
            text = self.sentences[0]
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(text_surf, (10, 10))

    def update(self, dt=0):
        
        # if the box is not actived, make the text box invisible
        if not self.active:
            self.surface.fill((0, 0, 0, 0))

        #clear the text box
        self.surface.fill((0, 0, 0, 160))

        #render current line of text
        #only render if active and index is valid
        if self.active and self.index < len(self.sentences):
            text = self.sentences[self.index]
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(text_surf, (10, 30))

        elif not self.active or self.index >= len(self.sentences):
            # clear the text box
            self.surface.fill((0, 0, 0, 0))  


class Rock(pygame.sprite.Sprite):
    def __init__(self, background, size=(60, 60), player=None, safe_distance=200):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("src/Images/map/obstacles/rock.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)

        # Spawn to the right of the player
        def _random_x_right_of_player():
            if player is None:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            try:
                player_world_x = player.rect.x - self.background.rect.x
            except Exception:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            # Only spawn to the right of player with safe distance
            min_spawn_x = player_world_x + safe_distance
            if max_x > min_spawn_x:
                return random.randrange(min_spawn_x, max_x + 1)
            else:
                # fallback if range is invalid
                return min_spawn_x

        self.world_x = _random_x_right_of_player()
        #self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0
        if player is not None:
            self.world_y = player.rect.centery - (self.image.get_height() // 2)
        else:
            self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0

        # If still in center band (old heuristic), move to edge (minor fallback)
        center_safe_min = int(max_x * 0.3)
        center_safe_max = int(max_x * 0.7)
        if center_safe_min <= self.world_x <= center_safe_max:
            if random.choice([True, False]):
                self.world_x = random.randrange(0, center_safe_min) if center_safe_min > 0 else 0
            else:
                self.world_x = random.randrange(center_safe_max, max_x + 1) if center_safe_max < max_x else max_x

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # Extra safety: if sprite ended up left of player on-screen, push it right of player
        try:
            if player is not None:
                player_screen_right = player.rect.right
                min_screen_x = player_screen_right + safe_distance
                if self.rect.x < min_screen_x:
                    # move world_x so on-screen x is just right of player
                    self.world_x = max(min_screen_x - self.background.rect.x, 0)
                    self.rect.x = int(self.world_x + self.background.rect.x)
        except Exception:
            pass

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)


class Spike(pygame.sprite.Sprite):
    """Obstacle placed in world coordinates as part of the background.
    Obstacles store a `world_x/world_y` and compute their onscreen `rect`
    from the background's offset so they move with the background scrolling.
    """
    def __init__(self, background, size=(60, 60), player=None, safe_distance=200):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("src/Images/map/obstacles/spike.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)

        def _random_x_right_of_player():
            if player is None:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            try:
                player_world_x = player.rect.x - self.background.rect.x
            except Exception:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            # Only spawn to the right of player with safe distance
            min_spawn_x = player_world_x + safe_distance
            if max_x > min_spawn_x:
                return random.randrange(min_spawn_x, max_x + 1)
            else:
                # fallback if range is invalid
                return min_spawn_x

        self.world_x = _random_x_right_of_player()
        # Spawn at player's height (same y position)
        if player is not None:
            self.world_y = player.rect.centery - (self.image.get_height() // 2)
        else:
            self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0

        # If spawned in center band, move to edge (minor fallback)
        center_safe_min = int(max_x * 0.3)
        center_safe_max = int(max_x * 0.7)
        if center_safe_min <= self.world_x <= center_safe_max:
            if random.choice([True, False]):
                self.world_x = random.randrange(0, center_safe_min) if center_safe_min > 0 else 0
            else:
                self.world_x = random.randrange(center_safe_max, max_x + 1) if center_safe_max < max_x else max_x

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # Extra safety: ensure spike appears to the right of player on-screen
        try:
            if player is not None:
                player_screen_right = player.rect.right
                min_screen_x = player_screen_right + safe_distance
                if self.rect.x < min_screen_x:
                    self.world_x = max(min_screen_x - self.background.rect.x, 0)
                    self.rect.x = int(self.world_x + self.background.rect.x)
        except Exception:
            pass

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)




class Portal(pygame.sprite.Sprite):
    
    def __init__(self, player, background, screen_width=1920, all_sprites=None, required_hits=50):
        super().__init__()
        self.player = player
        self.background = background
        self.screen_width = screen_width
        self.all_sprites = all_sprites

        # load boss frames (safe loads; if missing, create placeholder)
        try:
            self.frames = [
                pygame.image.load(r"src\Images\portals\portal0.gif"),
                pygame.image.load(r"src\Images\portals\portal1.gif"),
                pygame.image.load(r"src\Images\portals\portal2.gif"),
                pygame.image.load(r"src\Images\portals\portal3.gif"),
                pygame.image.load(r"src\Images\portals\portal4.gif")
            ]
        except Exception:
            # fallback: two colored surfaces
            f1 = pygame.Surface((200, 600), pygame.SRCALPHA); f1.fill((150, 30, 30))
            f2 = pygame.Surface((200, 600), pygame.SRCALPHA); f2.fill((180, 60, 60))
            self.frames = [f1, f2]

        #portal size
        self.size = (80, 150)
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 400
        self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)

        # world spawn: near the end but visible on screen
        enemy_w = self.image.get_width()
        bg_w = max(1, self.background.image.get_width())
        max_x = max(0, bg_w - enemy_w)
        # prefer near end but not off-screen: end_margin and visible clamp
        end_margin = 300
        # ensure visible on initial screen (background.rect.x likely 0)
        self.world_x = 8530
        # fallback if negative
        if self.world_x < 0:
            self.world_x = max(0, max_x - end_margin)

        # vertical position centered on player
        self.world_y = self.player.rect.centery - (self.image.get_height() // 2)

        # onscreen rect
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # boss stationary (no world_x change)
        self.speed = 0.0

        # hit requirement
        self.required_hits = required_hits
        self.hits = 0


    def update(self, dt=0):
        # animation
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = pygame.transform.scale(self.frames[self.frame_index], self.size)
            self.rect = self.image.get_rect(center=center)

        # ensure rect follows background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = self.world_y


class Shield(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        # Prefer the effect shield image; fall back to other known locations
        try:
            self.image = pygame.image.load(r"src\Images\effect\sheild_active.gif").convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 100))
        except Exception:
            try:
                # older path used previously
                self.image = pygame.image.load(r"src\Images\shield_active.gif").convert_alpha()
                self.image = pygame.transform.scale(self.image, (100, 100))
            except Exception:
                # final fallback to obsidian sword image
                self.image = pygame.image.load(r"src\Images\weapon\sword\obsidian\Obsidian_sword.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=owner.rect.center)
        self.timer = 0
        self.duration = 1000  # 1 second (expire if it doesn't block)
        self.blocks_remaining = 1

    def update(self, dt):
        self.timer += dt
        self.rect.center = self.owner.rect.center
        if self.timer >= self.duration:
            self.kill()

    def block_attack(self):
        self.blocks_remaining -= 1
        if self.blocks_remaining <= 0:
            self.kill()


class ObsidianAbility:
    def __init__(self, player):
        self.player = player
        self.cooldown = 0
        self.cooldown_duration = 10000  # 10 seconds
        self.shield = None

    def use(self):
        if self.cooldown > 0:
            return False
        # Create shield
        self.shield = Shield(self.player)
        self.cooldown = self.cooldown_duration
        return True

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.shield and not self.shield.alive():
            self.shield = None


class ObsidianBlade(pygame.sprite.Sprite):
    def __init__(self, owner, time=300, offset=(0,0)):
        """Create a short-lived obsidian blade that appears outside the player and then disappears.
        """
        super().__init__()
        self.owner = owner
        self.offset = offset
        # Load obsidian sword image
        self.image = pygame.image.load(r"src\Images\weapon\sword\obsidian\Obsidian_sword.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.scale(self.image, (100, 35))
        facing = getattr(self.owner, 'facing', 'right')
        if facing == 'right':
            x = self.owner.rect.right + 5 + self.offset[0]
        elif facing == "left":
            self.image = pygame.transform.rotate(self.image, 180)
            x = self.owner.rect.left - self.image.get_width() - 5 + self.offset[0]
        y = self.owner.rect.centery - (self.image.get_height() // 2) + self.offset[1]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.timer = 0
        self.count_time = 300
        # obsidian blade damage (strong)
        self.damage = 60

    def update(self, dt):
        """Advance lifetime; blade does not move after spawning."""
        self.timer += dt
        if self.timer >= self.count_time:
            self.kill()


class Bush(pygame.sprite.Sprite):
    """Bush obstacle - harmless decoration, works like Rock"""
    def __init__(self, background, size=(80, 80), player=None, safe_distance=200):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("src/Images/map/obstacles/bush.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)

        # Spawn to the right of the player
        def _random_x_right_of_player():
            if player is None:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            try:
                player_world_x = player.rect.x - self.background.rect.x
            except Exception:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            # Only spawn to the right of player with safe distance
            min_spawn_x = player_world_x + safe_distance
            if max_x > min_spawn_x:
                return random.randrange(min_spawn_x, max_x + 1)
            else:
                # fallback if range is invalid
                return min_spawn_x

        self.world_x = _random_x_right_of_player()
        if player is not None:
            self.world_y = player.rect.centery - (self.image.get_height() // 2)
        else:
            self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0

        # If still in center band, move to edge
        center_safe_min = int(max_x * 0.3)
        center_safe_max = int(max_x * 0.7)
        if center_safe_min <= self.world_x <= center_safe_max:
            if random.choice([True, False]):
                self.world_x = random.randrange(0, center_safe_min) if center_safe_min > 0 else 0
            else:
                self.world_x = random.randrange(center_safe_max, max_x + 1) if center_safe_max < max_x else max_x

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # Extra safety: if sprite ended up left of player on-screen, push it right of player
        try:
            if player is not None:
                player_screen_right = player.rect.right
                min_screen_x = player_screen_right + safe_distance
                if self.rect.x < min_screen_x:
                    # move world_x so on-screen x is just right of player
                    self.world_x = max(min_screen_x - self.background.rect.x, 0)
                    self.rect.x = int(self.world_x + self.background.rect.x)
        except Exception:
            pass

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)


class Tree1(pygame.sprite.Sprite):
    """Tree1 obstacle - harmless decoration, works like Rock"""
    def __init__(self, background, size=(100, 120), player=None, safe_distance=200):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("src/Images/map/obstacles/tree1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)

        # Spawn to the right of the player
        def _random_x_right_of_player():
            if player is None:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            try:
                player_world_x = player.rect.x - self.background.rect.x
            except Exception:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            # Only spawn to the right of player with safe distance
            min_spawn_x = player_world_x + safe_distance
            if max_x > min_spawn_x:
                return random.randrange(min_spawn_x, max_x + 1)
            else:
                # fallback if range is invalid
                return min_spawn_x

        self.world_x = _random_x_right_of_player()
        if player is not None:
            self.world_y = player.rect.centery - (self.image.get_height() // 2)
        else:
            self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0

        # If still in center band, move to edge
        center_safe_min = int(max_x * 0.3)
        center_safe_max = int(max_x * 0.7)
        if center_safe_min <= self.world_x <= center_safe_max:
            if random.choice([True, False]):
                self.world_x = random.randrange(0, center_safe_min) if center_safe_min > 0 else 0
            else:
                self.world_x = random.randrange(center_safe_max, max_x + 1) if center_safe_max < max_x else max_x

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # Extra safety: if sprite ended up left of player on-screen, push it right of player
        try:
            if player is not None:
                player_screen_right = player.rect.right
                min_screen_x = player_screen_right + safe_distance
                if self.rect.x < min_screen_x:
                    # move world_x so on-screen x is just right of player
                    self.world_x = max(min_screen_x - self.background.rect.x, 0)
                    self.rect.x = int(self.world_x + self.background.rect.x)
        except Exception:
            pass

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)


class Tree2(pygame.sprite.Sprite):
    """Tree2 obstacle - harmless decoration, works like Rock"""
    def __init__(self, background, size=(110, 130), player=None, safe_distance=200):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("src/Images/map/obstacles/tree2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)

        # Spawn to the right of the player
        def _random_x_right_of_player():
            if player is None:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            try:
                player_world_x = player.rect.x - self.background.rect.x
            except Exception:
                return random.randrange(0, max_x + 1) if max_x >= 0 else 0
            # Only spawn to the right of player with safe distance
            min_spawn_x = player_world_x + safe_distance
            if max_x > min_spawn_x:
                return random.randrange(min_spawn_x, max_x + 1)
            else:
                # fallback if range is invalid
                return min_spawn_x

        self.world_x = _random_x_right_of_player()
        if player is not None:
            self.world_y = player.rect.centery - (self.image.get_height() // 2)
        else:
            self.world_y = random.randrange(0, max_y + 1) if max_y >= 0 else 0

        # If still in center band, move to edge
        center_safe_min = int(max_x * 0.3)
        center_safe_max = int(max_x * 0.7)
        if center_safe_min <= self.world_x <= center_safe_max:
            if random.choice([True, False]):
                self.world_x = random.randrange(0, center_safe_min) if center_safe_min > 0 else 0
            else:
                self.world_x = random.randrange(center_safe_max, max_x + 1) if center_safe_max < max_x else max_x

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))

        # Extra safety: if sprite ended up left of player on-screen, push it right of player
        try:
            if player is not None:
                player_screen_right = player.rect.right
                min_screen_x = player_screen_right + safe_distance
                if self.rect.x < min_screen_x:
                    # move world_x so on-screen x is just right of player
                    self.world_x = max(min_screen_x - self.background.rect.x, 0)
                    self.rect.x = int(self.world_x + self.background.rect.x)
        except Exception:
            pass

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)
