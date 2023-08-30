from PIL import Image
import os

def convert_dir_to_rgb(dir: str, make_copy: bool = True, convert_all: bool = False):
    """Converts all .png files in a dir to use the RGB color mode.
    dir must be an absolute path. 
    If make_copy is set to False it will simply override all the files otherwise it will make a copy with the filename prefixed by "rgb_\"
    If convert_all is set to True it will convert all images, including those which are already RGB.
    """
    for filename in os.listdir(dir):
        if filename.endswith(".png"):
            with Image.open(os.path.join(dir, filename)) as img:
                if not img.mode == "RGB" or convert_all:
                    rgb_image = img.convert("RGB")
                    # Save the converted image
                    if make_copy:
                        rgb_image.save(os.path.join(dir, f"rgb_{filename}"))
                    else:
                        rgb_image.save(os.path.join(dir, f"{filename}"))

def px_to_colordict(image: Image.Image, allowed_colors: list | set == None):
    """Return a dict with the keys being the color and each keys value being a set with the cords of all pixels that have that color. 
    If allowed_colors is left as None all colors will be allow otherwise it will only add colors to the dict which have one of those colors. 
    All values entered and returned must be/are RGB."""
    image = image.convert("RGB")        
    px = image.load()
    
    colordict = {}
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if px[x,y] in allowed_colors or allowed_colors == None:
                if px[x,y] in colordict.keys():
                    colordict[px[x,y]].add((x,y))
                else:
                    colordict[px[x,y]] = set((x,y))
    
    return colordict

