"""Galaxy on Fire 2 ship skin renderer

EARLY UNFINISHED PROTOTYPE

Written by Trimatix
"""
from PIL import Image, ImageChops, ImageOps
import subprocess
# import sys
from typing import List, Dict
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
CWD = os.getcwd()

script_path = os.path.dirname(os.path.realpath(__file__))
RENDER_TEMP_DIR = script_path + os.sep + "temp"
RENDER_ARGS_PATH = script_path + os.sep + "render_vars"


debugPrint = False
if os.getenv("DEBUG_MODE") is not None:
    if os.getenv("DEBUG_MODE").upper() == "TRUE":
        debugPrint = True

if debugPrint:
    print("SCRIPT_PATH", SCRIPT_PATH, sep=": ")
    print("RENDER_TEMP_DIR", RENDER_TEMP_DIR, sep=": ")
    print("RENDER_ARGS_PATH", RENDER_ARGS_PATH, sep=": ")

class RenderFailed(Exception):
    pass



##### UTIL FUNCTIONS #####

def trim(im : Image) -> Image:
    """Crop image to content, written by neouyghur: https://stackoverflow.com/a/48605963/11754606

    :param Image im: The image to crop
    :return: im, with all surrounding empty space removed
    :rtype: Image
    """
    if debugPrint:
        print("inside trim()")
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def ensureImageMode(tex : Image, mode="RGBA") -> Image:
    """Ensure the passed image is in a given mode. If it is not, convert it.
    https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes

    :param Image tex: The image whose mode to check
    :param str mode: The mode to ensure and convert to if needed
    :return: tex if it is of the given mode. tex converted to mode otherwise.
    :rtype: Image
    """
    if debugPrint:
        print("inside ensureImageMode()")
    return tex if tex.mode == mode else tex.convert(mode)


def compositeTextures(outTexPath : str, shipPath : str, textures : Dict[int, str], disabledLayers: List[int]):
    """Combine a list of textures into a single image, with respect to masks provided in shipPath.

    :param str outTexPath: Path to which the resulting texture should be saved, including file name and extension
    :param str shipPath: Path to the bbShip being rendered
    :param Dict[int, str] textures: Dictionary associating mask indices to texture file paths to composite. If a mask index is not in textures or disabledLayers, the default texture for that region will be used. The first element corresponds to the underlayer to render beneith the ship's base texture (foreground elements). All (currently 2) remaining textures are overlayed with respect to the ship's texture region masks.
    :param List[int] disabledLayers: List of texture regions to 'disable' - setting them to the bottom texture. TODO: Instead of doing this by recompositing the bottom texture, just iterate through disabled layers and apply masks. Apply bottom texture at the end.
    """
    if debugPrint:
        print("inside compositeTextures()")
    # Load and combine the base texture and under layer
    workingTex = ensureImageMode(Image.open(textures[0]))
    baseTex = ensureImageMode(Image.open(shipPath + os.sep + "skinBase.png"))
    workingTex = Image.alpha_composite(workingTex, baseTex)

    maxLayerNum = max(max(textures), max(disabledLayers)) if disabledLayers else max(textures)

    # For each layer number
    for maskNum in range(1,maxLayerNum+1):
        if maskNum in textures:
            # If skinning this region, load the texture with the corresponding index
            newTex = ensureImageMode(Image.open(textures[maskNum]))
        elif maskNum in disabledLayers:
            # If disabling this region, load in the bottom texture
            newTex = ensureImageMode(Image.open(textures[0]))
        else:
            # If neither skinning nor masking this region, skip it
            continue

        # Check that a corresponding mask exists for the model
        try:
            mask = Image.open(shipPath + os.sep + "mask" + str(maskNum) + ".jpg")
        except FileNotFoundError:
            print("WARNING: Attempted to " + ("render" if maskNum in textures else "disable") + " texture region " + str(maskNum) + " but mask" + str(maskNum) + ".jpg does not exist. shipPath:" + shipPath)
        else:
            # Load in the mask
            # Gimp and pillow use opposite shades to represent opacity in a mask, so invert the mask
            mask = ensureImageMode(ImageOps.invert(mask), "L")
            # Apply the texture with respect to the mask
            workingTex = Image.composite(workingTex, newTex, mask)

    workingTex.convert("RGB").save(outTexPath)


def setRenderArgs(args : List[str]):
    """Pass arguments to the render via the arguments file

    :param List[str] args: List of arguments to write to file
    """
    if debugPrint:
        print("inside setRenderArgs()")
    with open(SCRIPT_PATH + os.sep + "render_vars","w") as f:
        for arg in args:
            f.write(arg + "\n")


def start_render():
    if debugPrint:
        print("inside start_render()")
    subprocess.call("blender -b \"" + SCRIPT_PATH + os.sep + "cube.blend\" -P \"" + SCRIPT_PATH + os.sep + "_render.py\"", shell=True)


async def renderShip(skinName : str, shipPath : str, shipModelName : str, textures : Dict[int, str], disabledLayers: List[int], res_x : int, res_y : int, full=False): # TODO: Add 'useBaseTexture' argument. Pass to render_vars. If true, should bypass skinBase (for 'full' skins that don't use skinBase)
    """Render the given ship model with the specified skin layer(s).
    The resulting image is cropped to content and saved in shipPath + "/skins/" + skinName.jpg

    :param str skinName: The name of the skin being rendered. Depicts the name of the output file.
    :param str shipPath: Path to the bbShip being rendered. Must contain shipModelName
    :param str shipModelName: The name of the model file to render. Not a path. Must be contained within shipPath
    :param Dict[int, str] textures: Dictionary associating mask indices to texture file paths to composite. If a mask index is not in textures or disabledLayers, the default texture for that region will be used. The first element corresponds to the underlayer to render beneith the ship's base texture (foreground elements). All (currently 2) remaining textures are overlayed with respect to the ship's texture region masks.
    :param List[int] disabledLayers: List of texture regions to 'disable' - setting them to the bottom texture.
    :param int res_x: The width in pixels of the render resolution. This is not the the width of the final image, as empty space around the rendered object is cropped out automatically.
    :param int res_y: The height in pixels of the render resolution. This is not the the height of the final image, as empty space around the rendered object is cropped out automatically.
    :param bool full: When True, ignore all texture regions and base textures included with the ship, and render the first element in textures as the texture for the model. (Default False)
    """
    if debugPrint:
        print("inside renderShip()")
    # Generate render arguments
    current_model = shipPath + os.sep + shipModelName
    render_output_file = shipPath + os.sep + "skins" + os.sep + skinName + "-RENDER.png"
    texture_output_file = shipPath + os.sep + "skins" + os.sep + skinName + ".jpg"

    if res_x > 1920:
        raise ValueError("Attempted to render an image above 1080p (width=" + str(res_x) + ")")
    if res_y > 1080:
        raise ValueError("Attempted to render an image above 1080p (height=" + str(res_y) + ")")
    if res_x < 352:
        raise ValueError("Attempted to render an image below 240p (width=" + str(res_x) + ")")
    if res_y < 240:
        raise ValueError("Attempted to render an image below 240p (height=" + str(res_y) + ")")
    render_resolution = str(res_x) + "x" + str(res_y)

    if not full:
        compositeTextures(texture_output_file, shipPath, textures, disabledLayers)

    # Pass the arguments to the renderer
    setRenderArgs([render_resolution, render_output_file, current_model, textures[0] if full else texture_output_file])
    # Render the requested model
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ThreadPoolExecutor(), start_render)

    # Load the newly rendered image
    try:
        bg = Image.open(render_output_file)
    except FileNotFoundError:
        raise RenderFailed()
    # Crop it to content
    new_im = trim(bg)
    # Save it back to file
    new_im.save(render_output_file)
