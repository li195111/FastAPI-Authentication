'''
Items Models
© 2022 - 酷喬伊科技有限公司 QChoice Tech, Ltd. All rights reserved.
'''
from .base import IBase

# Item
class IItem(IBase):
  is_private: bool = False


class Item(IItem):
  id: int
  owner_id: int

  class Config:
    orm_mode = True


# Media
class MediaItem(Item):
  blob_url: str


# Image
class IImage(IItem):
  pass


class ImageCreate(IImage):
  pass


class Image(IImage, MediaItem):
  pass


# Video
class IVideo(IItem):
  pass


class VideoCreate(IVideo):
  pass


class Video(IVideo, MediaItem):
  pass

