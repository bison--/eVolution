import pygame
from pygame.surface import Surface
import config
from local_modules.BaseModule import BaseModule
from local_modules.BindText import BindText
import local_modules.HamsterModule as HamsterModule
from pygameFpsCounter_bak import FpsCounterSlim


class GameMaster:

    def __init__(self):
        self.screen = None  # type: Surface or None
        self.time_passed = 0
        self.game_is_running = True
        self.max_fps = config.MAX_FPS
        self.all_modules = []  # type: list[BaseModule]

    def import_modules(self):
        screen_rect = self.screen.get_rect()
        hamster_module = HamsterModule.HamsterModule(self.screen)
        self.all_modules.append(hamster_module)

        generation_text2 = BindText(self.screen)
        generation_text2.position = (10, config.SCREEN_HEIGHT - generation_text2.font_size)
        generation_text2.bind_object(hamster_module, 'round_ticks', False)
        self.all_modules.append(generation_text2)

        generation_text = BindText(self.screen)
        generation_text.position = (10, config.SCREEN_HEIGHT - generation_text.font_size * 2)
        generation_text.bind_object(hamster_module, 'generation', False)
        self.all_modules.append(generation_text)

    def run(self):
        pygame.init()
        pygame.display.set_caption("Graphics Test")

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
        clock = pygame.time.Clock()

        fps = FpsCounterSlim.FpsCounterSlim(self.screen)
        fps.color = (38, 127, 0)

        self.import_modules()

        while self.game_is_running:
            # limit frame speed to fps
            self.time_passed = clock.tick(self.max_fps)

            self.screen.fill((155, 155, 155))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_is_running = False
                    elif event.key == pygame.K_c:
                        for module in self.all_modules:
                            module.calculate()
                    elif event.key == pygame.K_r:
                        self.all_modules.clear()
                        self.import_modules()
                    else:
                        for module in self.all_modules:
                            module.handle_input(event)

            #pygame.draw.rect(
            #    self.screen,
            #    (3, 3, 3),
            #    pygame.rect.Rect(0, 0, config.SCREEN_WIDTH, 100)
            #)
            #img = pygame.image.load('assets/images/cybergrid_sky_800.png')
            #self.screen.blit(img, img.get_rect())

            for module in self.all_modules:
                module.frame()
                module.timer()
                module.draw()

            fps.render_fps()
            # final draw
            pygame.display.flip()
