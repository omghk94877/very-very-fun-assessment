import pygame

class Player(pygame.sprite.Sprite):
    """
    Player is not really moving, instead it's the backgound moving. 
    player only moves when the background reach the edge
    """

    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)

        #images of different actions
        self.stand = "image"
        self.move_l = "image"
        self.move_r = "image"
        self.jump = "image"
        self.attack = "image"
        self.die = "image"


        #starting image is stand
        self.image = self.stand

        #setting rect for collision
        self.rect = self.image.get_rect()

        #displacement
        self.dx = 0
        self.dy = 0

    def move_left(self):
        self.image = self.move_l

    def move_right(self):
        self.image = self.move_r

    def move_up(self):
        self.image = self.jump
        

    def death(self):
        self.image = self.die
        

    def att(self):
        self.image = self.attack
        

    def update(self):
        pass

class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()

        #background, get from the parameter from main
        self.image = image
        self.rect = self.image.get_rect()

        #speed
        self.dx = 0
        self.dy = 0

    def player_move_left(self):
        """
        if player move left, background move right
        """
        self.dx = 5

    def player_move_right(self):
        """
        if player move right, background move left
        """  
        self.dx = -5

    def player_move_up(self):
        pass

    def stop(self):
        self.dx = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy


class Enemy(pygame.sprite.Sprite):
    pass

class Blade(pygame.sprite.Sprite):
    pass

class Bullet(pygame.sprite.Sprite):
    pass

class Weapons(pygame.sprite.Sprite):
    pass

class Entities(pygame.sprite.Sprite):
    """
    Include level, health, etc
    """
    pass

class Obstacle(pygame.sprite.Sprite):
    pass