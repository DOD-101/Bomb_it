"""
Implements the MapFrame class.

Status: Working
"""


from utils.utils import strToRGB
from uuid import uuid4
from pygame import Surface, image, transform, Rect, draw
import shared

class MapFrame:
    row = 0
    instance_num = 0
    instances = {}
    def __init__(self, surface: Surface, frame_color, map_path: str, instance_name) -> None:
        MapFrame.instance_num += 1
        MapFrame.instances[instance_name] = self
        self.surface = surface
        self.size = 200
        self.instance_name = instance_name
        self.x_pos, self.y_pos= self._get_pos()
        self.frame_color = strToRGB(frame_color)
        self.map_path = map_path

        self.draw()

    def _get_pos(self):
        instance_num = MapFrame.instance_num
        row = 0
        while instance_num > shared.map_row_length:
            instance_num -= shared.map_row_length
            row += 1

        cords = [instance_num, row]
        converted_cords = [shared.MAP_QUEUE_W + 20 + (20 + self.size) * cords[0], 20 + (20 + self.size) * cords[1]]
        return converted_cords

    def draw(self):
        frame = Rect(self.x_pos, self.y_pos, self.size, self.size)
        map_preview = image.load(self.map_path)
        map_preview = transform.scale(map_preview, (160, 160))
        draw.rect(self.surface, self.frame_color, frame)
        self.surface.blit(map_preview, (self.x_pos + 20, self.y_pos + 20))

    def checkmouseover(self, mouse_pos) -> bool:
        if self.x_pos <= mouse_pos[0] <= self.x_pos + self.size and self.y_pos <= mouse_pos[1] <= self.y_pos + self.size:
            return True
        else:
            return None

    def onclick(self):
        shared.map_queue.appendMap(self.instance_name)

    def checkANDExecute(self, mouse_pos) -> None:
        if self.checkmouseover(mouse_pos) == True:
            self.onclick()