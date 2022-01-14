import pygame as pg
from random import randint, uniform
vec = pg.math.Vector2
import pygame
import math
import Weapon
import pygame_menu

WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (140, 140, 140)

r_val = 4
w_val = 5
d_val = 3

walls = []

# Mob properties
MOB_SIZE = 32
MAX_SPEED = 2
MAX_FORCE = 0.4
RAND_TARGET_TIME = 500
WANDER_RING_DISTANCE = 150
WANDER_RING_RADIUS = 50
WANDER_TYPE = 2
WALL_LIMIT = 30


APPROACH_RADIUS = 120

FLEE_DISTANCE = 200

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))

all_sprites = pg.sprite.Group()

class Mobby(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load("wolf.png")
        self.image = pg.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos

    def follow_mouse(self):
        mpos = pg.mouse.get_pos()
        self.acc = (mpos - self.pos).normalize() * 0.5

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < APPROACH_RADIUS:
            self.desired *= dist / APPROACH_RADIUS * MAX_SPEED
        else:
            self.desired *= MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def update(self):
        # self.follow_mouse()

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.kill()

        if 12 == 12:
            self.acc = self.seek_with_approach((340, 240))
        # equations of motion
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = self.pos
        
class Mobse(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load("lun.png")
        self.image = pg.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos

    def follow_mouse(self):
        mpos = pg.mouse.get_pos()
        self.acc = (mpos - self.pos).normalize() * 0.5

    def flee(self, target):
        steer = vec(0, 0)
        dist = self.pos - target
        if dist.length() < FLEE_DISTANCE:
            self.desired = (self.pos - target).normalize() * MAX_SPEED
        else:
            self.desired = self.vel.normalize() * MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def update(self):
        # self.follow_mouse()

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                 self.kill()

        self.acc = self.flee(pg.mouse.get_pos())
        # equations of motion
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = self.pos

class Mob(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load("bun.png")
        self.image = pg.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.last_update = 0
        self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def wander_improved(self):
        future = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
        target = future + vec(WANDER_RING_RADIUS, 0).rotate(uniform(0, 360))
        self.displacement = target
        return self.seek(target)

    def wander(self):
        # select random target every few sec
        now = pg.time.get_ticks()
        if now - self.last_update > RAND_TARGET_TIME:
            self.last_update = now
            self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        return self.seek(self.target)

    def update(self):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.kill()

        if WANDER_TYPE == 1:
            self.acc = self.wander()
        else:
            self.acc = self.wander_improved()
        # equations of motion
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = self.pos


def normalize_vector(vector):
    if vector == [0, 0]:
        return [0, 0]    
    pythagoras = math.sqrt(vector[0]*vector[0] + vector[1]*vector[1])
    return (vector[0] / pythagoras, vector[1] / pythagoras)
class Player(pygame.sprite.Sprite):
    projectiles = pygame.sprite.Group()
    def __init__(self, screenSize):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.image.load("hunt.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(x=screenSize[0]//2,
                                        y=screenSize[1]//2)
        
        self.pos = [screenSize[0] // 2, screenSize[1] // 2]
        self.health = 3
        self.alive = True
        self.movementVector = [0, 0]
        self.movementSpeed = 3
        self.availableWeapons = [Weapon.Pistol(),
                                 Weapon.Shotgun(),
                                 Weapon.MachineGun()]
        self.equippedWeapon = self.availableWeapons[0]

    def move(self, screenSize, tDelta):
        self.movementVector = normalize_vector(self.movementVector)
        newPos = (self.pos[0] + self.movementVector[0]*self.movementSpeed*tDelta,
                  self.pos[1] + self.movementVector[1]*self.movementSpeed*tDelta)
        if newPos[0] < 0:
            self.pos[0] = 0
        elif newPos[0] > screenSize[0] - self.rect.width:
            self.pos[0] = screenSize[0] - self.rect.width
        else:
            self.pos[0] = newPos[0]

        if newPos[1] < 0:
            self.pos[1] = 0
        elif newPos[1] > screenSize[1]-self.rect.height:
            self.pos[1] = screenSize[1]-self.rect.width
        else:
            self.pos[1] = newPos[1]
        
        self.rect.topleft = self.pos
        self.movementVector = [0, 0]
        
    def shoot(self, mousePos):
        self.equippedWeapon.shoot(self, mousePos)
        
    def render(self, surface):
        surface.blit(self.image, self.pos)

class Wall(object):
    def __init__(self, x, y, w = 16, h = 16):
        self.rect = pygame.Rect(x, y, w, h)

        
def process_mouse(mouse, hero):
    if mouse[0]:
        hero.sprite.shoot(pg.mouse.get_pos())

def render_entities(hero):
    hero.sprite.render(screen)
    for proj in Player.projectiles:
        proj.render(screen)


def move_entities(hero, timeDelta):
    score = 0
    hero.sprite.move(screen.get_size(), timeDelta)
    return score
def lops():
    clock = pg.time.Clock()
    global d_val, w_val, r_val, walls
    enemy = []
    print(d_val, w_val, r_val)
    for i in range(d_val):
        enemy.append(Mobse())
    for i in range(w_val):
        enemy.append(Mob())
    for i in range(r_val):
        enemy.append(Mobby())
    
    walls.append(Wall(100, 500, w=600, h=10))
    walls.append(Wall(100, 100, w=10, h=400))
    walls.append(Wall(690, 100, w=10, h=400))
    walls.append(Wall(100, 100, w=600, h=10))
    
    paused = False
    show_vectors = False
    running = True
    scoreFont = pg.font.Font("fonts/UpheavalPro.ttf", 30)
    healthFont = pg.font.Font("fonts/OmnicSans.ttf", 50)
    healthRender = healthFont.render('z', True, pg.Color('red'))
    pg.display.set_caption("Steer")
    hero = pygame.sprite.GroupSingle(Player(screen.get_size()))
    enemies = pygame.sprite.Group()
    lastEnemy = 0
    score = 0
    while running:
        keys = pg.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        # clock.tick(FPS)
        process_mouse(mouse, hero)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    paused = not paused
                if event.key == pg.K_m:
                    Mob()
                if event.key == pg.K_w:
                    hero.sprite.movementVector[1] -= 1
                if event.key == pg.K_a:
                    hero.sprite.movementVector[0] -= 1
                if event.key == pg.K_s:
                    hero.sprite.movementVector[1] += 1
                if event.key == pg.K_d:
                    hero.sprite.movementVector[0] += 1
                if event.key == pg.K_1:
                    hero.sprite.equippedWeapon = hero.sprite.availableWeapons[0]
                if event.key == pg.K_2:
                    hero.sprite.equippedWeapon = hero.sprite.availableWeapons[1]
                if event.key == pg.K_3:
                    hero.sprite.equippedWeapon = hero.sprite.availableWeapons[2]
        currentTime = pg.time.get_ticks()
        score += move_entities(hero, clock.get_time()/17)
        render_entities(hero)
        if not paused:
            all_sprites.update()
        pg.display.set_caption("{:.2f}".format(clock.get_fps()))
        screen.fill(WHITE)
        all_sprites.draw(screen)
        for i in walls:
            pygame.draw.rect(screen, LIGHTGRAY, i)
        if show_vectors:
            for sprite in all_sprites:
                sprite.draw_vectors()
        for hp in range(hero.sprite.health):
            screen.blit(healthRender, (15 + hp*35, 0))
        scoreRender = scoreFont.render(str(12), True, pg.Color('black'))
        scoreRect = scoreRender.get_rect()
        scoreRect.right = WIDTH - 20
        scoreRect.top = 20
        screen.blit(scoreRender, scoreRect)
        
        clock.tick(120)
        pg.display.flip()


def MyRab(value):
    global r_val
    try:
        r_val = int(value)
    except:
        r_val = 0
