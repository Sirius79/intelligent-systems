import pygame
import random
from random import randint
import math
import numpy as np
import matplotlib.pyplot as plt
import time
import itertools
from collections import defaultdict

'''
    map:
    xxxxxxxxxxxx
    x...bpbg.twx
    x....bgdg.tx
    x...bpbg...x
    x....b.b...x
    x...b.bpb..x
    x..bpb.bpb.x
    x.bpb.bpb..x
    x..b...b...x
    x.bpb.bpb..x
    xs.bpb.b...x
    xxxxxxxxxxxx

    x = wall
    s = start
    d = destination
    b = breeze
    p = pit
    g = glitter
    t = stench
    w = wumpus

'''
white = (255, 255, 255)
black = (0, 0, 0)

class Environment(object):

    def __init__(self, width=720, height=540):
        '''
            Initialize pygame, window, background
            observation: (stench, breeze, glitter, bump, scream)
            action: (left, right, up, down, shoot)
        '''
        pygame.init()
        logo = pygame.image.load('wumpus.jpg')
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Wumpus World")
        self.map = list("...bpbg.tw....bgdg.t...bpbg.......b.b......b.bpb....bpb.bpb..bpb.bpb....b...b....bpb.bpb..s.bpb.b...")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(white)
        self.spritey = 461
        self.spritex = 11
        self.wumpus = 1 # live wumpus
        self.arrow = 1 # arrow in quiver
        self.agent_pos = 90
        self.done = 0
        self.action_space = [0,1,2,3,4]
        

    def draw_grid(self):

        # draw horizontal lines of the grid
        pygame.draw.line(self.background, black, (10, 10), (510, 10))
        pygame.draw.line(self.background, black, (10, 60), (510, 60))
        pygame.draw.line(self.background, black, (10, 110), (510, 110))
        pygame.draw.line(self.background, black, (10, 160), (510, 160))
        pygame.draw.line(self.background, black, (10, 210), (510, 210))
        pygame.draw.line(self.background, black, (10, 260), (510, 260))
        pygame.draw.line(self.background, black, (10, 310), (510, 310))
        pygame.draw.line(self.background, black, (10, 360), (510, 360))
        pygame.draw.line(self.background, black, (10, 410), (510, 410))
        pygame.draw.line(self.background, black, (10, 460), (510, 460))
        pygame.draw.line(self.background, black, (10, 510), (510, 510))

        # draw vertical lines of the grid
        pygame.draw.line(self.background, black, (10, 10), (10, 510))
        pygame.draw.line(self.background, black, (60, 10), (60, 510))
        pygame.draw.line(self.background, black, (110, 10), (110, 510))
        pygame.draw.line(self.background, black, (160, 10), (160, 510))
        pygame.draw.line(self.background, black, (210, 10), (210, 510))
        pygame.draw.line(self.background, black, (260, 10), (260, 510))
        pygame.draw.line(self.background, black, (310, 10), (310, 510))
        pygame.draw.line(self.background, black, (360, 10), (360, 510))
        pygame.draw.line(self.background, black, (410, 10), (410, 510))
        pygame.draw.line(self.background, black, (460, 10), (460, 510))
        pygame.draw.line(self.background, black, (510, 10), (510, 510))

    def draw_actor(self, x, y):
        img = pygame.image.load("player.gif")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_pit(self, x, y):
        img = pygame.image.load("pit.gif")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_breeze(self, x, y):
        img = pygame.image.load("breeze.jpeg")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_glitter(self, x, y):
        img = pygame.image.load("glitter.jpg")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_dest(self, x, y):
        img = pygame.image.load("gold.jpg")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_stench(self, x, y):
        img = pygame.image.load("stench.jpg")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_wumpus(self, x, y):
        img = pygame.image.load("wumpus.jpg")
        img = pygame.transform.scale(img, (48, 48))
        self.background.blit(img, [x, y])

    def draw_blank(self, x, y):
        pygame.draw.rect(self.background,white,(x,y,48,48))

    def draw_map(self):
        x = 11
        y = 11
        count = 0
        for i in self.map:
            if i == 'd':
                self.draw_dest(x, y)
            elif i == 'b':
                self.draw_breeze(x, y)
            elif i == 'p':
                self.draw_pit(x, y)
            elif i == 'g':
                self.draw_glitter(x, y)
            elif i == 't':
                self.draw_stench(x, y)
            elif i == 'w':
                self.draw_wumpus(x, y)
            else:
                self.draw_blank(x,y)
            count += 1
            x += 50
            if count == 10:
                x = 11
                y += 50
                count = 0
                
    def generate_state(self, pos):
        '''
            returns the state corresponding the tile position
        '''
        # get the tile at position
        tile = self.map[pos]
        if tile == 'b':
            return [0,1,0,0,0]
        elif tile == 'g':
            return [0,0,1,0,0]
        elif tile == 't':
            return [1,0,0,0,0]
        elif tile == '.' or tile == 's':
            return [0,0,0,0,0]
        elif tile == 'p':
            return [1,1,1,1,1]
        elif tile == 'w' and self.wumpus:
            return [1,1,1,1,1]
        elif tile == 'w':
            return [0,0,0,0,0]
        elif tile == 'd':
            return [10,10,10,10,10]

    def movement(self, action):
        '''
            render movement on taking action
        '''
        # move left
        if action == 0:
            # rendering movement
            if not self.spritex <=11:
                self.spritex -= 50
                self.agent_pos -= 1
                if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                    self.reset()
                    return
            else:
                return
        # move right
        elif action == 1:
            if not self.spritex >=460:
                self.spritex += 50
                self.agent_pos += 1
                if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                    self.reset()
                    return
            else:
                return
        # move up
        elif action == 2:
            if not self.spritey <=11:
                self.spritey -= 50
                self.agent_pos -= 10
                if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                    self.reset()
                    return
            else:
                return 
        # move down
        elif action == 3:
            if not self.spritey >= 460:
                self.spritey += 50
                self.agent_pos += 10
                if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                    self.reset()
                    return
            else:
                return

    def step(self, action):
        '''
            return next_state, reward, done
        '''
        if action == 0:
            # move left
            if int(str(self.agent_pos)[-1]) > 0:
                # update position if possible
                self.agent_pos -= 1
            else:
                # bumped
                _ = self.reset()
                return [0,0,0,1,0], -1, 0
            observation = self.generate_state(self.agent_pos)
            if observation == [1,1,1,1,1]:
                # encountered live wumpus or pit
                _ = self.reset()
                return observation, -1000, 1
            elif observation == [-1,-1,-1,-1,-1]:
                # reached destination/gold
                _ = self.reset()
                return observation, 1000, 1
            else:
                # take normal step
                return observation, -1, 0
            
        elif action == 1:
            # move right
            if int(str(self.agent_pos)[-1]) < 9:
                # update position if possible
                self.agent_pos += 1
            else:
                # bumped
                _ = self.reset()
                return [0,0,0,1,0], -1, 0
            observation = self.generate_state(self.agent_pos)
            if observation == [1,1,1,1,1]:
                # encountered live wumpus or pit
                _ = self.reset()
                return observation, -1000, 1
            elif observation == [-1,-1,-1,-1,-1]:
                # reached destination/gold
                _ = self.reset()
                return observation, 1000, 1
            else:
                # take normal step
                return observation, -1, 0
            
        elif action == 2:
            # move up
            if self.agent_pos >= 10:
                # update position if possible
                self.agent_pos -= 10
            else:
                # bumped
                _ = self.reset()
                return [0,0,0,1,0], -1, 0
            observation = self.generate_state(self.agent_pos)
            if observation == [1,1,1,1,1]:
                # encountered live wumpus or pit
                _ = self.reset()
                return observation, -1000, 1
            elif observation == [-1,-1,-1,-1,-1]:
                # reached destination/gold
                _ = self.reset()
                return observation, 1000, 1
            else:
                # take normal step
                return observation, -1, 0
            
        elif action == 3:
            # move down
            if self.agent_pos <= 89:
                # update position if possible
                self.agent_pos += 10
            else:
                # bumped
                _ = self.reset()
                return [0,0,0,1,0], -1, 0
            observation = self.generate_state(self.agent_pos)
            if observation == [1,1,1,1,1]:
                # encountered live wumpus or pit
                _ = self.reset()
                return observation, -1000, 1
            elif observation == [-1,-1,-1,-1,-1]:
                # reached destination/gold
                _ = self.reset()
                return observation, 1000, 1
            else:
                # take normal step
                return observation, -1, 0
            
        elif action == 4:
            # shoot
            if self.arrow:
                # if arrow in quiver
                self.arrow = 0
                if self.generate_state(self.agent_pos+1) == [1,1,1,1,1] or self.generate_state(self.agent_pos-10) == [1,1,1,1,1]:
                    # if live wumpus if near
                    return [1,0,0,0,1], -10, 0
                else:
                    return self.generate_state(self.agent_pos), -10, 0
            else:
                return self.generate_state(self.agent_pos), -1, 0
      

    def reset(self):
        self.agent_pos = 90
        self.spritey = 461
        self.spritex = 11
        self.wumpus = 1
        self.arrow = 1
        return [0,0,0,0,0]

    
    def run(self):
        '''
            Main loop
        '''
        # variable to control main loop
        running = True

        #initial state
        state = self.generate_state(self.agent_pos)

        # main loop
        while running:
            # event handling from event queue
            self.draw_grid()
            self.draw_map()
            self.draw_actor(self.spritex, self.spritey)
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
            probs = policy[tuple(state)] / policy[tuple(state)].sum()
            action = np.random.choice(5, 1, p=probs)[0]
            print(state, probs, action)
            self.movement(self.action_space[action])
            state,_,_ = self.step(action)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # user presses escape key
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_LEFT:
                        if not self.spritex <=11:
                            self.spritex -= 50
                            self.agent_pos -= 1
                            if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                                self.reset()
                        else:
                            print([0,0,0,1,0])
                    elif event.key == pygame.K_RIGHT:
                        if not self.spritex >=460:
                            self.spritex += 50
                            self.agent_pos += 1
                            if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                                self.reset()
                        else:
                            print([0,0,0,1,0])
                    elif event.key == pygame.K_UP:
                        if not self.spritey <=11:
                            self.spritey -= 50
                            self.agent_pos -= 10
                            if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                                self.reset()
                        else:
                            print([0,0,0,1,0])
                    elif event.key == pygame.K_DOWN:
                        if not self.spritey >= 460:
                            self.spritey += 50
                            self.agent_pos += 10
                            if self.generate_state(self.agent_pos) == [1,1,1,1,1]:
                                self.reset()
                        else:
                            print([0,0,0,1,0])

            pygame.display.update()

env = Environment()

policy = {(0, 0, 0, 0, 0): np.array([4962, 3980, 4094, 4338, 3748]),
          (1, 1, 0, 1, 0): np.array([5044, 4143, 4882, 5561, 4037]),
          (1, 1, 0, 0, 1): np.array([2923, 4777, 3152, 5206, 6184]),
          (0, 0, 1, 1, 1): np.array([3013, 5621, 6235, 6119, 4042]),
          (1, 0, 1, 1, 0): np.array([4571, 4127, 4150, 5899, 3500]),
          (1, 0, 1, 0, 0): np.array([3544, 4545, 6070, 4473, 5334]),
          (0, 0, 1, 1, 0): np.array([4152, 5239, 3178, 3375, 3796]),
          (1, 0, 0, 1, 1): np.array([3686, 3772, 3869, 4263, 3741]),
          (0, 1, 0, 1, 0): np.array([4904, 4702, 3011, 4433, 3692]),
          (1, 1, 0, 1, 1): np.array([3517, 5904, 4059, 3891, 4258]),
          (1, 0, 0, 0, 1): np.array([2757, 4701, 5375, 4335, 5193]),
          (0, 1, 1, 1, 1): np.array([6221, 4326, 4345, 6279, 5728]),
          (0, 1, 0, 0, 1): np.array([2482, 3494, 3986, 3541, 2971]),
          (1, 0, 1, 0, 1): np.array([4447, 3895, 5800, 2978, 3923]),
          (1, 1, 1, 1, 0): np.array([3200, 5191, 5119, 5758, 4878]),
          (1, 0, 1, 1, 1): np.array([2141, 5157, 3076, 3995, 5675]),
          (0, 0, 0, 1, 0): np.array([4244, 5294, 3600, 2870, 4619]),
          (1, 0, 0, 0, 0): np.array([5369, 3228, 5558, 4385, 5348]),
          (0, 1, 0, 1, 1): np.array([4862, 6129, 4250, 4897, 5020]),
          (0, 0, 0, 0, 1): np.array([3639, 5988, 4249, 4008, 3762]),
          (1, 1, 0, 0, 0): np.array([2863, 4114, 4529, 4692, 5379]),
          (1, 0, 0, 1, 0): np.array([4542, 4240, 3759, 4087, 4045]),
          (0, 0, 1, 0, 0): np.array([5096, 4522, 6201, 2011, 2988]),
          (0, 1, 1, 1, 0): np.array([5267, 4048, 3041, 4688, 4238]),
          (0, 0, 0, 1, 1): np.array([6316, 2809, 5275, 4189, 5167]),
          (1, 1, 1, 0, 1): np.array([3190, 4649, 6308, 5155, 4508]),
          (1, 1, 1, 1, 1): np.array([4790, 2727, 5252, 4239, 3647]),
          (1, 1, 1, 0, 0): np.array([5413, 5106, 4137, 5223, 5269]),
          (0, 0, 1, 0, 1): np.array([2864, 3881, 2993, 4085, 2099]),
          (0, 1, 0, 0, 0): np.array([5101, 4836, 3663, 3955, 4287]),
          (0, 1, 1, 0, 1): np.array([5978, 4097, 4265, 5833, 2809]),
          (0, 1, 1, 0, 0): np.array([3531, 4699, 5186, 5627, 4825])}

env.run()
