import pygame as pg

vec2 = pg.math.Vector2

ROAD_TRIP = 50000 #50000 or 7000

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 450

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

BG_COLOR = 'black'
FPS = 60

ROAD_WIDTH = 2000 #Road width
SEGMENT_LENGTH = 250 #Road segment length
CAMERA_DEPTH = 0.84 #Camera depth
SHOW_N_SEGMENTS = 600 #Amount of road segments to load

STRONG_TILT = 0.7 #Unused
WEAK_TILT = 0.7

GO_FORCE = 0.04
STOP_FORCE = 0.1

if True: #Event 0 (Space)
    dark_grass = pg.Color(0, 200, 200)
    light_grass = pg.Color(0, 225, 225)
    white_rumble = pg.Color(0, 85, 85)
    black_rumble = pg.Color(0, 20, 20)
    dark_road = pg.Color(130, 130, 130)
    light_road = pg.Color(150, 150, 150)
        #Y scaling
    INTENSITY_Y = 25
    CORRECTION = 1
    DAMPER = 200
    UPPER_BOUND = 40000
    LOWER_BOUND = -40000
    BOUND_PULL = 5
    ENTROPY_Y = 0.005
    BIAS_Y = 0

        #X scaling
    INTENSITY_X = 10
    ENTROPY_X = 0.005
    BIAS_X = 0

if True: #Event 1(Earth)
    dark_grass_1 = pg.Color(0, 200, 0)
    light_grass_1 = pg.Color(0, 225, 0)
    white_rumble_1 = pg.Color(0, 130, 85)
    black_rumble_1 = pg.Color(0, 50, 20)
    dark_road_1 = pg.Color(130, 160, 130)
    light_road_1 = pg.Color(150, 180, 150)
            #Y scaling
    INTENSITY_Y_1 = 5
    CORRECTION_1 = 1
    DAMPER_1 = 20
    UPPER_BOUND_1 = 40000
    LOWER_BOUND_1 = -40000
    BOUND_PULL_1 = 5
    ENTROPY_Y_1 = 0.1
    BIAS_Y_1 = 0

        #X scaling
    INTENSITY_X_1 = 1
    ENTROPY_X_1 = 0.1
    BIAS_X_1 = 0

if True: #Event 2 (Exit Earth Ramp start)
    dark_grass_2 = pg.Color(0, 200, 200)
    light_grass_2 = pg.Color(0, 225, 225)
    white_rumble_2 = pg.Color(0, 85, 85)
    black_rumble_2 = pg.Color(0, 20, 20)
    dark_road_2 = pg.Color(130, 130, 130)
    light_road_2 = pg.Color(150, 150, 150)
        #Y scaling
    INTENSITY_Y_2 = 0
    CORRECTION_2 = 1
    DAMPER_2 = 200
    UPPER_BOUND_2 = 40000
    LOWER_BOUND_2 = -40000
    BOUND_PULL_2 = 5
    ENTROPY_Y_2 = 0.009
    BIAS_Y_2 = 3

        #X scaling
    INTENSITY_X_2 = 0
    ENTROPY_X_2 = 0.002
    BIAS_X_2 = 0

if True: #Event 3 (Exit Earth Ramp end)
    dark_grass_3 = pg.Color(0, 200, 200)
    light_grass_3 = pg.Color(0, 225, 225)
    white_rumble_3 = pg.Color(0, 85, 85)
    black_rumble_3 = pg.Color(0, 20, 20)
    dark_road_3 = pg.Color(130, 130, 130)
    light_road_3 = pg.Color(150, 150, 150)
        #Y scaling
    INTENSITY_Y_3 = 4
    CORRECTION_3 = 1
    DAMPER_3 = 200
    UPPER_BOUND_3 = 40000
    LOWER_BOUND_3 = -40000
    BOUND_PULL_3 = 5
    ENTROPY_Y_3 = 0.009
    BIAS_Y_3 = 0

        #X scaling
    INTENSITY_X_3 = 4
    ENTROPY_X_3 = 0.005
    BIAS_X_3 = 0

if True: #Event 4 (Space Station) #50
    EVENT_LENGTH_4 = 100

    dark_grass_4 = pg.Color(45, 35, 70)
    light_grass_4 = pg.Color(65, 45, 115)
    white_rumble_4 = pg.Color(0, 85, 85)
    black_rumble_4 = pg.Color(0, 20, 20)
    dark_road_4 = pg.Color(75, 55, 160)
    light_road_4 = pg.Color(90, 50, 240)

        #Y scaling
    INTENSITY_Y_4 = 3
    CORRECTION_4 = 1
    DAMPER_4 = 5
    UPPER_BOUND_4 = 40000
    LOWER_BOUND_4 = -40000
    BOUND_PULL_4 = 5
    ENTROPY_Y_4 = 0.009
    BIAS_Y_4 = 0

        #X scaling
    INTENSITY_X_4 = 10
    ENTROPY_X_4 = 0.02
    BIAS_X_4 = 0

if True: #Event 5 Asteroid belt
    EVENT_LENGTH_5 = 2000

    dark_grass_5 = pg.Color(0, 200, 200)
    light_grass_5 = pg.Color(0, 225, 225)
    white_rumble_5 = pg.Color(0, 85, 85)
    black_rumble_5 = pg.Color(0, 20, 20)
    dark_road_5 = pg.Color(110, 110, 110)
    light_road_5 = pg.Color(130, 130, 130)

        #Y scaling
    INTENSITY_Y_5 = 25
    CORRECTION_5 = 1
    DAMPER_5 = 50
    UPPER_BOUND_5 = 40000
    LOWER_BOUND_5 = -40000
    BOUND_PULL_5 = 5
    ENTROPY_Y_5 = 0.05
    BIAS_Y_5 = 0

        #X scaling
    INTENSITY_X_5 = 2
    ENTROPY_X_5 = 0.03
    BIAS_X_5 = 0

if True: #Event 6 Highway
    EVENT_LENGTH_6 = 6000

    dark_grass_6 = pg.Color(0, 80, 80)
    light_grass_6 = pg.Color(0, 100, 100)
    white_rumble_6 = pg.Color(0, 85, 85)
    black_rumble_6 = pg.Color(0, 20, 20)
    dark_road_6 = pg.Color(110, 110, 110)
    light_road_6 = pg.Color(130, 130, 130)

        #Y scaling
    INTENSITY_Y_6 = 0.5
    CORRECTION_6 = 1
    DAMPER_6 = 200
    UPPER_BOUND_6 = 40000
    LOWER_BOUND_6 = -40000
    BOUND_PULL_6 = 1
    ENTROPY_Y_6 = 0.05
    BIAS_Y_6 = 0

        #X scaling
    INTENSITY_X_6 = 0.1
    ENTROPY_X_6 = 0.5
    BIAS_X_6 = 0

if True: #Event 96 Enter Caturn Ramp start

    dark_grass_96 = pg.Color(0, 200, 200)
    light_grass_96 = pg.Color(0, 225, 225)
    white_rumble_96 = pg.Color(0, 85, 85)
    black_rumble_96 = pg.Color(0, 20, 20)
    dark_road_96 = pg.Color(0, 130, 130)
    light_road_96 = pg.Color(0, 150, 150)
        #Y scaling
    INTENSITY_Y_96 = 0
    CORRECTION_96 = 1
    DAMPER_96 = 140
    UPPER_BOUND_96 = 40000
    LOWER_BOUND_96 = -60000
    BOUND_PULL_96 = 5
    ENTROPY_Y_96 = 0.005
    BIAS_Y_96 = -2.75

        #X scaling
    INTENSITY_X_96 = 0
    ENTROPY_X_96 = 0.001
    BIAS_X_96 = 0

if True: #Event 97 Enter Caturn Ramp end

    dark_grass_97 = pg.Color(0, 80, 80)
    light_grass_97 = pg.Color(0, 100, 100)
    white_rumble_97 = pg.Color(0, 85, 85)
    black_rumble_97 = pg.Color(0, 20, 20)
    dark_road_97 = pg.Color(0, 160, 160)
    light_road_97 = pg.Color(0, 180, 180)
        #Y scaling
    INTENSITY_Y_97 = 0
    CORRECTION_97 = 1
    DAMPER_97 = 200
    UPPER_BOUND_97 = 40000
    LOWER_BOUND_97 = -60000
    BOUND_PULL_97 = 5
    ENTROPY_Y_97 = 0.005
    BIAS_Y_97 = 0

        #X scaling
    INTENSITY_X_97 = 1
    ENTROPY_X_97 = 0.05
    BIAS_X_97 = 0

if True: #Event 98 Flat Caturn ground

    dark_grass_98 = pg.Color(0, 80, 80)
    light_grass_98 = pg.Color(0, 100, 100)
    white_rumble_98 = pg.Color(0, 85, 85)
    black_rumble_98 = pg.Color(0, 20, 20)
    dark_road_98 = pg.Color(0, 160, 160)
    light_road_98 = pg.Color(0, 180, 180)
        #Y scaling
    INTENSITY_Y_98 = 5
    CORRECTION_98 = 1
    DAMPER_98 = 20
    UPPER_BOUND_98 = 40000
    LOWER_BOUND_98 = -60000
    BOUND_PULL_98 = 5
    ENTROPY_Y_98 = 0.1
    BIAS_Y_98 = 0

        #X scaling
    INTENSITY_X_98 = 1
    ENTROPY_X_98 = 0.1
    BIAS_X_98 = 0

if True: #Event 99 (The end)

    TIME_SPENT_LANDING = 3800

INTERIOR_ATTRS = {

    'ShipHull': {
        'path': 'images/Interior/Interior.png',
        'frames': 1,
        'scale': (800,480),
        'pos': (0,0),
    },
    'DPad': {
        'path': 'images/Interior/DPad.png',
        'frames': 5,
        'scale': (64*4,64*4),
        'pos': (-140,192),
    },
    'StopGo': {
        'path': 'images/Interior/StopGo.png',
        'frames': 4,
        'scale': (64*4,64*4),
        'pos': (140,192),
    },
    'TurbineIcon': {
        'path': 'images/Interior/TurbineIcon.png',
        'frames': 7,
        'scale': (64*2,64*2),
        'pos': (-312,-156),
    },
    
    'TurbineIcon_2': {
        'path': 'images/Interior/TurbineIcon.png',
        'frames': 7,
        'scale': (64*2,64*2),
        'pos': (312,-156),
    },
   'POS_NUM_1': {
        'path': 'images/Interior/Numbers.png',
        'frames': 10,
        'scale': (8*4,8*4),
        'pos': (-138,-180),
    },
   'POS_NUM_2': {
        'path': 'images/Interior/Numbers.png',
        'frames': 10,
        'scale': (8*4,8*4),
        'pos': (-108,-180),
    },
   'POS_TXT': {
        'path': 'images/Interior/Pos_Txt.png',
        'frames': 1,
        'scale': (48*4,8*4),
        'pos': (-150,-180),
    },

}

SCENE_WIDTH = 200
SCENE_HEIGHT = 120
SCENE_ATTRS = {

    'IntroScene_1': {
        'path': 'images/Scenes/IntroScene_1.png',
        'frames': 9,
        'special': 1,
        'framerate': 7,
    },
    'IntroScene_1_1': {
        'path': 'images/Scenes/IntroScene_1_1.png',
        'frames': 15,
        'special': 1,
        'framerate': 7,
    },
    'IntroScene_2': {
        'path': 'images/Scenes/IntroScene_2.png',
        'frames': 16,
        'special': 1,
        'framerate': 7,
    },
    'IntroScene_3': {
        'path': 'images/Scenes/IntroScene_3.png',
        'frames': 12,
        'special': 1,
        'framerate': 7,
    },
    'IntroScene_4': {
        'path': 'images/Scenes/IntroScene_4.png',
        'frames': 21,
        'special': 1,
        'framerate': 7,
    },
    'DiedScene_1': {
        'path': 'images/Scenes/DiedScene_1.png',
        'frames': 11,
        'special': 1,
        'framerate': 7,
    },
    'DiedScene_2': {
        'path': 'images/Scenes/DiedScene_2.png',
        'frames': 16,
        'special': 1,
        'framerate': 7,
    },
    'EndScene_1': {
        'path': 'images/Scenes/EndScene_1.png',
        'frames': 10,
        'special': 1,
        'framerate': 6,
    },
    'EndScene_2': {
        'path': 'images/Scenes/EndScene_2.png',
        'frames': 14,
        'special': 1,
        'framerate': 6,
    },

}
