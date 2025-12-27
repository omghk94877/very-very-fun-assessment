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



class Enemy(pygame.sprite.Sprite):
    pass

class Blade(pygame.sprite.Sprite):
    pass

class Bullet(pygame.sprite.Sprite):
    pass

class Background(pygame.sprite.Sprite):
    pass

class Weapons(pygame.sprite.Sprite):
    pass

class Physics(pygame.sprite.Sprite):
    pass

class Obstacle(pygame.sprite.Sprite):
    pass