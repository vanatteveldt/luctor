from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os


def create_thumbnail(inf, size=300):
    im = Image.open(inf)
    im.thumbnail((size,size), Image.ANTIALIAS)
    f = BytesIO()
    im.save(f, format='jpeg')
    return bytes


def save_thumbnail(source_field, destination_field, size=300):
    inf = source_field.file.name
    fn = os.path.splitext(os.path.basename(inf))[0]
    outf = "{fn}-small-{size}.jpg".format(**locals())
    bytes = create_thumbnail(inf, size)
    destination_field.save(outf, ContentFile(bytes))


def set_thumbnails(picture):
    save_thumbnail(picture.image, picture.image_small, size=300)
    save_thumbnail(picture.image, picture.image_thumb, size=50)
    picture.save()
    print( picture.image_thumb.url)
