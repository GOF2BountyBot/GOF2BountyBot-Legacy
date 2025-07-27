import importlib
from ..exceptions import CodecLoadException

# Discover codecs

try:
    import EtcPakCodec
except CodecLoadException:
    pass

try:
    import Tex2ImgCodec
except CodecLoadException:
    pass

try:
    import RawCodec
except CodecLoadException:
    pass
