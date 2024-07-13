import asyncio
import pygame as pg
import sys
import math
import time
import random
from typing import List
from settings import *

#from gpiozero import Button
#Up          = Button(26)
#Left        = Button(16)
#Down        = Button(6)
#Right       = Button(5)
#Triangle    = Button(25)
#Green       = Button(24)
#Red         = Button(23)

async def main():
    clock = pg.time.Clock()
    
    while True:
        clock.tick(FPS)
        game.run()

        await asyncio.sleep(0)

class GameWindow(object):
    def __init__(self):
        
            #Define locals
        pg.init()
        self.display_surface = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.window_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.mode = 2 #Normal gameplay, 2 for intro trigger
        self.offroad = [0,0] #status, iterable
        self.ship_speed = 0
        self.konami_code_progress = [0,0,0,0,0,0,0,0,0,0] #Up, up, down, down, left, right, left, right, b, a
        self.konami_code_toggle = [0,0,0,0,0,0,0,0,0,0]

        self.dcamera_depth = 0

            #Set groups
        self.player_group = pg.sprite.Group()
        self.road_group = pg.sprite.Group()
        self.interior_group = pg.sprite.Group()
        self.scene_group = pg.sprite.Group()

            #Control booleans
        self.LEFT = False
        self.RIGHT = False
        self.UP = False
        self.DOWN = False
        self.GO = False
        self.STOP = False
        self.EXIT = False

        self.skyway = Skyway(self)
        Ship_Interior(self, 'ShipHull')
        Ship_Interior(self, 'DPad')
        Ship_Interior(self, 'StopGo')
        Ship_Interior(self, 'TurbineIcon')
        Ship_Interior(self, 'TurbineIcon_2')
        Ship_Interior(self, 'POS_NUM_1')
        Ship_Interior(self, 'POS_NUM_2')
        Ship_Interior(self, 'POS_TXT')
        Cutscene(self)

        pg.mixer.music.load('music/The Race.mp3')
        pg.mixer.music.play(-1)


    def controls(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.LEFT = True
        else:
            self.LEFT = False
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.RIGHT = True
        else:
            self.RIGHT = False
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.UP = True
        else:
            self.UP = False
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.DOWN = True
        else:
            self.DOWN = False
        if keys[pg.K_c] or keys[pg.K_j]:
            self.STOP = True
        else:
            self.STOP = False
        if keys[pg.K_x] or keys[pg.K_i]:
            self.GO = True
        else:
            self.GO = False
        if keys[pg.K_z] or keys[pg.K_u]:
            self.EXIT = True
        else:
            self.EXIT = False

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
        #pg.display.set_caption(f'{self.clock.get_fps(): .1f}') #Display the FPS as the caption
    
    def cutscene(self):

        self.scene_group.update()

        self.display_surface.fill(BG_COLOR)
        self.scene_group.draw(self.display_surface)
        pg.display.flip()

    def eyes_on_road(self):

        self.road_group.update()
        self.interior_group.update()

        #self.window_surface.fill(BG_COLOR)
        self.display_surface.fill(BG_COLOR)
        self.road_group.draw(self.display_surface)

        #self.display_surface.blit(self.window_surface,(DISPLAY_WIDTH/2-WINDOW_WIDTH/2,DISPLAY_HEIGHT/2-WINDOW_HEIGHT/2))
        self.interior_group.draw(self.display_surface)

        pg.display.flip()

    def run(self):

        self.check_events()
        self.controls()

        if self.mode == 1:
            self.eyes_on_road()
        elif self.mode > 1:
            self.cutscene()

class Line:
    def __init__(self, app, i):

            #Define locals
        self.app = app
        self.i = i
        self.x = self.y = self.z = 0.0
        self.X = self.Y = self.W = 0.0
        self.scale = 0.0
        self.curve = 0.0
        self.spriteX = 0.0
        self.clip = 0.0
        self.sprite: pg.Surface = None
        self.sprite_rect: pg.Rect = None
        self.grass_color: pg.Color = "black"
        self.rumble_color: pg.Color = "black"
        self.road_color: pg.Color = "black"

            #Abnormal Locals
        self.dy = 0.0 #Slope of lines
        self.dx = 0.0 #Slope of lines
        self.draw_grass = False
        self.grass_tag = 0
        self.height_offset = 1

    def project(self, camX: int, camY: int, camZ: int):
            #Pseudo 3D effect
        self.scale = (CAMERA_DEPTH + self.app.dcamera_depth) / (self.z - camZ)
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * ROAD_WIDTH * WINDOW_WIDTH / 2

    def drawSprite(self, draw_surface: pg.Surface):
        if self.sprite is None:
            return  #For lines without images assigned
        
        w = self.sprite.get_width()
        h = self.sprite.get_height()
        destX = self.X + self.scale * self.spriteX * WINDOW_WIDTH / 2
        destY = self.Y + 4
        destW = w * self.W / 20
        destH = h * self.W / 20

        destX += destW * self.spriteX
        destY += destH * -1 * self.height_offset

        #kill image if it lags (evil)
        if destW > w*12:
            return

        scaled_sprite = pg.transform.scale(self.sprite, (destW, destH))
        crop_surface = scaled_sprite
        draw_surface.blit(crop_surface, (destX, destY))

class Skyway(pg.sprite.Sprite):
    def __init__(self, app):
        
            #Define locals
        self.app = app
        self.group = app.road_group
        self.road_angle = 0
        self.road_segment = 0
        self.tilt = 0
        self.reset = False

        super().__init__(self.group)

            #Decoy image
        self.size = vec2([WINDOW_WIDTH,WINDOW_HEIGHT])
        self.window_surface = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.window_surface.get_rect(center = vec2(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))

            #Background Mess
        self.background_image = pg.image.load("images/SpaceSky.png").convert_alpha()
        self.background_image = pg.transform.scale(
            self.background_image, (self.background_image.get_width()*2, self.background_image.get_height()*2)
        )
        self.background_surface = pg.Surface(
            (self.background_image.get_width() * 3, self.background_image.get_height())
        )
        self.background_surface.blit(self.background_image, (0, 0))
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width(), 0)
        )
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width() * 2, 0)
        )
        self.background_rect = self.background_surface.get_rect(
            topleft=(-self.background_image.get_width(), -50)
        )
        self.window_surface.blit(self.background_surface, self.background_rect)

        if True: #Event backgrounds (If statement for closure)
            self.background_image_1 = pg.image.load("images/EarthSky.png").convert_alpha()
            self.background_image_1 = pg.transform.scale(
                self.background_image_1, (self.background_image_1.get_width()*2, self.background_image_1.get_height()*2)
            )
            self.background_surface_1 = pg.Surface(
                (self.background_image_1.get_width() * 3, self.background_image_1.get_height())
            )
            self.background_surface_1.blit(self.background_image_1, (0, 0))
            self.background_surface_1.blit(
                self.background_image_1, (self.background_image_1.get_width(), 0)
            )
            self.background_surface_1.blit(
                self.background_image_1, (self.background_image_1.get_width() * 2, 0)
            )
            self.background_rect_1 = self.background_surface_1.get_rect(
                topleft=(-self.background_image_1.get_width(), -50)
            )
            self.window_surface.blit(self.background_surface_1, self.background_rect_1)

        if True: #Caturn backgrounds (If statement for closure)
            self.caturn_image_1 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_1.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_2 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_2.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_3 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_3.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_4 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_4.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_5 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_5.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_6 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_6.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_7 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_7.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_8 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_8.png").convert_alpha(), (800*2, 480*2))
            self.caturn_image_100 = pg.transform.scale(pg.image.load("images/SpaceSky_Caturn_100.png").convert_alpha(), (800*2, 480*2))

            self.caturn_rect = self.caturn_image_6.get_rect(center = (DISPLAY_WIDTH/2,DISPLAY_HEIGHT/2))


        self.sprites: List[pg.Surface] = []
        for i in range(1, 100): #Grab all billboard images from the files
            try:
                self.sprites.append(pg.image.load(f"images/{i}.png").convert_alpha())
            except:
                self.sprites.append(pg.image.load(f"images/1.png").convert_alpha())

            #Terrain generation
            #Grab constants
        self.CONST_intensity_y = INTENSITY_Y
        self.CONST_correction = CORRECTION
        self.CONST_damper = DAMPER
        self.CONST_upper_bound = UPPER_BOUND
        self.CONST_lower_bound = LOWER_BOUND
        self.CONST_bound_pull = BOUND_PULL
        self.CONST_entropy_y = ENTROPY_Y
        self.CONST_bias_y = BIAS_Y
        self.CONST_intensity_x = INTENSITY_X
        self.CONST_entropy_x = ENTROPY_X
        self.CONST_bias_x = BIAS_X
            #Terrain Y
        self.speed_float = 0
        self.line_y = 0
        self.line_dy = 0
        self.line_ddy = 0
        self.line_dddy = 0
        self.corrections = 0
            #Terrain X
        self.line_x = 0
        self.line_dx = 0
        self.line_ddx = 0
            #Cosmetic
        self.draw_grass = False
        self.grass_tag = 0

            #Events
            #0: Space
            #1: Earth (Road color change, scenery, flat, ramp up at the end)

        self.events = [0, 0, 0] #Event type, iterable timer (Like self.busy[0][0]), time since event
        self.events = [1, 1000, -1000] #Prime first event
        self.event_diceroll = 0
        self.player_incline = 0
        self.lines: List[Line] = []

        for i in range(ROAD_TRIP): #Road trip is the length of the track

            line = Line(self.app,i)

            line.z = (
                i * SEGMENT_LENGTH + 0.00001
            )  # adding a small value avoids Line.project() errors

            self.grass_tag = 0

                #Handle event timers
            if self.events[1] < 0:
                self.events[0] = 0
            else:
                self.events[1] -= 1

            if i == 1000:
                self.events = [2, 500, -1000]
            
            if i == 1500:
                self.events = [3, 500, -1000]

            if i == (ROAD_TRIP - 4000):
                self.events = [96, 1000, -1000]
            
            if i == (ROAD_TRIP - 3000):
                self.events = [97, 200, -1000]
            
            if i == (ROAD_TRIP - 2800):
                self.events = [98, 2800, -2800]
            
            if self.events[2] > 2000: #Start thinkin' about a new event. Hmmmm
                if int(random.random()*100) == 0:
                    self.event_diceroll = int(random.random()*3)

                    if self.event_diceroll == 0:
                        self.events = [4, EVENT_LENGTH_4, -EVENT_LENGTH_4] #Space station
                    elif self.event_diceroll == 1:
                        self.events = [5, EVENT_LENGTH_5, -EVENT_LENGTH_5] #Asteroid belt
                    elif self.event_diceroll == 2:
                        self.events = [6, EVENT_LENGTH_6, -EVENT_LENGTH_6] #Asteroid belt
            
            self.events[2] += 1

            # Event Attributes
            if self.events[0] == 0:

                self.draw_grass = False

                grass_color = light_grass if (i // 3) % 2 else dark_grass
                rumble_color = white_rumble if (i // 3) % 3 else black_rumble
                road_color = light_road if (i // 3) % 2 else dark_road

                self.CONST_intensity_y = INTENSITY_Y
                self.CONST_correction = CORRECTION
                self.CONST_damper = DAMPER
                self.CONST_upper_bound = UPPER_BOUND
                self.CONST_lower_bound = LOWER_BOUND
                self.CONST_bound_pull = BOUND_PULL
                self.CONST_entropy_y = ENTROPY_Y
                self.CONST_bias_y = BIAS_Y
                self.CONST_intensity_x = INTENSITY_X
                self.CONST_entropy_x = ENTROPY_X
                self.CONST_bias_x = BIAS_X

            elif self.events[0] == 1:

                self.draw_grass = True

                grass_color = light_grass_1 if (i // 6) % 2 else dark_grass_1
                rumble_color = white_rumble_1 if (i // 3) % 3 else black_rumble_1
                road_color = light_road_1 if (i // 3) % 2 else dark_road_1

                self.CONST_intensity_y = INTENSITY_Y_1
                self.CONST_correction = CORRECTION_1
                self.CONST_damper = DAMPER_1
                self.CONST_upper_bound = UPPER_BOUND_1
                self.CONST_lower_bound = LOWER_BOUND_1
                self.CONST_bound_pull = BOUND_PULL_1
                self.CONST_entropy_y = ENTROPY_Y_1
                self.CONST_bias_y = BIAS_Y_1
                self.CONST_intensity_x = INTENSITY_X_1
                self.CONST_entropy_x = ENTROPY_X_1
                self.CONST_bias_x = BIAS_X
            
            elif self.events[0] == 2: #Exiting earth ramp

                self.draw_grass = False

                grass_color = light_grass_2 if (i // 3) % 2 else dark_grass_2
                rumble_color = white_rumble_2 if (i // 3) % 3 else black_rumble_2
                road_color = light_road_2 if (i // 3) % 2 else dark_road_2

                self.CONST_intensity_y = INTENSITY_Y_2
                self.CONST_correction = CORRECTION_2
                self.CONST_damper = DAMPER_2
                self.CONST_upper_bound = UPPER_BOUND_2
                self.CONST_lower_bound = LOWER_BOUND_2
                self.CONST_bound_pull = BOUND_PULL_2
                self.CONST_entropy_y = ENTROPY_Y_2
                self.CONST_bias_y = BIAS_Y_2
                self.CONST_intensity_x = INTENSITY_X_2
                self.CONST_entropy_x = ENTROPY_X_2
                self.CONST_bias_x = BIAS_X_2
            
            elif self.events[0] == 3:

                self.draw_grass = False

                grass_color = light_grass_3 if (i // 3) % 2 else dark_grass_3
                rumble_color = white_rumble_3 if (i // 3) % 3 else black_rumble_3
                road_color = light_road_3 if (i // 3) % 2 else dark_road_3

                self.CONST_intensity_y = INTENSITY_Y_3
                self.CONST_correction = CORRECTION_3
                self.CONST_damper = DAMPER_3
                self.CONST_upper_bound = UPPER_BOUND_3
                self.CONST_lower_bound = LOWER_BOUND_3
                self.CONST_bound_pull = BOUND_PULL_3
                self.CONST_entropy_y = ENTROPY_Y_3
                self.CONST_bias_y = BIAS_Y_3
                self.CONST_intensity_x = INTENSITY_X_3
                self.CONST_entropy_x = ENTROPY_X_3
                self.CONST_bias_x = BIAS_X_3

            elif self.events[0] == 4:

                self.draw_grass = True
                self.grass_tag = 4

                grass_color = light_grass_4 if (i // 6) % 2 else dark_grass_4
                rumble_color = white_rumble_4 if (i // 3) % 3 else black_rumble_4
                road_color = light_road_4 if (i // 3) % 2 else dark_road_4

                self.CONST_intensity_y = INTENSITY_Y_4
                self.CONST_correction = CORRECTION_4
                self.CONST_damper = DAMPER_4
                self.CONST_upper_bound = UPPER_BOUND_4
                self.CONST_lower_bound = LOWER_BOUND_4
                self.CONST_bound_pull = BOUND_PULL_4
                self.CONST_entropy_y = ENTROPY_Y_4
                self.CONST_bias_y = BIAS_Y_4
                self.CONST_intensity_x = INTENSITY_X_4
                self.CONST_entropy_x = ENTROPY_X_4
                self.CONST_bias_x = BIAS_X_4

            elif self.events[0] == 5: #Asteroid belt

                self.draw_grass = False

                grass_color = light_grass_5 if (i // 3) % 2 else dark_grass_5
                rumble_color = white_rumble_5 if (i // 3) % 3 else black_rumble_5
                road_color = light_road_5 if (i // 3) % 2 else dark_road_5

                self.CONST_intensity_y = INTENSITY_Y_5
                self.CONST_correction = CORRECTION_5
                self.CONST_damper = DAMPER_5
                self.CONST_upper_bound = UPPER_BOUND_5
                self.CONST_lower_bound = LOWER_BOUND_5
                self.CONST_bound_pull = BOUND_PULL_5
                self.CONST_entropy_y = ENTROPY_Y_5
                self.CONST_bias_y = BIAS_Y_5
                self.CONST_intensity_x = INTENSITY_X_5
                self.CONST_entropy_x = ENTROPY_X_5
                self.CONST_bias_x = BIAS_X_5
            
            elif self.events[0] == 6: #Highway

                self.draw_grass = True
                self.grass_tag = 6

                grass_color = light_grass_6 if (i // 12) % 2 else dark_grass_6
                rumble_color = white_rumble_6 if (i // 3) % 3 else black_rumble_6
                road_color = light_road_6 if (i // 3) % 2 else dark_road_6

                self.CONST_intensity_y = INTENSITY_Y_6
                self.CONST_correction = CORRECTION_6
                self.CONST_damper = DAMPER_6
                self.CONST_upper_bound = UPPER_BOUND_6
                self.CONST_lower_bound = LOWER_BOUND_6
                self.CONST_bound_pull = BOUND_PULL_6
                self.CONST_entropy_y = ENTROPY_Y_6
                self.CONST_bias_y = BIAS_Y_6
                self.CONST_intensity_x = INTENSITY_X_6
                self.CONST_entropy_x = ENTROPY_X_6
                self.CONST_bias_x = BIAS_X_6
            
            elif self.events[0] == 96: #Enter Caturn Ramp start

                self.draw_grass = False

                grass_color = light_grass_96 if (i // 3) % 2 else dark_grass_96
                rumble_color = white_rumble_96 if (i // 3) % 3 else black_rumble_96
                road_color = light_road_96 if (i // 3) % 2 else dark_road_96

                self.CONST_intensity_y = INTENSITY_Y_96
                self.CONST_correction = CORRECTION_96
                self.CONST_damper = DAMPER_96
                self.CONST_upper_bound = UPPER_BOUND_96
                self.CONST_lower_bound = LOWER_BOUND_96
                self.CONST_bound_pull = BOUND_PULL_96
                self.CONST_entropy_y = ENTROPY_Y_96
                self.CONST_bias_y = BIAS_Y_96
                self.CONST_intensity_x = INTENSITY_X_96
                self.CONST_entropy_x = ENTROPY_X_96
                self.CONST_bias_x = BIAS_X_96
            
            elif self.events[0] == 97: #Enter Caturn Ramp end

                self.draw_grass = True

                grass_color = light_grass_97 if (i // 3) % 2 else dark_grass_97
                rumble_color = white_rumble_97 if (i // 3) % 3 else black_rumble_97
                road_color = light_road_97 if (i // 3) % 2 else dark_road_97

                self.CONST_intensity_y = INTENSITY_Y_97
                self.CONST_correction = CORRECTION_97
                self.CONST_damper = DAMPER_97
                self.CONST_upper_bound = UPPER_BOUND_97
                self.CONST_lower_bound = LOWER_BOUND_97
                self.CONST_bound_pull = BOUND_PULL_97
                self.CONST_entropy_y = ENTROPY_Y_97
                self.CONST_bias_y = BIAS_Y_97
                self.CONST_intensity_x = INTENSITY_X_97
                self.CONST_entropy_x = ENTROPY_X_97
                self.CONST_bias_x = BIAS_X_97
            
            elif self.events[0] == 98: #Caturn Flats

                self.draw_grass = True

                grass_color = light_grass_98 if (i // 3) % 2 else dark_grass_98
                rumble_color = white_rumble_98 if (i // 3) % 3 else black_rumble_98
                road_color = light_road_98 if (i // 3) % 2 else dark_road_98

                self.CONST_intensity_y = INTENSITY_Y_98
                self.CONST_correction = CORRECTION_98
                self.CONST_damper = DAMPER_98
                self.CONST_upper_bound = UPPER_BOUND_98
                self.CONST_lower_bound = LOWER_BOUND_98
                self.CONST_bound_pull = BOUND_PULL_98
                self.CONST_entropy_y = ENTROPY_Y_98
                self.CONST_bias_y = BIAS_Y_98
                self.CONST_intensity_x = INTENSITY_X_98
                self.CONST_entropy_x = ENTROPY_X_98
                self.CONST_bias_x = BIAS_X_98

            line.grass_color = grass_color
            line.rumble_color = rumble_color
            line.road_color = road_color

            if int(random.random() / self.CONST_entropy_y) == 1: #Introduce vertical randomness
                self.line_dddy = random.random()*self.CONST_intensity_y-(self.CONST_intensity_y/2)
            
            if self.line_y > self.CONST_upper_bound and self.line_dy > -1 or self.line_dy > self.CONST_damper:
                self.line_dy -= self.CONST_correction
                self.line_dddy = -1
                self.corrections += 1
            elif self.line_y < self.CONST_lower_bound and self.line_dy < 1 or self.line_dy < -self.CONST_damper:
                self.line_dy += self.CONST_correction
                self.line_dddy = 1
                self.corrections += 1

            self.line_ddy = (self.line_ddy + self.line_dddy)/2
            self.line_dy = (self.line_dy + self.line_ddy)/1 + self.CONST_bias_y

            line.dy = self.line_dy
            line.dx = self.line_x

            self.line_y = self.line_y + self.line_dy
            line.y = int(self.line_y)

            if int(random.random() / self.CONST_entropy_x) == 1: #Introduce horizontal randomness
                self.line_ddx = random.random()*self.CONST_intensity_x-(self.CONST_intensity_x/2)
            else:
                self.line_ddx = 0
            
            self.line_dx = (self.line_dx + self.line_ddx)/2
            self.line_x = (self.line_x + self.line_dx)/1.01
            
            line.curve = self.line_x
            line.draw_grass = self.draw_grass
            line.grass_tag = self.grass_tag


            # Sprites segments
            line.height_offset = 1

            if self.events[0] == 0: #Space sprites
                if i > 100 and int(random.random()*10) == 0:
                    line.spriteX = (random.random()*-10)-3
                    line.height_offset = (random.random()*6-1)
                    line.sprite = self.sprites[int(random.random()*4)]
                if i > 100 and int(random.random()*10) == 0:
                    line.spriteX = (random.random()*10)+3
                    line.height_offset = (random.random()*6-1)
                    line.sprite = self.sprites[int(random.random()*4)]

                if int(random.random()*10000) == 0:
                    line.spriteX = (random.random()*1)+0.1
                    line.height_offset = (random.random()*1-0.25)
                    line.sprite = self.sprites[4]
                
                if self.line_x > 2 and i % 20 == 0:
                    line.spriteX = -1.65
                    line.height_offset=0.9
                    line.sprite = self.sprites[10]
                
                if self.line_x < -2 and i % 20 == 0:
                    line.spriteX = 0.65
                    line.height_offset=0.9
                    line.sprite = self.sprites[11]
            
            elif self.events[0] == 1: #Earth sprites
                if int(random.random()*30) == 0:
                    line.spriteX = (random.random()*-5)-1.75
                    line.sprite = self.sprites[int(random.random()*2)+30]
                if int(random.random()*30) == 0:
                    line.spriteX = (random.random()*5)+0.1
                    line.sprite = self.sprites[int(random.random()*2)+30]
            
            elif self.events[0] == 2 or self.events[0] == 3: #Transitioning Earth sprites

                if i > 100 and int(random.random()*20) == 0:
                    line.spriteX = (random.random()*-7)
                    line.sprite = self.sprites[int(random.random()*1)+40]
                    line.height_offset = -0.25
                if i > 100 and int(random.random()*20) == 0:
                    line.spriteX = (random.random()*7)
                    line.sprite = self.sprites[int(random.random()*1)+40]
                    line.height_offset = -0.25
            
            elif self.events[0] == 4: #Space Station 1

                if int(random.random()*20) == 0:
                    line.spriteX = (random.random()*-2)-1.75
                    line.height_offset = 1
                    line.sprite = self.sprites[53]

                if self.events[1] > EVENT_LENGTH_4-7 and self.events[1] % 2 == 0:
                    line.spriteX = -0.49*(EVENT_LENGTH_4-self.events[1])-0.25
                    line.sprite = self.sprites[int(random.random()*3)+50]
                    line.height_offset = 0.035
                
                elif self.events[1] > EVENT_LENGTH_4-7 and self.events[1] % 2 == 1:
                    line.spriteX = 0.49*(EVENT_LENGTH_4-self.events[1])-0.25
                    line.sprite = self.sprites[int(random.random()*3)+50]
                    line.height_offset = 0.035
            
            elif self.events[0] == 5: #Asteroid Sprites
                if int(random.random()*20) == 0:
                    line.spriteX = (random.random()*-5)-1.75
                    line.height_offset = (random.random()*5)-2
                    line.sprite = self.sprites[int(random.random()*3)+60]
                if int(random.random()*20) == 0:
                    line.spriteX = (random.random()*5)+0.1
                    line.height_offset = (random.random()*5)-2
                    line.sprite = self.sprites[int(random.random()*3)+60]

            elif self.events[0] == 6: #Highway Sprites
                if int(random.random()*50) == 0:
                    line.spriteX = (random.random()*-5)-1.75
                    line.height_offset = (random.random()*3)
                    line.sprite = self.sprites[int(random.random()*3)+70]
                if int(random.random()*50) == 0:
                    line.spriteX = (random.random()*5)+0.1
                    line.height_offset = (random.random()*3)
                    line.sprite = self.sprites[int(random.random()*3)+70]
                
                if i % 200 == 0:
                    line.spriteX = -1.65+0.25
                    line.height_offset = 1
                    line.sprite = self.sprites[74]
                if i % 200 == 1:
                    line.spriteX = 0.65-0.25
                    line.height_offset = 1
                    line.sprite = self.sprites[75]

                if i % 80 == 0 and self.events[2] > -700:
                    line.spriteX = 0.65
                    line.height_offset = 1
                    line.sprite = self.sprites[73]
                if i % 80 == 1 and self.events[2] > -700:
                    line.spriteX = -1.65
                    line.height_offset = 1
                    line.sprite = self.sprites[73]

            elif self.events[0] == 98: #Caturn sprites (80 - 100)

                if self.events[2] < -1500:

                    if int(random.random()*40) == 0:
                        line.height_offset = 1
                        line.spriteX = (random.random()*-5)-1.75
                        line.sprite = self.sprites[int(random.random()*2)+80]
                    if int(random.random()*40) == 0:
                        line.height_offset = 1
                        line.spriteX = (random.random()*5)+0.5
                        line.sprite = self.sprites[int(random.random()*2)+80]
                
                elif self.events[2] == -1000:
                    line.height_offset = 1
                    line.spriteX = -0.5
                    line.sprite = self.sprites[89]
                else:

                    if int(random.random()*35) == 0:
                        line.height_offset = 1
                        line.spriteX = (random.random()*-5)-1.75
                        line.sprite = self.sprites[int(random.random()*2)+82]
                    if int(random.random()*35) == 0:
                        line.height_offset = 1
                        line.spriteX = (random.random()*5)+0.5
                        line.sprite = self.sprites[int(random.random()*2)+82]
                
            

            self.lines.append(line)

        self.N = len(self.lines)
        self.pos = 0
        self.playerX = 0  # player start at the center of the road
        self.playerY = 1500  # camera height offset

        self.road_list = []

    def drawQuad(
        self,
        surface,
        color,
        x1,
        y1,
        w1,
        x2,
        y2,
        w2,
    ):
        pg.draw.polygon(
            surface, color, [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)]
        )

    def controls(self):

        if abs(self.playerX) > ROAD_WIDTH*2: #YA FELL OFF!
            self.app.mode = 6
            self.playerX = 0
            self.speed_float = 0
            if self.pos > 10000*SEGMENT_LENGTH:
                self.pos = self.pos - 10000*SEGMENT_LENGTH
            else:
                self.pos = 0
        
        if self.pos > (ROAD_TRIP - 1000)*SEGMENT_LENGTH:
            self.app.mode = 8
            self.playerX = 0
            self.speed_float = 0
            self.pos = 0


        #playerX and playerY control the camera (Can't sink below ground though...)

        if self.road_angle > 0.15:
            if self.app.RIGHT:
                self.playerX = self.playerX / 1.05
            else:
                self.playerX -= self.road_angle*20*int(self.speed_float)
        if self.road_angle < -0.15:
            if self.app.LEFT:
                self.playerX = self.playerX / 1.05
            else:
                self.playerX -= self.road_angle*20*int(self.speed_float)
        else:
            self.playerX = self.playerX / 1.01
        
        if self.app.LEFT:
            self.tilt -= WEAK_TILT
        elif self.app.RIGHT:
            self.tilt += WEAK_TILT

            

        if abs(self.tilt) < 0.05:
            self.tilt = 0
        else:
            self.tilt /= 1.1
        
        if self.playerX > -5 and self.playerX < 5:
            self.playerX = 0
        
        if self.app.GO:
            #self.playerY += 100
            self.speed_float += GO_FORCE
        if self.app.STOP:
            #self.playerY -= 100
            if self.speed_float > STOP_FORCE:
                self.speed_float -= STOP_FORCE
        
        self.app.ship_speed = self.speed_float

    def update(self):

        self.window_surface.fill(BG_COLOR)

        self.speed = int(self.speed_float)*SEGMENT_LENGTH

        self.controls()
        
        self.pos += self.speed

        while self.pos >= self.N * SEGMENT_LENGTH:
            self.pos -= self.N * SEGMENT_LENGTH
        while self.pos < 0:
            self.pos += self.N * SEGMENT_LENGTH
        startPos = self.pos // SEGMENT_LENGTH

        x = dx = 0.0 #Prepare for next loop

        camH = self.lines[startPos].y + self.playerY
        maxy = WINDOW_HEIGHT

        if self.speed > 0:
            self.background_rect.x -= self.lines[startPos].curve * 1.25 * int(self.speed_float)
        elif self.speed < 0:
            self.background_rect.x += self.lines[startPos].curve * 1.25 * int(self.speed_float)

        if self.background_rect.right < self.background_image.get_width(): #Scroll background
            self.background_rect.x = -self.background_image.get_width()
        elif self.background_rect.left > 0:
            self.background_rect.x = -self.background_image.get_width()

        self.window_surface.blit(self.background_surface, self.background_rect)

        if startPos < 2000: #Earth background
            if self.speed > 0:
                self.background_rect_1.x -= self.lines[startPos].curve * 2
            elif self.speed < 0:
                self.background_rect_1.x += self.lines[startPos].curve * 2

            if self.background_rect_1.right < self.background_image_1.get_width():
                self.background_rect_1.x = -self.background_image_1.get_width()
            elif self.background_rect_1.left > 0:
                self.background_rect_1.x = -self.background_image_1.get_width()
            
            if startPos < 1000:
                self.background_rect_1.y = self.player_incline * 40 - 160
            else:
                self.background_rect_1.y = self.player_incline * 40 - 160 + startPos-1000

            self.window_surface.blit(self.background_surface_1, self.background_rect_1)
        



            #Shift background to convey player incline
        self.player_incline = self.lines[startPos % self.N].dy / 100
        self.background_rect.y = self.player_incline * 40 - 80
        self.road_angle = 0

        if startPos > ROAD_TRIP - TIME_SPENT_LANDING: #Caturn animations
            self.caturn_scale = (startPos-(ROAD_TRIP - TIME_SPENT_LANDING))

            if self.caturn_scale > 0 and self.caturn_scale <= 100:
                self.caturn_image_scaled = self.caturn_image_1
            elif self.caturn_scale > 100 and self.caturn_scale <= 200:
                self.caturn_image_scaled = self.caturn_image_2
            elif self.caturn_scale > 200 and self.caturn_scale <= 300:
                self.caturn_image_scaled = self.caturn_image_3
            elif self.caturn_scale > 300 and self.caturn_scale <= 400:
                self.caturn_image_scaled = self.caturn_image_4
            elif self.caturn_scale > 400 and self.caturn_scale <= 500:
                self.caturn_image_scaled = self.caturn_image_5
            elif self.caturn_scale > 500 and self.caturn_scale <= 600:
                self.caturn_image_scaled = self.caturn_image_6
            elif self.caturn_scale > 600 and self.caturn_scale <= 700:
                self.caturn_image_scaled = self.caturn_image_7
            elif self.caturn_scale > 700 and self.caturn_scale <= 800:
                self.caturn_image_scaled = self.caturn_image_8
            else:
                self.caturn_image_scaled = self.caturn_image_100

        
            self.caturn_rect = self.caturn_image_scaled.get_rect(center = (DISPLAY_WIDTH/2,DISPLAY_HEIGHT/2))
            self.caturn_rect.y = self.player_incline * 40 - 160
            self.window_surface.blit(self.caturn_image_scaled,self.caturn_rect)

            #Load the road
        for n in range(startPos, startPos + SHOW_N_SEGMENTS):
            current = self.lines[n % self.N]
            current.project(self.playerX - x, camH, self.pos - (self.N * SEGMENT_LENGTH if n >= self.N else 0))

            #Compensate for player angle
            current.Y = current.Y + (90*(n - self.pos/SEGMENT_LENGTH) * self.player_incline) / ((n - self.pos/SEGMENT_LENGTH)**1.1+1)

            x += dx
            dx += current.curve

            current.clip = maxy

            # don't draw "above ground"
            if current.Y >= maxy+1000:
                continue
            maxy = current.Y

            prev = self.lines[(n - 1) % self.N]  # previous line

            if n - self.pos/SEGMENT_LENGTH > 10:
                darkness = ((n-10)-self.pos/SEGMENT_LENGTH)/(SHOW_N_SEGMENTS)
            else:
                darkness = 0

            if n - self.pos/SEGMENT_LENGTH == 5: #Car is located here!
                self.road_angle = current.dx
            
            if self.playerY < 1700:
                self.playerY = 1700

            self.road_list.append([
                0,
                prev.X,
                prev.Y,
                prev.W,
                current.X,
                current.Y,
                current.W,
                (current.grass_color.r-current.grass_color.r*darkness, current.grass_color.g-current.grass_color.g*darkness, current.grass_color.b-current.grass_color.b*darkness, current.grass_color.a),
                (current.rumble_color.r-current.rumble_color.r*darkness, current.rumble_color.g-current.rumble_color.g*darkness, current.rumble_color.b-current.rumble_color.b*darkness, current.rumble_color.a),
                (current.road_color.r-current.road_color.r*darkness, current.road_color.g-current.road_color.g*darkness, current.road_color.b-current.road_color.b*darkness, current.road_color.a),
            ])



            #Draw everything!
        
        for n in range(startPos + SHOW_N_SEGMENTS, startPos + 1, -1):


                #Billboard sprites
            self.lines[n % self.N].drawSprite(self.window_surface)

                #Polygonal road
            if (n % self.N)-startPos > 0 and (n % self.N)-startPos < len(self.road_list)-1:
                self.road_segment = self.road_list[(n % self.N)-startPos]
                if self.lines[n % self.N].draw_grass:
                    if self.lines[n % self.N].grass_tag == 0:
                        self.drawQuad(
                            self.window_surface,
                            self.road_segment[7],
                            0,
                            self.road_segment[2],
                            WINDOW_WIDTH,
                            0,
                            self.road_segment[5],
                            WINDOW_WIDTH,
                        )
                    elif self.lines[n % self.N].grass_tag == 4:
                        self.drawQuad(
                            self.window_surface,
                            self.road_segment[7],
                            self.road_segment[1],
                            self.road_segment[2],
                            self.road_segment[3] * 10,
                            self.road_segment[4],
                            self.road_segment[5],
                            self.road_segment[6] * 10,
                        )
                    elif self.lines[n % self.N].grass_tag == 6:
                        self.drawQuad(
                            self.window_surface,
                            self.road_segment[7],
                            self.road_segment[1],
                            self.road_segment[2],
                            self.road_segment[3] * 4.5,
                            self.road_segment[4],
                            self.road_segment[5],
                            self.road_segment[6] * 4.5,
                        )
                self.drawQuad(
                    self.window_surface,
                    self.road_segment[8],
                    self.road_segment[1],
                    self.road_segment[2],
                    self.road_segment[3] * 1.2,
                    self.road_segment[4],
                    self.road_segment[5],
                    self.road_segment[6] * 1.2,
                )
                self.drawQuad(
                    self.window_surface,
                    self.road_segment[9],
                    self.road_segment[1],
                    self.road_segment[2],
                    self.road_segment[3],
                    self.road_segment[4],
                    self.road_segment[5],
                    self.road_segment[6],
                )
        
        self.road_list = []
        
        self.image = self.window_surface
        self.rect = self.window_surface.get_rect(center = vec2(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
        
        self.image, self.rect = rotate(self.image, self.rect, self.tilt)
        
class Ship_Interior(pg.sprite.Sprite):
    def __init__(self, app, sp_tag):

            #Define locals
        self.app = app
        self.group = app.interior_group
        self.sp_tag = sp_tag
        self.attrs = INTERIOR_ATTRS[self.sp_tag]
        self.sprite_sheet = pg.image.load(self.attrs['path']).convert_alpha()
        self.sprite_width = self.sprite_sheet.get_width()
        self.sprite_height = self.sprite_sheet.get_height() / self.attrs['frames']
        self.sp_frame = 0
        self.sp_frame_float = 0
        self.turbine_heatup = 0

        super().__init__(self.group)

        self.get_image()

        self.rect = self.image.get_rect(center = vec2(DISPLAY_WIDTH/2 + self.attrs['pos'][0], DISPLAY_HEIGHT/2 + self.attrs['pos'][1]))

    def update(self):

        self.animate()
        self.get_image()

    def easter_eggs(self):
        #YAHAHAHA! YOU FOUND ME!
        #I put some easter eggs here :)
        pass
    


    def animate(self):

        if self.sp_tag == 'DPad':
            if not self.app.LEFT and not self.app.RIGHT and not self.app.UP and not self.app.DOWN:
                self.sp_frame = 0
            elif self.app.LEFT:
                self.sp_frame = 1
            elif self.app.RIGHT:
                self.sp_frame = 2
            elif self.app.UP:
                self.sp_frame = 3
            elif self.app.DOWN:
                self.sp_frame = 4
        elif self.sp_tag == 'StopGo':
            if not self.app.GO and not self.app.STOP:
                self.sp_frame = 0
            elif self.app.GO and self.app.STOP:
                self.sp_frame = 1
            elif self.app.STOP:
                self.sp_frame = 2
            elif self.app.GO:
                self.sp_frame = 3
        elif self.sp_tag == 'TurbineIcon' or self.sp_tag == 'TurbineIcon_2':
            if self.app.ship_speed > 0:
                self.sp_frame_float += (self.app.ship_speed/3) + 0.025

            if int(self.sp_frame_float) >= self.attrs['frames']:
                self.sp_frame_float = 0
            self.sp_frame = int(self.sp_frame_float)
        
        elif self.sp_tag == 'POS_NUM_1':
            self.sp_frame = int( (self.app.skyway.pos/SEGMENT_LENGTH) / ROAD_TRIP * 10)
        elif self.sp_tag == 'POS_NUM_2':
            self.sp_frame = int( (self.app.skyway.pos/SEGMENT_LENGTH) / ROAD_TRIP * 100)-int( (self.app.skyway.pos/SEGMENT_LENGTH) / ROAD_TRIP * 10)*10
        elif self.sp_tag == 'POS_TXT':
            self.sp_frame = 0

    
    def get_image(self):
        
        self.image = self.sprite_sheet.subsurface((0, self.sp_frame*self.sprite_height, self.sprite_width, self.sprite_height))
        self.image = pg.transform.scale(self.image, self.attrs['scale'])

def rotate(image, rect, angle):
    # Rotate the original image without modifying it.
    new_image = pg.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect

class Cutscene(pg.sprite.Sprite):
    def __init__(self, app):
        
            #Define locals
        self.repeat_i = 0
        self.initialize = True
        self.imagecount = 0
        self.framecount = -50
        self.app = app
        self.i = 0
        
        self.image = pg.image.load('images/Scenes/IntroScene_1.png')
        self.attrs = SCENE_ATTRS['IntroScene_1']
        self.image2 = pg.image.load(self.attrs['path']).convert_alpha()
        self.group = app.scene_group

            #SUUUUUPER INIT
        super().__init__(self.group)

    def scene_thinking(self):

        if self.app.mode == 2:

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['IntroScene_1']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = -60
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 2.5
        
        elif self.app.mode == 2.5:

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['IntroScene_1_1']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 3
        
        elif self.app.mode == 3:

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['IntroScene_2']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 4
        
        elif self.app.mode == 4:

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['IntroScene_3']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 5
        
        elif self.app.mode == 5:

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['IntroScene_4']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.skyway.reset = True
                self.app.mode = 1
        
        elif self.app.mode == 6: #DIED

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['DiedScene_1']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 7
        
        elif self.app.mode == 7: #DIED

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['DiedScene_2']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = 0
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 5
        
        elif self.app.mode == 8: #Won

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['EndScene_1']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = -20
                self.initialize = False
                pg.mixer.music.load('music/Win.mp3')
                pg.mixer.music.play(-1)

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.i = 0
                self.initialize = True
                self.app.mode = 9

        elif self.app.mode == 9: #Won

            if self.initialize == True:
                self.attrs = SCENE_ATTRS['EndScene_2']
                self.image2 = pg.image.load(self.attrs['path'])
                self.imagecount = 0
                self.framecount = -30
                self.initialize = False

            if self.imagecount < self.attrs['frames']-1:
                self.framecount = self.framecount + 1
                if self.framecount > self.attrs['framerate']:
                    self.framecount = 0
                    self.imagecount = self.imagecount + 1
            else:
                self.framecount = 0
                self.imagecount = 4
                
        
        

    def scene_rendering(self):
        
        self.image = self.image2.subsurface(0,(self.imagecount)*SCENE_HEIGHT, SCENE_WIDTH, SCENE_HEIGHT)
        self.image = pg.transform.scale(self.image, (DISPLAY_WIDTH,DISPLAY_HEIGHT))
        self.rect = self.image.get_rect(center = (DISPLAY_WIDTH/2,DISPLAY_HEIGHT/2))

    def update(self):

        self.scene_thinking()
        self.scene_rendering()

game = GameWindow()
asyncio.run( main())