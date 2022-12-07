import pyglet
from pyglet import gl, graphics, shapes

program = shapes.get_default_shader()

W, H = 780, 630
SIZE = 100
BG_COLOR = (.75, .75, .75, 1)

window = pyglet.window.Window(width=W, height=H, caption='Test')
window.set_location(1, 30)

batch = graphics.Batch()
background = graphics.Group(0)
foreground = graphics.Group(1)


x, y = 200, 200
x1, y1 = 100, 100
width, height = 300, 300
x2 = x1 + width
y2 = y1 + height
n = 6
vlist2 = program.vertex_list(
    n, gl.GL_TRIANGLES, batch=batch, group=foreground, translation='f', vertices='f',
    colors=('Bn', (0, 0, 255, 255, 255, 0, 255, 255, 0, 255, 0, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255)))
# vlist2.translation[:] = [x, y] * n
vlist2.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y1, x2, y2, x1, y2]


@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == '__main__':
    program.bind()
    gl.glClearColor(*BG_COLOR)  # цвет окна
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    pyglet.app.run()
    program.unbind()
