import pygame
from random import randint, uniform, shuffle
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
        if self.rect.centery > WINDOW_HEIGHT or self.rect.centery < 0 or self.rect.centerx > WINDOW_WIDTH or self.rect.centerx < 0:
            self.rect.center -= self.direction * self.speed * dt
            
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf, speed=500):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.speed = speed
    
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
    def __init__(self, surf, pos, groups, offsets):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400 + offsets[0], 500 + offsets[0])
        self.rotation = 0
        self.rspeed = randint(40 + offsets[1], 200 + offsets[1])

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
        self.rotation += self.rspeed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Heart(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = pygame.transform.smoothscale_by(surf, 0.16)
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(400, 700)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

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

class Health(pygame.sprite.Sprite):
    def __init__(self, surf, life, groups):
        super().__init__()
        groups[0].add(self, layer=1)
        groups[1].add(self)
        self.image = pygame.transform.smoothscale_by(surf, 0.05)
        self.rect = self.image.get_frect(midtop = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40))
        self.number = life
        self.direction = 0

    def update(self, dt):
        if self.number > 1:
            if self.number % 2 == 0:
                self.direction = -1 * (self.number / 2)
            else:
                self.direction = (self.number-1) / 2
            self.rect = self.image.get_frect(midtop = ((WINDOW_WIDTH / 2) + 30 * self.direction, WINDOW_HEIGHT - 40))

def collisions():
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        for life in health_sprites:
            if life.number == player.life:
                if player.life > 3:
                    life.kill()
                life.image = pygame.transform.smoothscale_by(health_image, 0.05)
        damage_sound.play()
        player.life -= 1
    if player.life == 0:
        player.kill()
        return False
     
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            Explosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

    if pygame.sprite.spritecollide(player, heart_sprites, True, pygame.sprite.collide_mask):
        player.life += 1
        if player.life > 3:
            Health(health_black_image, player.life, (all_sprites, health_sprites))
        else:
            for life in health_sprites:
                if life.number == player.life:
                    life.image = pygame.transform.smoothscale_by(health_black_image, 0.05)


    return True

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
    restart_button = restart_rect.inflate(120,0).move(0,-5)
    pygame.draw.rect(screen, '#f0f0f0', restart_button)
    screen.blit(restart_surf, restart_rect)

    quit_surf = buttom_font.render('Quit', True, "#8b0a20")
    quit_rect = quit_surf.get_frect(midtop = restart_rect.move(0,18).midbottom)
    quit_button = restart_rect.inflate(120,0).move(0,50)
    pygame.draw.rect(screen, '#f0f0f0', quit_button)
    screen.blit(quit_surf, quit_rect)

    return restart_button, quit_button

def game(state, start, color):
    # color setup
    tar = None
    trigger_color = False
    colors = [c for c in pygame.colordict.THECOLORS.values() if sum(c[:3]) < 600]
    shuffle(colors)

    level = 0

    meteor_timer = 500
    meteor_speed_offset = 0
    meteor_rotation_offset = 0

    star_speed = 400
    star_height = 0 - WINDOW_HEIGHT
    star_range = 16

    while state:
        dt = clock.tick() / 1000
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            
            if event.type == star_event:
                if level % 10 == 0:
                    star_speed += 100
                    if level % 50 == 0:
                        star_height *= 1.5
                        star_range += 5
                    for _ in range(star_range):
                        Star(all_sprites, (randint(0, WINDOW_WIDTH), randint(int(star_height), 0)), star_surf, star_speed)                        
                else:
                    for _ in range(star_range):
                        Star(all_sprites, (randint(0, WINDOW_WIDTH), randint(int(star_height), 0)), star_surf, star_speed)

            if event.type == meteor_event:
                x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                meteor = Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites), (meteor_speed_offset, meteor_rotation_offset))
                all_sprites.change_layer(meteor, 1)
                if level % 5 == 0 and meteor_timer > 100:
                    meteor_timer *= 1-(level/200)
                    pygame.time.set_timer(meteor_event, int(meteor_timer))

            if event.type == level_event:
                level+=1
                tar = colors[level]
                trigger_color = True
                if sum(tar[:3]) < 300:
                    meteor_speed_offset += 5
                else:
                    meteor_rotation_offset += 2

                if level % 5 == 0 and player.cooldown_duration > 100:
                    player.cooldown_duration -= 150
                    
            if event.type == color_event and trigger_color:
                color = color_fill(color, target=tar)
                if color == tar:
                    trigger_color = False

            if event.type == heart_event:
                Heart(health_red_image, (randint(0, WINDOW_WIDTH), randint(-200, -100)), (all_sprites, heart_sprites))
                pygame.time.set_timer(heart_event, randint(5_000, 50_000))
                

        # update
        all_sprites.update(dt)
        state = collisions()

        # draw the game
        screen.fill(color)
        display_score((pygame.time.get_ticks() - start) // 100)
        all_sprites.draw(screen)


        pygame.display.flip()

def over(boom, frame):
    restart, quit = display_game_over()

    while True:
        dt = clock.tick() / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart.collidepoint(event.pos):
                    return True
                if quit.collidepoint(event.pos):
                    return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
        
        # update
        boom += 40 * dt
        if boom < 100:
            Explosion(explosion_frames, (randint(0, WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)), final_boom)
            explosion_sound.play()

        final_boom.update(dt)

        # draw game_over screen
        # screen.fill('#3a2e3f')
        screen.blit(pygame.transform.grayscale(frame), (0,0))
        final_boom.draw(screen)
        display_game_over()

        pygame.display.flip()

def color_fill(color=pygame.Color(58,46,63), speed=1, target=None):
    if target:
        target = pygame.Color(target)
        r = color.r + speed if color.r < target.r else color.r - speed if color.r > target.r else target.r
        g = color.g + speed if color.g < target.g else color.g - speed if color.g > target.g else target.g
        b = color.b + speed if color.b < target.b else color.b - speed if color.b > target.b else target.b
        return pygame.Color(r,g,b)
    return color

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
health_image = pygame.image.load(join('images', 'health.png')).convert_alpha()
health_black_image = pygame.image.load(join('images', 'health-black.png')).convert_alpha()
health_red_image = pygame.image.load(join('images', 'health-red.png')).convert_alpha()

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

star_event = pygame.event.custom_type()
pygame.time.set_timer(star_event, 1500)

level_event = pygame.event.custom_type()
pygame.time.set_timer(level_event, 10_000)

color_event = pygame.event.custom_type()
pygame.time.set_timer(color_event, 50)

heart_event = pygame.event.custom_type()
pygame.time.set_timer(heart_event, randint(5_000, 50_000))

while running:
    # sprites
    all_sprites = pygame.sprite.LayeredUpdates()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    final_boom = pygame.sprite.Group()
    health_sprites = pygame.sprite.Group()
    heart_sprites = pygame.sprite.Group()
    for _ in range(30):
        Star(all_sprites, (randint(0, WINDOW_WIDTH), randint(-WINDOW_HEIGHT, WINDOW_HEIGHT)), star_surf)
    player = Player(all_sprites)
    for i in range(player.life):
        Health(health_black_image, i+1, (all_sprites, health_sprites))

    # reset sound
    pygame.mixer.stop()
    game_music.play(loops=-1)

    # game start
    start = pygame.time.get_ticks()
    color = color_fill()
    if not game(True, start, color):
        pygame.mixer.stop()
        final_explosion = 0
        frozen_frame = screen.copy()

        # game is over
        running = over(final_explosion, frozen_frame)
    else:
        running = False

pygame.quit()