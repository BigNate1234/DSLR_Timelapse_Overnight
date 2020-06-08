'''
||
|| @file 	DSLR_timelapse.py
|| @version	1.0
|| @author	Nathaniel Furman
|| @contact	nfurman@ieee.org
||
|| @description
|| | Control a DSLR camera using the 'gphoto2' library for an overnight
|| | time lapse.
|| #
||
|| @license
|| | This library is free software; you can redistribute it and/or
|| | modify it under the terms of the GNU Lesser General Public
|| | License as published by the Free Software Foundation; version
|| | 2.1 of the License.
|| |
|| | This library is distributed in the hope that it will be useful,
|| | but WITHOUT ANY WARRANTY; without even the implied warranty of
|| | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
|| | Lesser General Public License for more details.
|| |
|| | You should have received a copy of the GNU Lesser General Public
|| | License along with this library; if not, write to the Free Software
|| | Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
|| #
||

Additional credit to GitHub user 'IronSenior' for python functions to
control aspects of the gphoto2 library. Thank you for your work, as it
greatly helped here.

'''

import os
import datetime
import time
import gphoto2 as gp

# @author IronSenior
# Added error exceptions
def configured_camera():
  # Getting the camera
  context = gp.Context()
  cam = gp.Camera()
  try:
    cam.init(context)
  except gp.GPhoto2Error as err:
    print('Camera could not detect camera, please check connection and try again.')
    print(err)
    exit()

  print(cam.get_summary(context))
  return cam

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def check_range(value):
    ivalue = int(value)
    if ivalue < 0 or ivalue > 24:
        raise argparse.ArgumentTypeError("%s is an invalid hour value" % value)
    return ivalue

# TODO:
# Include offset and reverse offset in timing

def find_city():
  from astral import LocationInfo
  from astral.geocoder import database, lookup
  db = database()
  unconfirmed = True
  try:
    while unconfirmed:
      loc = input('What is your location/city? ')
      try:
        city = lookup(loc, db)
      except KeyError:
        print('ERROR: Did not find that location, please try again.')
        continue
      print('Found:',city)
      try:
        while True:
          result = input('Does this look correct (y/n)? ')
          if result.lower() == 'n':
            break # Go back to outer while loop to choose city
          elif result.lower() == 'y':
            unconfirmed = False
            break
          else:
            print('Please choose yes or no')
      except KeyboardInterrupt:
        print('\nExiting...')
        exit()
  except KeyboardInterrupt:
    print("\nSorry you didn't find your city, please try setting a start time.")
    exit()
  return city

def take_photos(cam):
  while True:
    counter = 0
    capt_name = 'capt_' + f'{counter:04}' + '.jpg'
    counter += 1
    curr_time = datetime.datetime.today()
    # Check if ran past time
    if curr_time.hour > end_time:
      print('\n\nFinished taking photos. Enjoy!\n\n')
      break
    # Take the photo
    # Adapted from IronSenior
    cam_file_path = gp.check_result(gp.gp_camera_capture(cam, gp.GP_CAPTURE_IMAGE))
    print('Internal image (camera) file path: {0}/{1}'.format(file_path.folder,file_path.name))
    target = os.path.join(curr_formatted, capt_name)
    camera_file = gp.check_result(gp.gp_camera_file_get(cam, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL))
    gp.check_result(gp.gp_file_save(camera_file, target))
    print('Captured image ', capt_name, ', sleeping now.')
    try:
      time.sleep(delay)
    except KeyboardInterrupt:
      print('Detected KeyboardInterrupt, exiting...')
  
  gp.check_result(gp.gp_camera_exit(cam))




if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Take time lapse photos.')
  parser.add_argument('d', metavar='delay', type=check_positive, 
        help='The delay (in minutes) between each photo.')
  parser.add_argument('--start-time', default=-1, type=check_range,
        help='Set which hour (24 hour time) to start, default is sunset.')
  parser.add_argument('--end_time', default=-1, type=check_range,
        help='Set which hour (24 hour time) to end, default is sunrise.')
  parser.add_argument('--offset', default=0, type=check_positive,
        help='Set time in minutes after "start_time" to take first photo.')
  parser.add_argument('--reverse-offset', default=0, type=check_positive,
        help='Set time in minutes  before "end_time" to stop taking photos.')
  parser.add_argument('--img-size', default=10, type=check_positive,
  	help='Approximate image size in MB.')
  args = parser.parse_args()
  delay = args.d
  start_time = args.start_time
  end_time = args.end_time
  offset = args.offset
  reverse_offset = args.reverse_offset
  img_size = args.img_size

  if start_time == -1 or end_time == -1:
    from astral.sun import sun
    city = find_city()
    s = sun(city.observer, datetime.date.today(), tzinfo=city.timezone) 
    if start_time == -1:
      start_time = s['sunset'].hour
      print('Start time set to:\t', start_time)
    if end_time == -1:
      end_time = s['sunrise'].hour
      print('End time set to:\t', end_time) 

  # Calculated time taking photos
  time_on = (24 - start_time) + end_time
  print('Taking photos for ', time_on, ' hours.')
  
  # Calculate approximate number of photos being taken
  num_pics = time_on * 60 / delay
  print('Taking approximately ', num_pics, 'pictures.')
  
  # Calculate approximate memory being used
  mem_usage = num_pics * img_size / 1000
  print('Using approximately ', mem_usage, 'GB total.')
  
  try:
    while True:
      result = input('Are these values okay (y/n)? ')
      if result.lower() == 'n':
        exit()
      elif result.lower() == 'y':
        break
      else:
        print('Please choose yes or no')
  except KeyboardInterrupt:
    print('\nExiting...')
    exit()

  # Set up directory 
  curr_day = datetime.datetime.today()
  curr_formatted = 'pics_' + curr_day.isoformat()[:16]
  os.mkdir(curr_formatted)
  # Check if before start_time
  curr_hour = curr_day.hour
  if curr_hour < start_time:
    curr_min = curr_day.minute
    sleep_time = 60*(start_time - curr_hour) - curr_min
    print('Not time to start, sleeping for ', sleep_time, 'minutes')
    try:
      time.sleep(sleep_time)
    except KeyboardInterrupt:
      print('\nWoken from sleep, exiting...')
      exit()

  cam = configured_camera()
  take_photos(cam)

'''
|| @changelog
|| | 1.0 2020-06-07 - Nathaniel Furman : Initial release
|| #
'''
