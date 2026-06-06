from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = WINDOW_WIDTH / 2 - target_pos[0]
        self.offset.y = WINDOW_HEIGHT / 2 - target_pos[1]

        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        objects_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]

        for layer in [ground_sprites, objects_sprites]:
            for sprite in sorted(layer, key=lambda x: x.rect.centery):
                self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)