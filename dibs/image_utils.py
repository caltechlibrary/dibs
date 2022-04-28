'''
image_utils.py: miscellaneous image-handling utilities for DIBS

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from io import BytesIO
from PIL import Image


# Exported functions
# .............................................................................

def as_jpeg(byte_array):
    '''Convert an image, stored as an array of bytes, into JPEG format.'''
    img = Image.open(BytesIO(byte_array))
    img = img.convert('RGB')
    buffer = BytesIO()
    img.save(buffer, 'JPEG')
    img.close()
    return buffer.getvalue()
