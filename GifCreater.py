
import json
from owslib.wms import WebMapService
from owslib.util import ServiceException
from urllib2 import HTTPError
import datetime
import tempfile
import os
from images2gif import writeGif
from PIL import Image
import shutil

class GifCreater(object):
   """docstring for GifCreater"""
   def __init__(self, config):
      super(GifCreater, self).__init__()
      self.image_factor = 50
      self.title = config['title']
      self.start_date = config['start_date']
      self.end_date = config['end_date']
      self.st_obj = datetime.datetime.strptime(self.start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
      self.end_obj = datetime.datetime.strptime(self.end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
      self.data_source = config['data_source']
      self.wms_layer = config['wms_layer']
      self.geo_bounds = tuple(map(float,config['geo_bounds'].split(',')))
      self.image_size = (int(abs(self.geo_bounds[0] - self.geo_bounds[2]))*self.image_factor,int(abs(self.geo_bounds[1] - self.geo_bounds[3]))*self.image_factor)
      print self.geo_bounds
      if self.test_wms():
         self.wms = WebMapService(self.data_source)
      else:
         raise Exception('Layer requested does not exist in wms')
      if not self.test_times():
         raise Exception('Start or End date requested are not available from WMS service')
      self.dates_available = self.get_dates()
      self.request_dates = self.get_requested_dates()
      self.temp_dir = tempfile.mkdtemp()
      self.final_out_dir = "/local1/data/scratch/create_gif/images/"




   def test_wms(self):
      try:
         wms = WebMapService(self.data_source)
         return self.wms_layer in wms.contents
      except HTTPError, e:
         print "WMS url given is incorrect", e
      except ServiceException, e:
         print "Service Exception", e

   def test_times(self):
      return (self.start_date and self.end_date in self.wms.contents[self.wms_layer].timepositions)


   def get_image(self, date, outname):
      img = self.wms.getmap(layers=[self.wms_layer], srs="EPSG:4326", bbox=self.geo_bounds, size=self.image_size, format="image/png", transparent=True, time=date)
      out = open(os.path.join(self.temp_dir,outname), 'wb')
      out.write(img.read())
      out.close

   def get_dates(self):
      dates_available = [datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ") for x in map(str.strip, self.wms.contents[self.wms_layer].timepositions)]
      return dates_available

   def get_requested_dates(self):
      dates = []
      for d in self.dates_available:
         if self.st_obj <= d <= self.end_obj:
            dates.append(d)
      return dates

   def get_images(self):
      for d in self.request_dates:
         d_str = datetime.datetime.strftime(d,"%Y-%m-%dT%H:%M:%S.%fZ")
         print "creating image for %s" % d_str
         self.get_image(d_str, d_str.replace(':', '_')+'.png')

   def gen_gif(self):
      file_names = sorted((fn for fn in os.listdir(self.temp_dir) if fn.endswith('.png')))
      print file_names
      images = [Image.open(os.path.join(self.temp_dir,fn)) for fn in file_names]
      filename = "blah.gif"
      writeGif(os.path.join(self.final_out_dir, filename), images, duration=1, dispose=2)
      shutil.rmtree(self.temp_dir)
      return self.create_gif_descriptor()

   def create_gif_descriptor(self):
      output = {
      "frames" : map(self.de_date, self.request_dates),
      "geo_bounds" : self.geo_bounds
      }
      return json.dumps(output)

   def de_date(self, date):
      return datetime.datetime.strftime(date, "%Y-%m-%dT%H:%M:%S.%fZ")

if __name__ == '__main__':
   with open('config.json', 'r') as f:
      config = json.load(f)
   gc = GifCreater(config)
   #print gc.wms
   #gc.get_image()
   print gc.image_size
   print len(gc.get_dates())
   print len(gc.get_requested_dates())
   gc.get_images()
   print gc.gen_gif()
