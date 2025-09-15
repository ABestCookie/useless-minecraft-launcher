import pygame, sys, platform


white=(255, 255, 255)
black=(0, 0, 0)
def main():
    pygame.init()
    pygame.display.set_caption("wewwewe")
    screen=pygame.display.set_mode((800, 600))
    clock=pygame.time.Clock()
    font=pygame.font.Font(None, 80)
    tmr=0

    while True:
        tmr += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        txt=font.render(str(tmr), True, white)
        screen.fill(black)
        screen.blit(txt, [10, 0])
        pygame.display.update()
        clock.tick(10)

if __name__ == '__main__':
    main()
