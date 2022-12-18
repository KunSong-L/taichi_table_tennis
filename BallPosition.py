import taichi as ti


def BP():
    gui_width = 300
    gui_height = gui_width+100
    gui_circle_y = gui_width/2/gui_height
    gui = ti.GUI('击球点选择', (gui_width, gui_height))
    # = gui.slider('Radius', 1, 50, step=1)
    xcoor = gui.label('X-coordinates')
    ycoor = gui.label('Y-coordinates')
    okay = gui.button('OK')

    xcoor.value = 0.5
    ycoor.value = gui_circle_y
    # radius.value = 10

    while gui.running:
        for e in gui.get_events(gui.PRESS):
            if e.key == gui.ESCAPE:
                gui.running = False
            elif e.key == 'a':
                if ((xcoor.value - 0.51) ** 2 + (ycoor.value - 0.5) ** 2) < 0.33 ** 2:
                    xcoor.value -= 0.01
                # else:
                #     xcoor.value +=0.01

            elif e.key == 'd':
                if ((xcoor.value - 0.49) ** 2 + (ycoor.value - 0.5) ** 2) < 0.33 ** 2:
                    xcoor.value += 0.01
            elif e.key == 's':
                if ((xcoor.value - 0.5) ** 2 + (ycoor.value - 0.51) ** 2) < 0.33 ** 2:
                    ycoor.value -= 0.01
            elif e.key == 'w':
                if ((xcoor.value - 0.5) ** 2 + (ycoor.value - 0.49) ** 2) < 0.33 ** 2:
                    ycoor.value += 0.01
            elif e.key == okay or e.key == 'Return':
                print('OK clicked')
                gui.clear()
                return xcoor.value, ycoor.value*gui_height/gui_width
                # gui.running = False
        gui.text('abc', (0.5, 0.9), color=0xFFFFFF)
        gui.background_color = 0x3CB310
        gui.circle((0.5, gui_circle_y), color=0xFFFFFF, radius=gui_width/2)
        gui.circle((xcoor.value, ycoor.value), color=0xFF0000, radius=5)
        gui.show()
