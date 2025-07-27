import importlib
from ..exceptions import CodecLoadException

# Discover codecs

try:
    from . import EtcPakCodec
except CodecLoadException:
    pass

try:
    from . import Tex2ImgCodec
except CodecLoadException:
    pass

try:
    from . import RawCodec
except CodecLoadException:
    pass
