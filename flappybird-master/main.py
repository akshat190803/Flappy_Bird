import pygame
from pygame.locals import *
import random
pygame.init()

clock = pygame.time.Clock()    
fps = 60                              

screen_width  = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

#define font and color
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (0,0,0)

#game variables
scroll = 0                   
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500        #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

bg = pygame.image.load('bg.png')
ground_image = pygame.image.load('ground.png')
button_image = pygame.image.load('restart.png')

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def reset_game():                       #function to reset the game
    pipe_group.empty()                  #firstly, clear the pipes
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height/2)
    return 0


class bird(pygame.sprite.Sprite):                   
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)      
        self.images = []                                       
        self.index = 0                                         
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]      
        self.rect = self.image.get_rect()                    
        self.rect.center = [x,y]   
        self.velocity = 0                            
        self.clicked = True                     

    def update(self):

        if flying:                                   
        #gravity
            self.velocity += 0.5                     
            if self.rect.bottom < 768:               
                self.rect.y += int(self.velocity)    
            if self.velocity > 8:                    
               self.velocity = 8
        
        if game_over == False:                      
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked:
                self.velocity = -8
                self.clicked = False
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = True

            #handle the animation
            self.counter += 1
            flap_cooldown = 15
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class pipe(pygame.sprite.Sprite):
    def __init__(self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x,y + int(pipe_gap/2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:            #once a pipe moves out of screen, we delete it from memory using kill
            self.kill() 

class button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    def draw(self):

        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse is on the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw the button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action



bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = bird(100, int(screen_height/2))

bird_group.add(flappy)       

#creating an instance of a button
restart = button(screen_width//2 - 45, 175, button_image )

run = True
while run:
    clock.tick(fps)      
    screen.blit(bg, (0,0))

    bird_group.draw(screen)
    bird_group.update() 
    pipe_group.draw(screen)

    if flying == True and game_over == False:
        pipe_group.update() 

    screen.blit(ground_image, (scroll,768))

	#check the score 
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
                
    draw_text(str(score), font, white, int(screen_width / 2), 100)

    #look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False
    
    if game_over == False and flying == True:

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = pipe(screen_width, int(screen_height/2) + pipe_height,1)      #creating an instance of pipe for bottom
            top_pipe = pipe(screen_width, int(screen_height/2) + pipe_height,-1)     #creating an instance of pipe for top
            pipe_group.add(btm_pipe)                                   #adding the btm_pipe to the pipe group        
            pipe_group.add(top_pipe)                                   #adding the top_pipe
            last_pipe = time_now
            
        scroll -= scroll_speed
        if abs(scroll) > 35:
            scroll = 0

    #check for game-over
    if game_over == True:
        if button.draw(restart) == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:   
            flying = True
    pygame.display.update()
pygame.quit()


