import pygame
from random import randint, uniform
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__()
        groups.add(self, layer=1)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300
        self.life = 3

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask
        self.mask = pygame.mask.from_surface(self.image)
    

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
            

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        if self.rect.centery > WINDOW_HEIGHT:
            self.rect.center -= self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.speed = 500
    
    def update(self, dt):
        self.rect.center += pygame.Vector2(0,1) * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation = 0
        self.rspeed = randint(40,200)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
        self.rotation += self.rspeed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.frame_index += 40 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        damage_sound.play()
        player.life -= 1
    if player.life == 0:
        player.kill()
        running = False
     
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            Explosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score(time):
    current_time = time
    text_surf = font.render(str(current_time), True, '#f0f0f0')
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, '#f0f0f0', text_rect.move(0, -8).inflate(20,10), 5, 10)

def display_game_over():
    over_surf = font.render('GAME OVER!', True, '#f0f0f0')
    over_rect = over_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    pygame.draw.rect(screen, 'black', over_rect.inflate(80,160).move(0, 55))
    pygame.draw.rect(screen, '#f0f0f0', over_rect.inflate(80,160).move(0, 55), 5)
    screen.blit(over_surf, over_rect)

    restart_surf = buttom_font.render('Restart', True, "#38d035")
    restart_rect = restart_surf.get_frect(midtop = over_rect.move(0,20).midbottom)
    pygame.draw.rect(screen, '#f0f0f0', restart_rect.inflate(120,0).move(0,-5))
    screen.blit(restart_surf, restart_rect)

    quit_surf = buttom_font.render('Quit', True, "#8b0a20")
    quit_rect = quit_surf.get_frect(midtop = restart_rect.move(0,18).midbottom)
    pygame.draw.rect(screen, '#f0f0f0', restart_rect.inflate(120,0).move(0,50))
    screen.blit(quit_surf, quit_rect)

# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')
running = True
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
buttom_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops=-1)

# sprites
all_sprites = pygame.sprite.LayeredUpdates()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
final_boom = pygame.sprite.Group()
for _ in range(30):
    Star(all_sprites, (randint(0, WINDOW_WIDTH), randint(-WINDOW_HEIGHT, WINDOW_HEIGHT)), star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

star_event = pygame.event.custom_type()
pygame.time.set_timer(star_event, 1500)

while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == star_event:
            for _ in range(16):
                Star(all_sprites, (randint(0, WINDOW_WIDTH), randint(-WINDOW_HEIGHT, 0)), star_surf)
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            meteor = Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
            all_sprites.change_layer(meteor, 1)

    # update
    all_sprites.update(dt)
    collisions()

    # draw the game
    screen.fill('#3a2e3f')
    display_score(pygame.time.get_ticks() // 100)
    all_sprites.draw(screen)


    pygame.display.flip()

pygame.mixer.stop()
final_explosion = 0
score = pygame.time.get_ticks() // 100
frozen_frame = screen.copy()

while not running:
    dt = clock.tick() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = True
    
    # update
    final_explosion += 40 * dt
    if final_explosion < 100:
        Explosion(explosion_frames, (randint(0, WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)), final_boom)
        explosion_sound.play()

    final_boom.update(dt)

    # draw game_over screen
    # screen.fill('#3a2e3f')
    screen.blit(pygame.transform.grayscale(frozen_frame), (0,0))
    final_boom.draw(screen)
    display_score(score)
    display_game_over()

    pygame.display.flip()

pygame.quit()