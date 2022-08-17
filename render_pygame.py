import pygame
from maplib import Mapview

class PygameMapview(Mapview):
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((self.width, self.height))

    def draw_tile(self, x, y, path):
        sfc = pygame.image.load(path)
        self.scr.blit(sfc, (x,y))

    def draw_circle(self, x, y, radius, color):
        pygame.draw.circle(self.scr, color, (x, y), radius)

    def flush(self):
        pygame.display.flip()


m = PygameMapview()

m.draw_map()

running = True
clock = pygame.time.Clock()
while running:
    clock.tick(5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                m.move_up(True)
            elif event.key == pygame.K_a:
                m.move_left(True)
            elif event.key == pygame.K_s:
                m.move_down(True)
            elif event.key == pygame.K_d:
                m.move_right(True)
            elif event.key == pygame.K_e:
                m.zoom_in(True)
            elif event.key == pygame.K_q:
                m.zoom_out(True)
    m.draw_map()
pygame.quit()