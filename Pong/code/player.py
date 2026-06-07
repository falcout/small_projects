from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface((SIZE['paddle']))
        self.rect = self.image.get_frect(center = POS['player'])
        self.image.fill(COLORS['paddle'])

        self.direction = 0
        self.speed = SPEED['player']

    def move(self, dt):
        keys = pygame.key.get_pressed()
        self.direction = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.rect.y += self.direction * self.speed * dt
        self.collision()

    def collision(self):
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

    def update(self, dt):
        self.move(dt)
        