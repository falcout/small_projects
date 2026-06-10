from settings import *

class AttackAnimationSprite(pygame.sprite.Sprite):
    def __init__(self, target, frames, groups):
        super().__init__(groups)
        self.frames, self.frames_index = frames, 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center=target.rect.center)

    def update(self, dt):
        self.frames_index += 5 * dt
        if self.frames_index < len(self.frames):
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill()