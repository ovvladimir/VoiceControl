# https://pyglet.readthedocs.io/en/stable/programming_guide/graphics.html
import pyglet
from pyglet import gl
from pyglet.window import key
import math
import sounddevice as sd
import numpy as np

W, H = 780, 630
BG_COLOR = (.75, .75, .75, 1)

SPEED_POLYGON = 30
SIZE = 30

SPEED_CIRCLE = 300
RADIUS = 20

level = [
    '----------------------------------------------------------------------------------------------------------------------------------',
    '-                           -                          --                        ---                                  -          -',
    '-                                                      --                                                       -                -',
    '-                                                                                                                                -',
    '-            --                                                   -                                                              -',
    '-                                                                                                                                -',
    '--                                                                -                                                              -',
    '-                                                                                   ---                                          -',
    '-                                       --                                          ---                                     ---  -',
    '-                                                                                                                                -',
    '-                                                                                                                                -',
    '-                                                                                 -                                              -',
    '-                                                     -                                                                          -',
    '-   --------                                          -                                                                          -',
    '-                                                                                                                  -             -',
    '-                                                                  --                                              -             -',
    '-                   --                                                                                                           -',
    '-                                                                             -                                  --              -',
    '-                                   -          -                             -                                  ---              -',
    '-                                   -                                       -                           -                        -',
    '----------------------------------------------------------------------------------------------------------------------------------'
]

level.reverse()

window = pyglet.window.Window(width=W, height=H, caption='Voice Control')
window.set_location(5, 30)
window.set_mouse_visible(visible=False)
counter = pyglet.window.FPSDisplay(window=window)

keys = key.KeyStateHandler()
window.push_handlers(keys)

# group = pyglet.graphics.Group()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
batch = pyglet.graphics.Batch()

# text
penalty = [0]
penalty_label = pyglet.text.Label(
    text=f'Штраф: {penalty[0]}', font_name='Times difference Roman', color=(255, 0, 0, 255),
    x=window.width // 2, anchor_x='center', y=window.height - SIZE, anchor_y='top',
    font_size=16, batch=batch, group=foreground)

# start QUADS
polygon_list = []
x = y = 0
for row in level:
    for col in row:
        if col == '-':
            polygon = batch.add(
                4, pyglet.gl.GL_QUADS, background,
                ('v2f/stream', [x, y, x, y + SIZE, x + SIZE, y + SIZE, x + SIZE, y]),
                ('c3f/static', (0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0)))
            polygon_list.append(polygon)
        x += SIZE
    y += SIZE
    x = 0
# end QUADS


def face(a, b, c, x1, y1, radius):
    point_list = []
    for angle in range(a, b, c):
        radian = math.radians(angle)
        s = radius * math.sin(radian)
        c = radius * math.cos(radian)
        point_list.append(x1 + c)
        point_list.append(y1 + s)
    number_points = len(point_list) // 2
    lists = batch.add(
        number_points, pyglet.gl.GL_POINTS, foreground,
        ('v2f/stream', point_list),
        ('c4B', [0, 128, 0, 255] * number_points)
    )
    face_list.append(lists)
    return lists


def update(dt):
    if face_list[1].colors[:] == [255, 0, 0, 255] * (len(face_list[1].colors) // 4):
        for obj in face_list:
            obj.colors = [0, 128, 0, 255] * (len(obj.colors) // 4)
    # motion face
    if keys[key.LEFT] and circle_list.vertices[0] > 0 + RADIUS * 2:
        for ver_list in face_list:
            ver_list.vertices = [
                element - SPEED_CIRCLE * dt if n % 2 == 0 else element
                for n, element in enumerate(ver_list.vertices)]
    if keys[key.RIGHT] and circle_list.vertices[0] < W:
        for ver_list in face_list:
            ver_list.vertices = [
                element + SPEED_CIRCLE * dt if n % 2 == 0 else element
                for n, element in enumerate(ver_list.vertices)]
    if keys[key.UP] and circle_list.vertices[1] < H - RADIUS:
        for ver_list in face_list:
            ver_list.vertices = [
                element + SPEED_CIRCLE * dt if n % 2 != 0 else element
                for n, element in enumerate(ver_list.vertices)]
    if keys[key.DOWN] and circle_list.vertices[1] > 0 + RADIUS:
        for ver_list in face_list:
            ver_list.vertices = [
                element - SPEED_CIRCLE * dt if n % 2 != 0 else element
                for n, element in enumerate(ver_list.vertices)]

    # motion QUADS
    if polygon_list[0].vertices[0] > -W * 4 + 1:
        for ver in polygon_list:
            ver.vertices = [
                elem - SPEED_POLYGON * dt if e % 2 == 0 else elem
                for e, elem in enumerate(ver.vertices)]
    # motion face in end game
    else:
        if circle_list.vertices[0] < W:
            for ver_list in face_list:
                ver_list.vertices = [
                    element + SPEED_POLYGON * dt if n % 2 == 0 else element
                    for n, element in enumerate(ver_list.vertices)]

    # collision
    if circle_list.vertices[0] < W - RADIUS * 2:
        for ver in polygon_list:
            nx = max(ver.vertices[0], min(circle_list.vertices[0] - RADIUS, ver.vertices[0] + SIZE))
            ny = max(ver.vertices[1], min(circle_list.vertices[1], ver.vertices[1] + SIZE))
            dtc = (nx - (circle_list.vertices[0] - RADIUS)) ** 2 + (ny - circle_list.vertices[1]) ** 2
            if dtc <= RADIUS ** 2:
                penalty[0] += 0.1
                penalty_label.text = f'Штраф: {round(penalty[0], 1)}'
                for obj in face_list:
                    obj.colors = [255, 0, 0, 255] * (len(obj.colors) // 4)
    else:
        stream.stop(ignore_errors=True)
        stream.close(ignore_errors=True)


@window.event
def on_draw():
    window.clear()
    batch.draw()
    counter.draw()


def audio_callback(indata, frames, time, status):
    list_y.append(np.linalg.norm(indata) * 20)
    list_y.pop(0)
    volume = int(sum(list_y) / len(list_y))

    for k, ver_list in enumerate(face_list):
        difference_vol[k] = [i + j for i, j in zip(
            [volume if k == 0 else volume - RADIUS * 0.3 if k == 3 else volume + RADIUS * 0.2]
            * len(difference[k]), difference[k])]
        m = 0
        for n, element in enumerate(ver_list.vertices):
            ver_list.vertices[n] = difference_vol[k][m] if n % 2 != 0 else element
            m += 1 if n % 2 != 0 else 0


gl.glClearColor(*BG_COLOR)  # цвет окна
# включает прозрачность
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
gl.glPointSize(2.0)  # размер точек
gl.glEnable(gl.GL_POINT_SMOOTH)  # сглаживание точек
# gl.glLidifferenceidth(4) ???
# gl.glLineWidth(4.0)
# gl.glEnable(gl.GL_LINE_SMOOTH)

face_list = []  # для перемещения
circle_list = face(0, 360, 6, W // 2, H // 2, RADIUS)  # circle_list для столкновений
face(0, 360, 36, W // 2 - RADIUS * 0.42, H // 2 + RADIUS * 0.2, RADIUS // 6)
face(0, 360, 36, W // 2 + RADIUS * 0.42, H // 2 + RADIUS * 0.2, RADIUS // 6)
face(210, 340, 10, W // 2, H // 2, RADIUS * 0.6)
difference = [None] * len(face_list)
difference_vol = [None] * len(face_list)
for f in range(len(face_list)):
    difference[f] = [0] + [i - j for i, j in zip(
        face_list[f].vertices[3::2],
        [face_list[f].vertices[1]] * (len(face_list[f].vertices) // 2 - 1))]

list_y = [H // 2] * 20
stream = sd.InputStream(callback=audio_callback)
with stream:
    pyglet.clock.schedule_interval(update, 1 / 30.0)
    pyglet.app.run()

'''
NV = 4
COLOR = [255, 0, 0] * NV
pyglet.graphics.draw(
    NV, pyglet.gl.GL_POLYGON,
    ('v2i', [x, y, x, y + SIZE, x + SIZE, y + SIZE, x + SIZE, y]),
    ('c3B', COLOR))
NV - первый аргумент (кол-во вершин QUADS или POLYGON)
v2i (v - вершины, 2-а значения (x, y), i - int)
c3B (c - цвет, 3-и значения RGB (для каждой вершины отдельно),
     B - формат (255, 255, 255) или f - формат (1.0, 1.0, 1.0))
'''
'''
from pyglet.gl import *
# круг с радиусом RADIUS и координатами x, y (в def on_draw():)
glLoadIdentity()
glColor4f(1, 0, 0, .75)
glBegin(GL_TRIANGLE_FAN)
for angle in range(0, 360, 10):
    rads = math.radians(angle)
    s = RADIUS * math.sin(rads)
    c = RADIUS * math.cos(rads)
    glVertex3f(x + c, y + s, 0)
glEnd()
'''
