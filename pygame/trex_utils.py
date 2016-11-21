import pygame
import sys
def load():
    # path of player with different states
    PLAYER_PATH = (
        'assets/sprites/trex1.png',
        'assets/sprites/trex2.png',
        'assets/sprites/trex3.png',
        'assets/sprites/trex4.png',
        'assets/sprites/trex5.png',
        'assets/sprites/trex6.png',
        'assets/sprites/duck1.png',
        'assets/sprites/duck2.png',
    )

    # path of background
    # BACKGROUND_PATH = 'assets/sprites/background-black.png'

    # path of large cactus
    LARGE_CACTUS_PATH = (
        'assets/sprites/large_cactus1.png',
        'assets/sprites/large_cactus2.png',
        'assets/sprites/large_cactus3.png',
        'assets/sprites/large_cactus4.png',
        'assets/sprites/large_cactus5.png',
        'assets/sprites/large_cactus6.png',
    )

    # path of small cactus
    SMALL_CACTUS_PATH = (
        'assets/sprites/small_cactus1.png',
        'assets/sprites/small_cactus2.png',
        'assets/sprites/small_cactus3.png',
        'assets/sprites/small_cactus4.png',
        'assets/sprites/small_cactus5.png',
        'assets/sprites/small_cactus6.png',
    )

    # path of bird
    BIRD_PATH = (
        'assets/sprites/bird1.png',
        'assets/sprites/bird2.png',
    )

    IMAGES, SOUNDS, HITMASKS = {}, {}, {}

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha(),
    )

    IMAGES['HI'] = (
        pygame.image.load('assets/sprites/H.png').convert_alpha(),
        pygame.image.load('assets/sprites/I.png').convert_alpha(),
    )

    IMAGES['game_over'] = (
        pygame.image.load('assets/sprites/game_over.png').convert_alpha(),
        pygame.image.load('assets/sprites/restart.png').convert_alpha(),
    )

    # horizon sprite
    IMAGES['horizons'] = (
        pygame.image.load('assets/sprites/horizon1.png').convert_alpha(),
        pygame.image.load('assets/sprites/horizon2.png').convert_alpha(),
    )

    # cloud sprite
    IMAGES['cloud'] = pygame.image.load('assets/sprites/cloud.png').convert_alpha()

    # sounds
    # soundExt = '.wav'

    # SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/sound-hit' + soundExt)
    # SOUNDS['press']    = pygame.mixer.Sound('assets/audio/sound-press' + soundExt)
    # SOUNDS['reached']  = pygame.mixer.Sound('assets/audio/sound-reached' + soundExt)

    # select random background sprites
    # IMAGES['background'] = pygame.image.load(BACKGROUND_PATH).convert()

    # select random player sprites
    IMAGES['player'] = (
        pygame.image.load(PLAYER_PATH[0]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[1]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[2]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[3]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[4]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[5]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[6]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[7]).convert_alpha(),
    )

    # select random large cactus sprites
    IMAGES['large_cactci'] = (
        pygame.image.load(LARGE_CACTUS_PATH[0]).convert_alpha(),
        pygame.image.load(LARGE_CACTUS_PATH[1]).convert_alpha(),
        pygame.image.load(LARGE_CACTUS_PATH[2]).convert_alpha(),
        pygame.image.load(LARGE_CACTUS_PATH[3]).convert_alpha(),
        pygame.image.load(LARGE_CACTUS_PATH[4]).convert_alpha(),
        pygame.image.load(LARGE_CACTUS_PATH[5]).convert_alpha(),
    )

    # select random small cactus sprites
    IMAGES['small_cactci'] = (
        pygame.image.load(SMALL_CACTUS_PATH[0]).convert_alpha(),
        pygame.image.load(SMALL_CACTUS_PATH[1]).convert_alpha(),
        pygame.image.load(SMALL_CACTUS_PATH[2]).convert_alpha(),
        pygame.image.load(SMALL_CACTUS_PATH[3]).convert_alpha(),
        pygame.image.load(SMALL_CACTUS_PATH[4]).convert_alpha(),
        pygame.image.load(SMALL_CACTUS_PATH[5]).convert_alpha(),
    )

    IMAGES['birds'] = (
        pygame.image.load(BIRD_PATH[0]).convert_alpha(),
        pygame.image.load(BIRD_PATH[1]).convert_alpha(),
    )

    # hismask for large cactci
    HITMASKS['large_cactci'] = (
        getHitmask(IMAGES['large_cactci'][0]),
        getHitmask(IMAGES['large_cactci'][1]),
        getHitmask(IMAGES['large_cactci'][2]),
        getHitmask(IMAGES['large_cactci'][3]),
        getHitmask(IMAGES['large_cactci'][4]),
        getHitmask(IMAGES['large_cactci'][5]),
    )

    # hismask for small cactci
    HITMASKS['small_cactci'] = (
        getHitmask(IMAGES['small_cactci'][0]),
        getHitmask(IMAGES['small_cactci'][1]),
        getHitmask(IMAGES['small_cactci'][2]),
        getHitmask(IMAGES['small_cactci'][3]),
        getHitmask(IMAGES['small_cactci'][4]),
        getHitmask(IMAGES['small_cactci'][5]),
    )

    # hismask for bird
    HITMASKS['birds'] = (
        getHitmask(IMAGES['birds'][0]),
        getHitmask(IMAGES['birds'][1]),
    )

    # hitmask for player
    HITMASKS['player'] = (
        getHitmask(IMAGES['player'][0]),
        getHitmask(IMAGES['player'][1]),
        getHitmask(IMAGES['player'][2]),
        getHitmask(IMAGES['player'][3]),
        getHitmask(IMAGES['player'][4]),
        getHitmask(IMAGES['player'][5]),
        getHitmask(IMAGES['player'][6]),
        getHitmask(IMAGES['player'][7]),
    )

    return IMAGES, SOUNDS, HITMASKS

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask
