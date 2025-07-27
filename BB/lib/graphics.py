from PIL import Image, ImageDraw, ImageEnhance, ImageChops, ImageFilter
from typing import Dict, Union, Tuple, List
import random

def paddedScale(baseImage: Image.Image, w: int, h: int, fill: Union[str, int, Tuple[int]], offsetMode: str = "CENTRE",
                offset: int = 0, newMode: str = None) -> Image.Image:
    """Scale `baseImage` down to (`w`, `h`), but without distorting/stretching the image. Instead, if the image is of a
    different aspect ratio, the empty space around it is filled with `fill` - "black bars".

    offsetMode is a keyword string, being one of:
        "MIN" - Place the image in the top-left
        "MAX" - Place the image in the bottom-right
        "CENTRE" - Place the image in the centre
        "PX" - Place the image `offset` pixels from the top-left.

    :param Image.Image baseImage: The image to scale
    :param int w: The new desired image width
    :param int h: The new desired image height
    :param fill: The colour to fill empty space around the image with
    :type fill: Union[str, int, Tuple[int]]
    :param str offsetMode: Where to place the scaled image with respect to the empty space, as above (Default "CENTRE")
    :param int offset: If `offsetMode` is "PX", the number of pixels from the top-left to place the image (Default 0)
    :param str newMode: Mode override for the new image (Default baseImage.mode)
    :rtype: Image.Image
    """
    # Create new canvas
    if newMode is None:
        newMode = baseImage.mode
    elif baseImage.mode != newMode:
        baseImage = baseImage.convert(newMode)
    newImage = Image.new(newMode, (w, h), fill)

    # Calculate scaled size of baseImage by matching the longest side to the desired length of that side
    if baseImage.width < baseImage.height:
        newSize = (int(baseImage.width * (h / baseImage.height)), h)
    else:
        newSize = (w, int(baseImage.height * (w / baseImage.width)))
    scaledImage = baseImage.resize(newSize)

    # Calculate where to paste the scaled image
    if scaledImage.size == (w, h) or offsetMode == "MIN":
        pasteOrigin = (0, 0)
    elif offsetMode == "MAX":
        pasteOrigin = (w - scaledImage.width, h - scaledImage.height)
    elif offsetMode == "CENTRE":
        pasteOrigin = (int((w - scaledImage.width) / 2), int((h - scaledImage.height) / 2))
    elif offsetMode == "PX":
        if baseImage.width < baseImage.height:
            pasteOrigin = (offset, 0)
        else:
            pasteOrigin = (0, offset)
    else:
        raise ValueError(f"Unknown offsetMode: {offsetMode}")

    # Paste image and return
    scaledImage = padImage(scaledImage, pasteOrigin[1], w - (pasteOrigin[0]+scaledImage.width),
                            h - (pasteOrigin[1]+scaledImage.height), pasteOrigin[0], fill)
    newImage = Image.composite(scaledImage, newImage, scaledImage)
    # newImage.paste(scaledImage, pasteOrigin, scaledImage)
    return newImage


def dropShadow(baseImage: Image.Image, opacity: float, offset: Tuple[int, int], blurIterations: int) -> Image.Image:
    """Return a copy of baseImage with a drop shadow placed beneath.
    If the shadow goes out of bounds of the image, the image is NOT padded to account for this.
    You should isntead pass your image pre-padded.

    :param Image.Image baseImage: Image to apply the shadow to
    :param float opacity: Opacity of the shadow, between 0 and 1
    :param offset: Tuple specifying the x offset of the shadow followed by the y offset
    :type offset: Tuple[int, int]
    :param int blurIterations: The number of times to apply the blur filter to the shadow
    :return: baseImage pasted on top of a drop shadow. The image is "RGBA" mode.
    :rtype: Image.Image
    """
    shadow = ImageEnhance.Brightness(ImageChops.offset(baseImage, offset[0], offset[1])).enhance(0).convert("RGBA")
    if opacity < 1:
        shadowAlpha = ImageEnhance.Brightness(shadow.getchannel("A")).enhance(opacity)
        shadow.putalpha(shadowAlpha)
    for _ in range(blurIterations):
        shadow = shadow.filter(ImageFilter.BLUR)
    return Image.composite(baseImage, shadow, baseImage)

    


def cropAndScale(baseImage: Image.Image, w: int, h: int) -> Image.Image:
    """Crop baseImage to match the aspect ratio of (w, h), and then scale the result to match (w, h).
    Cropping is performed from the top-left of the image. The original image is not altered, a new one is created.

    :param Image.Image baseImage: Image to crop/resize
    :param int w: The desired new image width (px)
    :param int h: The desired new image height (px)
    :return: A copy of baseImage, resized to (w, h), but by cropping instead of stretching
    :rtype: Image.Image
    """
    # If sizes are the same, do nothing
    if baseImage.size == (w, h):
        return baseImage

    # If aspect ratios are different, crop
    if baseImage.width / baseImage.height != w / h:
        # Crop the longest side
        if baseImage.width / baseImage.height > w / h:
            desiredWidth = (w / h) * baseImage.height
            newImage = baseImage.crop((0, 0, int(desiredWidth), baseImage.height))
        else:
            desiredHeight = baseImage.width / (w / h)
            newImage = baseImage.crop((0, 0, baseImage.width, int(desiredHeight)))

        # If no scaling is needed, return cropped image
        if newImage.width == w:
            return newImage
    else:
        newImage = baseImage

    # Scale image
    return newImage.resize((w, h))



def padImage(pil_img: Image.Image, top: int, right: int, bottom: int, left: int,
        colour: Union[str, int, Tuple[int]]) -> Image.Image:
    """Pads an image, placing extra space around it and filling that space with the given colour.
    This is done by creating a new image, the original is not modified.

    https://note.nkmk.me/en/python-pillow-add-margin-expand-canvas/

    :param Image.Image pil_Image: The original image
    :param int top: Amount of extra space to add on top of the image, in pixels
    :param int right: Amount of extra space to add on the right of the image, in pixels
    :param int bottom: Amount of extra space to add beneith the image, in pixels
    :param int left: Amount of extra space to add on the left of the image, in pixels
    :param colour: Colour to fill the new empty space with. The type of this parameter depends on pil_image.mode
    :type colour: Union[str, int, Tuple[int]]
    """
    result = Image.new(pil_img.mode, (pil_img.size[0] + right + left, pil_img.size[1] + top + bottom), colour)
    result.paste(pil_img, (left, top))
    return result
