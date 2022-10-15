# Author: Evan Finnigan

from pygame import *
from time import time as t
from random import randint
 
#background music
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')
 
#fonts and captions
font.init()
font1 = font.SysFont('Sans-Serif', 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont('Sans-Serif', 36)
 
#we need the following images:
img_back = "galaxy.jpg" #game background
img_hero = "rocket.png" #hero
img_bullet = "bullet.png" #bullet
img_enemy = "ufo.png" #enemy
img_asteroid = "asteroid.png"
 
score = 0 #ships destroyed
lost = 0 #ships missed
max_lost = 3 #lose if you miss that many
 
#parent class for other sprites
class GameSprite(sprite.Sprite):
    #class constructor
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #Call for the class (Sprite) constructor:
        sprite.Sprite.__init__(self)
    
        #every sprite must store the image property
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        # self.image = image.load(player_image)
        self.speed = player_speed
    
        #every sprite must have the rect property that represents the rectangle it is fitted in
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    #method drawing the character on the window
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
 
#main player class
class Player(GameSprite):
    lives = 3
    reloading = False
    reload_time = 5
    lastframe = t()
    #method to control the sprite with arrow keys
    def update(self):
        deltatime = t() - self.lastframe
        self.lastframe = t()
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if self.reloading:
            print(self.reload_time)
            self.reload_time -= deltatime
            if self.reload_time <= 0:
                self.reloading = False
                self.reload_time = 5
    #method to "shoot" (use the player position to create a bullet there)
    def fire(self):
        if not self.reloading:
            fire_sound.play()
            bullet = Bullet(img_bullet, self.rect.x, self.rect.y, 15, 20, -15)
            bullets.add(bullet)
            if len(bullets.sprites()) >= 5:
                self.reloading = True

 
#enemy sprite class  
class Enemy(GameSprite):
    
    #enemy movement
    def update(self, finish):
        if finish:
            self.rect.y -= self.speed
            if self.rect.y < 0 - 64:
                self.kill()
                del self
                return
        else:
            self.rect.y += self.speed
        #disappears upon reaching the screen edge
        if self.rect.y > win_height:
            global lost
            self.respawn()
            lost = lost + 1
    def respawn(self):
        self.rect.x = randint(80, win_width - 80)
        self.rect.y = 0
        
class Asteroid(GameSprite):
    def update(self, finish):
        if finish:
            self.rect.y -= self.speed
            if self.rect.y < 0 - 64:
                self.kill()
                del self
                return
        else:
            self.rect.y += self.speed
        #disappears upon reaching the screen edge
        if self.rect.y > win_height:
            global lost
            self.respawn()
    def respawn(self):
        self.rect.x = randint(80, win_width - 80)
        self.rect.y = 0

#bullet sprite class  
class Bullet(GameSprite):
    #bullet movement
    def update(self):
        self.rect.y += self.speed
        #disappears upon reaching the screen edge
        if self.rect.y < 0:
            self.kill()
            del self

#Create a window
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
 
#create sprites
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
 
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 64,64, randint(1, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1,3):
    asteroid = Asteroid(img_asteroid, randint(80, win_width - 80), -40, 128,128, randint(1, 5))
    asteroids.add(asteroid)

bullets = sprite.Group()
 
#the "game is over" variable: as soon as True is there, sprites stop working in the main loop
finish = False
#Main game loop:
run = True #the flag is reset by the window close button
while run:
    #"Close" button press event
    for e in event.get():
        if e.type == QUIT:
            run = False
        #event of pressing the spacebar - the sprite shoots
        elif e.type == KEYDOWN and not finish:
            if e.key == K_SPACE:
                ship.fire()
    
    window.blit(background,(0,0))

    #write text on the screen
    text = font2.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (10, 20))

    text_lose = font2.render("Missed: " + str(lost), 1, (255, 255, 255))
    window.blit(text_lose, (10, 50))

    ship.update()
    ship.reset()

    # if not finish:
    #launch sprite movements
    monsters.update(finish)
    bullets.update()
    asteroids.update(finish)

    #update them in a new location in each loop iteration
    
    collided_sprites = sprite.groupcollide(monsters, bullets, False, True)
    # respawn the enemies in the collided sprites list
    for item in collided_sprites:
        item.respawn()
        score += 1

    collided_asteroid = sprite.spritecollideany(ship, asteroids)
    if collided_asteroid:
        collided_asteroid.respawn()
        ship.lives -= 1
        if ship.lives <= 0:
            lost += 3
            finish = True

    monsters.draw(window)
    bullets.draw(window)
    asteroids.draw(window)

    # Game over
    if score >= 10 or lost >= 3:
        finish = True
    
    if finish:
        if score >= 10:
            window.blit(win, (200, 200))
        else:
            window.blit(lose, (200, 200))

    display.update()

    #the loop is executed each 0.05 sec
    time.delay(50)
