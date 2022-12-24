import taichi as ti


def BP():
    gui_width = 300
    gui_height = gui_width+150
    gui_circle_x = 0.5
    gui_circle_y = gui_width/2/gui_height
    gui = ti.GUI('击球点选择', (gui_width, gui_height))
    # = gui.slider('Radius', 1, 50, step=1)
    xcoor = gui.label('X-coordinates')
    ycoor = gui.label('Y-coordinates')
    okay = gui.button('OK')

    angle = gui.slider("Angle Choose", 0, 90, step=1)

    xcoor.value = 0.5
    ycoor.value = gui_circle_y
    # radius.value = 10
    move_step = 0.005
    move_step_0 = 0.005
    delta_step = 0.001
    last_key = ''

    while gui.running:
        for e in gui.get_events(gui.PRESS):
            if e.key == gui.ESCAPE:
                gui.running = False
            elif e.key == 'a':
                if last_key == 'a':
                    move_step = move_step + delta_step
                else:
                    move_step = move_step_0

                if ((xcoor.value -move_step- gui_circle_x) ** 2/gui_circle_x**2 + (ycoor.value - gui_circle_y) ** 2/gui_circle_y**2) < 1:
                    xcoor.value -= move_step
                    last_key = 'a'
                # else:
                #     xcoor.value +=move_step

            elif e.key == 'd':
                if last_key == 'd':
                    move_step = move_step + delta_step
                else:
                    move_step = move_step_0

                if ((xcoor.value +move_step- gui_circle_x) ** 2/gui_circle_x**2 + (ycoor.value - gui_circle_y) ** 2/gui_circle_y**2) < 1:
                    xcoor.value += move_step
                    last_key = 'd'


            elif e.key == 's':
                if last_key == 's':
                    move_step = move_step + delta_step
                else:
                    move_step = move_step_0

                if ((xcoor.value - gui_circle_x) ** 2/gui_circle_x**2 + (ycoor.value -move_step- gui_circle_y) ** 2/gui_circle_y**2) < 1:
                    ycoor.value -= move_step
                    last_key = 's'

            elif e.key == 'w':
                if last_key == 'w':
                    move_step = move_step + delta_step
                else:
                    move_step = move_step_0

                if ((xcoor.value - gui_circle_x) ** 2/gui_circle_x**2 + (ycoor.value +move_step- gui_circle_y) ** 2/gui_circle_y**2) < 1:
                    ycoor.value += move_step
                    last_key = 'w'

            elif e.key == okay or e.key == 'Return':
                print('OK clicked')
                gui.clear()
                return xcoor.value, ycoor.value*gui_height/gui_width, angle.value
                # gui.running = False
        gui.text('abc', (0.5, 0.9), color=0xFFFFFF)
        gui.background_color = 0x3CB310
        gui.circle((0.5, gui_circle_y), color=0xFFFFFF, radius=gui_width/2)
        gui.circle((xcoor.value, ycoor.value), color=0xFF0000, radius=5)
        gui.show()
