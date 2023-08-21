import typing

def center(item_width: float | int = 0, item_height: float | int = 0, parent_width: float | int = 0, parent_height: float | int = 0, center_direction: typing.Literal["horizontal", "vertical", "both"] = "both"):
    def horizontal():
        return ((parent_width - item_width) / 2)
    def vertical():
        return ((parent_height - item_height) / 2)
    
    match(center_direction):
        case("horizontal"):
            return horizontal()
        case("vertical"):
            return vertical()
        case("both"):
            return (horizontal(), vertical())
        case(_):
            raise ValueError(f"{center_direction} is an invalid value for center_direction")
        
def strtoRGB(colorStr: str) -> tuple:
    if type(colorStr) == str: 
        colorStr = colorStr.lower()
        match(colorStr):
            case('white'):
                colorStr = (255,255,255)
            case('black'):
                colorStr = (0,0,0)
            case('red'):
                colorStr = (255,0,0)
            case('green'):
                colorStr = (0,255,0)
            case('blue'):
                colorStr = (0,0,255)
            case('armygreen'):
                colorStr = (75, 83, 32)
            case('explosionorange'):
                colorStr = (255, 102, 0)
            case(_):
                raise ValueError(f"Color str:{colorStr} doesn't exist!")
    return colorStr

