import pyglet

def load_animation(sprite_sheet):
    img = pyglet.image.load('sprite_sheets/'+sprite_sheet+'.png')
    sheet_meta = open('sprite_sheets/'+sprite_sheet+'_meta')
    animation_meta = []
    animation = {}

    for line in sheet_meta:
        if line.startswith('quad'):
            line=line.split(':')
            quad_width = int(line[1])
            quad_height = int(line[2])
        else:
            line=line.split(':')
            for i in range(int(line[2])):
                frame = img.get_region(i*quad_width, int(line[1])*quad_height, quad_width, quad_height)
                animation.setdefault(line[0],[]).append(frame)

    return img, animation
