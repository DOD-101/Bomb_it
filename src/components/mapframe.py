"""
Implements the MapFrame class.

Status: Working
"""


from pygame import Rect, Surface, draw, image, transform

import shared
from utils.utils import strToRGB


class MapFrame:
    """
    This class contains all information for a "tile"
    with a map in it on the Map selection screen.
    """

    row = 0
    instance_num = 0
    instances = {}

    def __init__(
        self, surface: Surface, frame_color, map_path: str, instance_name
    ) -> None:
        MapFrame.instance_num += 1
        MapFrame.instances[instance_name] = self
        self.surface = surface
        self.size = 200
        self.instance_name = instance_name
        self.x_pos, self.y_pos = self._getPos()
        self.frame_color = strToRGB(frame_color)
        self.map_path = map_path

        self.draw()

    def _getPos(self):
        instance_num = MapFrame.instance_num
        row = 0
        while instance_num > shared.map_row_length:
            instance_num -= shared.map_row_length
            row += 1

        cords = [instance_num, row]
        converted_cords = [
            shared.MAP_QUEUE_W + 20 + (20 + self.size) * cords[0],
            20 + (20 + self.size) * cords[1],
        ]
        return converted_cords

    def draw(self):
        """Draws the Mapframe to self.surface."""
        frame = Rect(self.x_pos, self.y_pos, self.size, self.size)
        map_preview = image.load(self.map_path)
        map_preview = transform.scale(map_preview, (160, 160))
        draw.rect(self.surface, self.frame_color, frame)
        self.surface.blit(map_preview, (self.x_pos + 20, self.y_pos + 20))

    def checkMouseOver(self, mouse_pos) -> bool:
        """Checks if the given mouse_position is over the button."""
        return (
            self.x_pos <= mouse_pos[0] <= self.x_pos + self.size
            and self.y_pos <= mouse_pos[1] <= self.y_pos + self.size
        )

    def onClick(self):
        """Appends the map for the Mapframe to shared.map_queue."""
        shared.map_queue.appendMap(self.instance_name)

    def checkANDExecute(self, mouse_pos) -> None:
        """
        Runs the onClick function if the provided mouse position
        is over the Mapframe.
        """
        if self.checkMouseOver(mouse_pos):
            self.onClick()
