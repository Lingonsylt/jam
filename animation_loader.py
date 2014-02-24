import pyglet

def load_animation(sprite_sheet):
    img = pyglet.image.load('sprite_sheets/'+sprite_sheet+'.png')
    sheet_meta = open('sprite_sheets/'+sprite_sheet+'_meta')
    animation_meta = []

    for line in sheet_meta:
        if line.startswith('quad'):
            line=line.split(':')
            quad_width = int(line[1])
            quad_height = int(line[2])
        else:
            line=line.split(':')
            animation_meta.append([line[0],int(line[1]),int(line[2])])

    ani_list = ()
    animation = {}
    for row in animation_meta:
        frame_set=[]
        for i in range(row[2]):
            frame = img.get_region(i*quad_width, row[1]*quad_height, quad_width, quad_height)
            animation.setdefault(row[0],[]).append(frame)

    return img, animation
