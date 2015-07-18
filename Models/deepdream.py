import os
from batcountry import BatCountry
from PIL import Image
import numpy as np

from lib.Worker.Models.uv_document import UnveillanceDocument
from vars import EmitSentinel, ASSET_TAGS
from conf import ANNEX_DIR, getConfig

class DeepDream(UnveillanceDocument):
	def __init__(self, _id=None, inflate=None):

		super(DeepDream, self).__init__(_id=_id, inflate=inflate)

	def get_image(self, file_name=None):
		if file_name is None:
			file_name = self.file_name
		else:
			file_name = os.path.join(self.base_path, file_name)

		print "GETTING IMAGE AT PATH %s" % os.path.join(ANNEX_DIR, file_name)
		return Image.open(os.path.join(ANNEX_DIR, file_name))

	def downsample(self):
		img = self.get_image()
		(width, height) = img.size

		asset_path = self.addAsset(None, "dream_1.jpg", \
			tags=[ASSET_TAGS['DLXDD_DD']], description="Derivative of original asset")

		MAX_HEIGHT = 576
		MAX_WIDTH = 720

		if width > MAX_WIDTH or height > MAX_HEIGHT:
			ratio = min((MAX_WIDTH / width), (MAX_HEIGHT / height))
			new_size = ((width * ratio), (height * ratio))

			img = img.resize(new_size, Image.ANTIALIAS)
		
		img.save(os.path.join(ANNEX_DIR, asset_path), 'JPEG')
		return True

	def iterate(self):
		THIS_DIR = os.getcwd()
		os.chdir(os.path.join(ANNEX_DIR, self.base_path))

		try:
			iter_num = len(self.getAssetsByTagName(ASSET_TAGS['DLXDD_DD']))

			bc = BatCountry(os.path.join(getConfig('caffe_root'), "models", "bvlc_googlenet"))
			img = bc.dream(np.float32(self.get_image(file_name="dream_%d.jpg" % iter_num)))
			bc.cleanup()

			os.chdir(THIS_DIR)

			iter_num += 1
			dream = Image.fromarray(np.uint8(img))
			asset_path = self.addAsset(None, "dream_%d.jpg" % iter_num, \
				tags=[ASSET_TAGS['DLXDD_DD']], description="deep dream iteration")

			if asset_path is not None:
				dream.save(os.path.join(ANNEX_DIR, asset_path))
				return True
		
		except Exception as e:
			print "ERROR ON ITERATION:"
			print e, type(e)

		return False

	def giffify(self):
		from fabric.api import settings, local

		avi_path = self.getAssetsByTagName(ASSET_TAGS['DLXDD_AVI'])
		gif_path = self.getAssetsByTagName(ASSET_TAGS['DLXDD_GIF'])
		ffmpeg = getConfig('ffmpeg')

		if avi_path is None:
			avi_path = self.addAsset(None, "deepdream_gif.avi",
				tags=[ASSET_TAGS['DLXDD_AVI']], description="avi of DeepDream gif")		

		with settings(warn_only=True):
			# image sequence to .avi {ATTENTION FORMATTING!}
			avi_path_tmp = avi_path.replace(".avi", "_tmp.avi")

			local("%s -y -f image2 -i dream_%d.jpg %s" % (ffmpeg, avi_path_tmp))

			# slow down .avi
			local("%s -y -i %s -filter:v \"setpts=10.0*PTS\" %s" % (ffmpeg, avi_path_tmp, avi_path))

			# burn to gif
			if gif_path is None:
				gif_path = self.addAsset(None, "deepdream.gif",
					tags=[ASSET_TAGS['DLXDD_GIF']], description="gif of DeepDream")

			local("%s -y -i %s -pix_fmt rgb24 %s" % (ffmpeg, avi_path, gif_path))

			return True

		return False

