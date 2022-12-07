# https://github.com/pyglet/pyglet/blob/master/pyglet/graphics/__init__.py?ysclid=lb9jogeint679420239
# https://docs.pyglet.org/en/latest/programming_guide/graphics.html
# from pyglet.graphics.shader import Shader, ShaderProgram
import pyglet
from pyglet import gl, graphics, shapes
from importlib import metadata
import warnings

warnings.filterwarnings('ignore')

ver = int(metadata.version('pyglet')[0])
print(ver)

program = shapes.get_default_shader()

W, H = 780, 630
SIZE = 30
SPEED_POLYGON = 30
BG_COLOR = (.75, .75, .75, 1)

window = pyglet.window.Window(width=W, height=H, caption='Test')
window.set_location(1, 30)
window.set_mouse_visible(visible=False)
# fps_display = pyglet.window.FPSDisplay(window=window)

batch = graphics.Batch()
background = graphics.Group(0)
foreground = graphics.Group(1)

playing_field = [
    '----------------------------------------------------------------------------------------------------------------------------------',
    '-                           -                          --                        ---                                  -          -',
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

# start QUADS
rectangle_list = []
x = y = 0
c = 1  # 1 если 'i', 255 если 'Bn'
for row in playing_field:
    for col in row:
        if col == '-':
            rectangle_list.append(program.vertex_list(
                6, gl.GL_TRIANGLES, batch=batch, group=background,
                vertices=('f', [x, y, x + SIZE, y, x + SIZE, y + SIZE, x, y, x + SIZE, y + SIZE, x, y + SIZE]),
                colors=('i', (0, 0, c, c, c, 0, c, c, 0, c, 0, c, c, c, 0, c, 0, 0, c, c, c, 0, 0, c))))
        x += SIZE
    y += SIZE
    x = 0
# end QUADS


def update(dt):
    # motion QUADS
    if rectangle_list[0].vertices[0] > -W * 4 + 1:
        for ver in rectangle_list:
            ver.vertices = [
                elem - SPEED_POLYGON * dt if e % 2 == 0 else elem
                for e, elem in enumerate(ver.vertices)]


@window.event
def on_draw():
    window.clear()
    # program.bind()
    batch.draw()
    # program.unbind()
    # fps_display.draw()


if __name__ == '__main__':
    gl.glClearColor(*BG_COLOR)  # цвет окна
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    pyglet.clock.schedule_interval(update, 1 / 30.0)
    program.bind()
    pyglet.app.run()
    program.unbind()  # ?
