from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((40,60))
        self.rect = self.image.get_frect(center = pos)

        self.old_rect = self.rect.copy()
        self.collision_sprites = collision_sprites

        self.gravity = 2
        self.direction = pygame.Vector2()
        self.speed = 500

    def move(self, dt):
        self.rect.centerx += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.centery += (self.direction.y + self.gravity) * self.speed * dt
        self.collision('vertical')

    def get_direction(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]

        self.direction.y += keys[pygame.K_SPACE] * -3

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                        self.rect.right = sprite.rect.left
                    elif self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
                        self.rect.left = sprite.rect.right
                else:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
                        self.rect.bottom = sprite.rect.top
                    elif self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                        self.rect.top = sprite.rect.bottom



    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.get_direction()
        self.move(dt)
        