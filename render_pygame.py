import pygame
from maplib import Mapview
from mvt import VectorMixin
from style_rgb import StyleMixin

class PygameMapview(Mapview):
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont("sans-serif", 18)

    def draw_tile(self, x, y, path):
        sfc = pygame.image.load(path)
        self.scr.blit(sfc, (x,y))

    def draw_point(self, x, y, color, size):
        pygame.draw.circle(self.scr, color, (x, y), size)
    
    def draw_text(self, x, y, text, color, size):
        self.scr.blit(self.font.render(text, True, color), (x, y))

    def draw_line(self, x1, y1, x2, y2, color, size):
        pygame.draw.line(self.scr, color, (x1, y1), (x2, y2), size)
    
    def draw_polygon(self, vertices, holes, color, size):
        points = []
        for i in range(0, holes[0], 2):
            points.append((vertices[i], vertices[i+1]))
        pygame.draw.polygon(self.scr, color, points, size)

    def draw_fill(self, color):
        self.scr.fill(color)

    def flush(self):
        pygame.display.flip()

class PygameVectorMapview(VectorMixin, StyleMixin, PygameMapview):
    urltmpl = "https://api.maptiler.com/tiles/v3-openmaptiles/{z}/{x}/{y}.pbf?key=dMxOGgHTyghLg71Ok4wG"
    pathtmpl = "vtiles/{z}/{x}/{y}.pbf"
    zoom = 14
    tilesize = 4096


m = PygameVectorMapview()
# m = PygameMapview()

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
    # break
pygame.quit()