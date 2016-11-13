import os, base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


game_path = 'file:///Users/junjiek/Downloads/Project/t-rex-runner/index.html'
chrome_options = Options()
chrome_options.add_argument("--disable-web-security")
driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)

driver.get(game_path)
for i in range(10):
	elem = driver.find_element_by_tag_name('body')
	elem.send_keys(Keys.SPACE)
	time.sleep(1)
	canvas = driver.find_element_by_id('game-canvas')

	# get the canvas as a PNG base64 string
	canvas_base64 = driver.execute_script("return arguments[0].toDataURL().substring(22);", canvas)
	# # decode
	canvas_png = base64.b64decode(canvas_base64)

	# # save to a file
	with open(r"canvas" + str(i) + ".png", 'wb') as f:
	    f.write(canvas_png)
