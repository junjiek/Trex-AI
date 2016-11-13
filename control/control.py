import os, base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# path to t-rex game html page
game_path = 'file://' + os.path.abspath(os.path.join(os.getcwd(), '..')) + '/game/index.html'
chrome_options = Options()
# disable security in Chrome to Allow-Control-Allow-Origin.
chrome_options.add_argument("--disable-web-security")
driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)

driver.get(game_path)
for i in range(10):
	elem = driver.find_element_by_tag_name('body')
	# Jump
	elem.send_keys(Keys.SPACE)
	time.sleep(1)

	canvas = driver.find_element_by_id('game-canvas')
	# Get the canvas as a PNG base64 string and decode
	canvas_base64 = driver.execute_script("return arguments[0].toDataURL().substring(22);", canvas)
	canvas_png = base64.b64decode(canvas_base64)
	# save to a file
	with open(r"canvas" + str(i) + ".png", 'wb') as f:
	    f.write(canvas_png)
