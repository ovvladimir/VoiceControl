from pyglet import gl, shapes, graphics, window, text, clock, app, canvas
import math
import sounddevice as sd
import numpy
import warnings

warnings.filterwarnings('ignore')

W, H = 780, 630
BG_COLOR = (.75, .75, .75, 1)

RED = (255, 0, 0, 255)
GREEN = (0, 128, 0, 255)
RADIUS = 30
SIZE = 30
SPEED = 60
speed_fase = 2
penalty = [0]
game = [True]

playing_field = [
    '----------------------------------------------------------------------------------------------------------------------------------',
    '-                           -                          --                        ---                                             -',
    '-                                                      --                                                       -                -',
    '-                                                                                                                                -',
    '-            --                                                   -                                                              -',
    '-                                                                                                                                -',
    '--                                                                -                                                              -',
    '-                                                                                   ---                                          -',
    '-                                       --                                          ---                                     ---  -',
    '-                                                                                                    -                           -',
    '-                                                                                                     -                          -',
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

playing_field.reverse()

config = gl.Config(sample_buffers=1, samples=4)  # smoothing (сглаживание)
my_window = window.Window(width=W, height=H, caption='Voice Control', config=config, resizable=True)
my_window.set_mouse_visible(visible=False)
screens = canvas.Display().get_screens()
screen = screens[0]
left, top = (screen.width - W) // 2, (screen.height - H) // 2
my_window.set_location(left, top)

program = shapes.get_default_shader()
batch = graphics.Batch()
background = graphics.Group(0)
foreground = graphics.Group(1)

# text
penalty_label = text.Label(
    text=f'Штраф: {penalty[0]}', font_name='Times New Roman', color=RED,
    x=W // 2, anchor_x='center', y=H - SIZE, anchor_y='top',
    font_size=16, batch=batch, group=foreground)
game_over_label = text.Label(
    text='', font_name='Times New Roman', color=RED,
    x=W // 2, anchor_x='center', y=H // 2 + SIZE, anchor_y='center',
    font_size=32, batch=batch, group=foreground)
game_start_label = text.Label(
    text='', font_name='Times New Roman', color=RED,
    x=W // 2, anchor_x='center', y=H // 2 - SIZE, anchor_y='center',
    font_size=32, batch=batch, group=foreground)


# start Quads
def create_quads(x, y):
    for row in playing_field:
        for col in row:
            if col == '-':
                rectangle_list.append(program.vertex_list(
                    6, gl.GL_TRIANGLES, batch=batch, group=background,
                    vertices=('f', [x, y, x + SIZE, y, x + SIZE, y + SIZE, x, y, x + SIZE, y + SIZE, x, y + SIZE]),
                    # colors = 1 if 'i' or 'f', 255 if 'Bn'
                    colors=('i', (0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1))))
            x += SIZE
        y += SIZE
        x = 0


rectangle_list = []
create_quads(0, 0)
# end Quads


# start Face
def face(a, b, c, x, y, radius, point=2):
    for angle in range(a, b, c):
        radian = math.radians(angle)
        s = radius * math.sin(radian)
        c = radius * math.cos(radian)
        face_list.append(shapes.Circle(
            x + c, y + s, point, color=GREEN, batch=batch, group=foreground))


def create_face(rad):
    face(0, 360, 6, W // 2, H // 2, rad)
    face(0, 360, 36, W // 2 - rad * 0.42, H // 2 + rad * 0.2, rad // 6)
    face(0, 360, 36, W // 2 + rad * 0.42, H // 2 + rad * 0.2, rad // 6)
    face(210, 340, 10, W // 2, H // 2, rad * 0.6)


face_list = []
create_face(RADIUS)
# end Face


def update(dt, collision=False):
    if game[0]:
        # motion Quads
        if rectangle_list[0].vertices[0] > -W * 4 + 1:
            for ver in rectangle_list:
                ver.vertices = [
                    elem - SPEED * dt if e % 2 == 0 else elem
                    for e, elem in enumerate(ver.vertices)]
        # motion Face
        else:
            for i in face_list:
                i.x += speed_fase

        # collision
        for ver in rectangle_list:
            nx = max(ver.vertices[0], min(face_list[0].x - RADIUS, ver.vertices[0] + SIZE))
            ny = max(ver.vertices[1], min(face_list[0].y, ver.vertices[1] + SIZE))
            dtc = (nx - (face_list[0].x - RADIUS)) ** 2 + (ny - face_list[0].y) ** 2
            if dtc <= RADIUS ** 2 and face_list[0].x < W - SIZE - speed_fase:
                penalty[0] += 1
                penalty_label.text = f'Штраф: {penalty[0]}'
                collision = True

        if collision:
            if face_list[0].color != RED:
                for i in face_list:
                    i.color = RED
        else:
            if face_list[0].color != GREEN:
                for i in face_list:
                    i.color = GREEN
    else:
        # game over
        game_over_label.text = 'GAME OVER'
        game_start_label.text = 'press Enter for a new game'
        face_list.clear()
        create_face(RADIUS * 7)


def new_game():
    penalty[0] = 0
    penalty_label.text = f'Штраф: {penalty[0]}'
    game_over_label.text = ''
    game_start_label.text = ''
    for ver in rectangle_list:
        ver.delete()
    rectangle_list.clear()
    face_list.clear()
    create_quads(0, 0)
    create_face(RADIUS)
    stream.start()
    game[0] = True


def audio_callback(indata, frames, time, status):
    volume = numpy.linalg.norm(indata)
    if face_list[0].x >= W - SIZE - speed_fase:
        game[0] = False
        stream.stop(ignore_errors=True)
    elif face_list[0].y >= H - RADIUS:
        for i in face_list:
            i.y -= speed_fase
    elif face_list[0].y <= RADIUS:
        for i in face_list:
            i.y += speed_fase
    elif volume > 4:
        for i in face_list:
            i.y += volume * 0.4
    else:
        for i in face_list:
            i.y -= speed_fase


@my_window.event
def on_key_press(symbol, modifiers):
    if symbol == window.key.ENTER and not game[0]:
        new_game()


@my_window.event
def on_draw():
    my_window.clear()
    program.bind()
    batch.draw()
    program.unbind()


if __name__ == '__main__':
    gl.glClearColor(*BG_COLOR)  # цвет окна
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    stream = sd.InputStream(callback=audio_callback)
    with stream:
        clock.schedule_interval(update, 1 / 30.0)
        app.run()
    stream.close(ignore_errors=True)
