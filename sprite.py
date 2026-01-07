import pygame
import random

class Player(pygame.sprite.Sprite):
    """
    Player is not really moving, instead it's the backgound moving. 
    player only moves when the background reach the edge
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        #images of different actions
        # Use simple Surfaces so code can run without external image files
        # load animation frames (some are lists of frames)
        self.stand = [pygame.image.load("smt/Images/player_animation/frame_03_delay-0.08s.gif")]

        self.move_l = [
            pygame.image.load("smt/Images/player_animation/frame_40_delay-0.08s.gif"),
            pygame.image.load("smt/Images/player_animation/frame_41_delay-0.08s.gif"),
        ]

        self.move_r = [
            pygame.image.load("smt/Images/player_animation/frame_14_delay-0.08s.gif"),
            pygame.image.load("smt/Images/player_animation/frame_15_delay-0.08s.gif"),
        ]

        # single-frame surfaces for jump/attack/die (wrap as lists for uniform handling)
        jump_surf = pygame.image.load("smt/Images/player_animation/frame_jump_delay-0.08s.gif")
        
        attack_surf = pygame.Surface((60, 40))
        attack_surf.fill((255, 128, 0))
        die_surf = pygame.Surface((10,10))
        die_surf.fill((128, 128, 128))

        self.jump = [jump_surf]
        self.attack_img = [attack_surf]
        self.die = [die_surf]

        # scale all loaded frames to the player's size (100x130)
        def _scale_list(frames, size=(80, 130)):
            return [pygame.transform.scale(f, size) for f in frames]

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

    def move_left(self):
        # switch to left-walk animation
        self.set_animation('move_l')
        self.facing = 'left'
        # no direct horizontal movement of the player; background scrolls instead

    def move_right(self):
        # switch to right-walk animation
        self.set_animation('move_r')
        self.facing = 'right'
        # no direct horizontal movement of the player; background scrolls instead

    def move_up(self):
        # jump only when on ground
        if not self.on_ground:
            return
        # switch to jump animation
        self.set_animation('jump')
        # initiate jump: negative vy moves up
        self.vy = -1
        self.on_ground = False
        # record background start position so we can restore it on landing
        if hasattr(self, 'background') and self.background is not None:
            self._bg_start_y = self.background.rect.y
        

    def death(self):
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

                # landing detection: when background returns to its start y, consider landed
                if hasattr(self, '_bg_start_y') and self.background.rect.y >= self._bg_start_y:
                    self.background.rect.y = self._bg_start_y
                    self.vy = 0.0
                    self.on_ground = True
                    # return to standing image when landed
                    self.init_move()
            else:
                # fallback: move player rect if no background reference
                self.rect.y += dy
                if self.ground_y is not None and self.rect.bottom >= self.ground_y:
                    self.rect.bottom = self.ground_y
                    self.vy = 0.0
                    self.on_ground = True
                    self.init_move()

class Background(pygame.sprite.Sprite):
    def __init__(self, image, screen_width=1920):
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
    def __init__(self, player, background, screen_width=1920):
        super().__init__()
        self.player = player
        self.background = background
        self.screen_width = screen_width
        
        # Load and setup enemy image
        self.frames = [
            pygame.image.load("smt\Images\Root_monster_frame0.gif").convert_alpha(),
            pygame.image.load("smt\Images\Root_monster_frame1.gif").convert_alpha(),
        ]
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 500
        self.image = self.frames[self.frame_index]
        self.image = pygame.transform.scale(self.image, (80, 80))
        
        # Spawn at random horizontal position in world coordinates
        self.world_x = random.randint(500, 2340)  # Random position within the extended background
        self.world_y = self.player.rect.centery - 40
        
        # Set initial screen position
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y))
        # movement parameters (pixels per ms)
        self.speed = 0.03  # ~60 px / 1000 ms => 60 px/s
        # when player is within this horizontal distance (in world coords), enemy will chase
        self.chase_radius = 500
    
    def update(self, dt=0):
        self.frame_timer += dt

        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.frame_index = 0

            self.image = self.frames[self.frame_index]
        # Basic chasing behavior: move in world-space toward player when close
        try:
            # compute player's world x (player screen x minus background offset)
            player_world_x = self.player.rect.x - self.background.rect.x
            dx = player_world_x - self.world_x
            # if within chase radius, move toward player
            if abs(dx) <= self.chase_radius and abs(dx) > 2:
                direction = 5 if dx > 0 else -5
                # advance world_x using dt-scaled speed
                self.world_x += direction * self.speed * dt
        except Exception:
            # if any reference missing, skip movement
            pass

        # Update screen position based on background movement and world coords
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = self.world_y

class Other_blade(pygame.sprite.Sprite):
    def __init__(self, owner, time=300, offset=(0,0)):
        """Create a short-lived blade that appears outside the player and then disappears.
        The blade does not move after being spawned; it simply exists for `time` ms.
        """
        super().__init__()
        self.owner = owner
        self.offset = offset
        # thin rectangle to look like a blade
        self.frames = [
            pygame.image.load("smt/Images/frame_0_delay-0.17s.gif").convert_alpha(),
            pygame.image.load("smt/Images/frame_1_delay-0.17s.gif").convert_alpha(),
            pygame.image.load("smt/Images/frame_2_delay-0.17s.gif").convert_alpha(),
        ]
        #transforming the images to correct size
        self.frames = [
            pygame.transform.scale(img, (50, 140)) for img in self.frames
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
        self.image = pygame.image.load("smt\Images\Obsidian_sword.png")
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.scale(self.image, (140, 50))
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
            pygame.image.load("smt/Images/firebal_0.gif").convert_alpha(),
            pygame.image.load("smt/Images/firebal_1.gif").convert_alpha(),
            pygame.image.load("smt/Images/firebal_2.gif").convert_alpha(),
        ]
        # simple rectangle to represent bullet
        self.image = pygame.Surface((10, 5))
        self.image.fill((0, 0, 0))

        #transforming the images to correct size
        self.frames = [
            pygame.transform.scale(img, (50,50)) for img in self.frames
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
        # Bullet lasts for 2 seconds
        self.count_time = 2000


    def update(self, dt):
        """Move the bullet using dt (milliseconds) and expire after count_time."""
        # move with subpixel precision
        self._pos_x += self.vx * dt
        self.rect.x = int(self._pos_x)

        self.timer += dt

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
            "Welcome to the game!",
            "Use WASD to move around.",
            "Press E to attack with a blade.",
            "Press Q to shoot a bullet.",
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
        self.index = 0

        self.font = pygame.font.SysFont(None, 28)


        #text box
        self.surface = pygame.Surface((800, 120), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 160))
        self.image = self.surface
        self.rect = self.surface.get_rect(topleft=(560, 900))

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
            self.surface.blit(text_surf, (10, 50))

        elif not self.active or self.index >= len(self.sentences):
            # clear the text box
            self.surface.fill((0, 0, 0, 0))  


class Rock(pygame.sprite.Sprite):
    """Obstacle placed in world coordinates as part of the background.
    Obstacles store a `world_x/world_y` and compute their onscreen `rect`
    from the background's offset so they move with the background scrolling.
    """
    def __init__(self, background, size=(100, 100)):
        super().__init__()
        self.background = background

        # Load and prepare image
        self.image = pygame.image.load("smt/Images/rock.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Choose a random position inside the background (world coordinates)
        max_x = max(0, self.background.image.get_width() - self.width)
        max_y = max(0, self.background.image.get_height() - self.height)
        self.world_x = random.randrange(0, max_x + 1)
        self.world_y = random.randrange(0, max_y + 1)

        # Initial on-screen rect uses background offset
        self.rect = self.image.get_rect(topleft=(self.world_x + self.background.rect.x, self.world_y + self.background.rect.y))

    def update(self, dt=0):
        # Keep onscreen rect in sync with background offset
        self.rect.x = int(self.world_x + self.background.rect.x)
        self.rect.y = int(self.world_y + self.background.rect.y)