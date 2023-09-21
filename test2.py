import sys, pygame
import checkbox
pygame.init()
pygame.font.init()

class Window:
    def __init__(self):
        self.running = True
        self.width=int(960)
        self.height=int(1080)
        self.screen=pygame.display.set_mode([self.width,self.height])
        my_outline_color = (78, 137, 202)
        my_check_color = (22, 61, 105)
        my_font_size = 25
        my_font_color = (39, 111, 191)
        my_text_offset = (28, 1)
        my_font = "Open Sans"

        self.boxes=[]
        self.idnum = 1

        self.add_checkbox(self.screen, self.get_box_x(), self.get_box_y(self.idnum), caption="checkbox",
            outline_color=my_outline_color, check_color=my_check_color, font_size=my_font_size, font_color=my_font_color,
            text_offset=my_text_offset, font=my_font)

        self.add_checkbox(self.screen, self.get_box_x(), self.get_box_y(self.idnum), caption="checkbox for something",
            outline_color=my_outline_color, check_color=my_check_color, font_size=my_font_size, font_color=my_font_color,
            text_offset=my_text_offset, font=my_font)

        self.add_checkbox(self.screen, self.get_box_x(), self.get_box_y(self.idnum), caption="checkbox for something else",
            outline_color=my_outline_color, check_color=my_check_color, font_size=my_font_size, font_color=my_font_color,
            text_offset=my_text_offset, font=my_font)

    def add_checkbox(self, surface, x, y, color=(230, 230, 230), caption="", outline_color=(0, 0, 0),
                 check_color=(0, 0, 0), font_size=22, font_color=(0, 0, 0), text_offset=(28, 1), font='Ariel Black'):
        self.idnum+=1

        box = checkbox.Checkbox(self.screen, x, y, self.idnum, color, caption,
            outline_color, check_color, font_size, font_color, text_offset, font)

        self.boxes.append(box)

    #Not working
    def remove_checkbox(self, id_to_remove):
        for box in self.boxes:
            if box.idnum == id_to_remove:
                self.boxes.remove(box)
        self.idnum-=1

    def get_box_x(self):
        return 50

    def get_box_y(self, y):
        return y*30

    def start(self):
        input_box = pygame.Rect(100, 100, 140, 32)
        while self.running:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for box in self.boxes:
                        box.update_checkbox(event)

                    #debugging
                    for box in self.boxes:
                        if box.checked:
                            print(str(box.caption)+ " is checked")
                        if not box.checked:
                            print(str(box.caption)+ " is not checked")

            #draw to screen
            pygame.draw.rect(self.screen, pygame.Color(255, 255, 255), [0,0,self.width,self.height])

            for box in self.boxes:
                box.render_checkbox()

            #refresh
            pygame.display.flip()

window = Window()
window.start()