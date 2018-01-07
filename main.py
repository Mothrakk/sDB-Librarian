# Written in Python 3.6
# https://github.com/Mothrakk

from os import getcwd 					 # get current working directory
cwd = getcwd()
from sys import path
path.insert(0, cwd + r"\dependencies")   # extend PYTHONPATH

from json import loads # json parsing
from selenium.webdriver import PhantomJS # headless browser for JS work
from requests import get 				 # regular GET requests, used in getting steam lib
from bs4 import BeautifulSoup as soup    # html parsing

def read_config_values():
	# Attempt to read from config.txt
	try:
		with open(cwd + r"\config\config.txt", 'r') as file:
			contents = file.read().strip().split('\n')
	except FileNotFoundError:
		raise Exception("The config file is missing.")
	# Attempt to retrieve a valid return amount
	try:
		return_amount = int(contents[2].split(':')[1])
	except Exception:
		raise ValueError("Bad return amount. Edit config.txt.")
	#
	steam_id = contents[0].split(':')[1]
	api = contents[1].split(':')[1]
	user_categories = [item.lower().strip() for item in contents[4].split(':')[1].split(',')]
	if len(user_categories) == 1 and user_categories[0] == "":
		user_categories = []
	return [steam_id, api, return_amount, user_categories]

def check_user_categories_validity(user_categories):
	with open(cwd + r"\config\valid_categories.txt", 'r') as file:
		valid_categories = file.read().split('\n')
	for user_category in user_categories:
		if user_category not in valid_categories:
			raise ValueError("{} is not a valid category. Please refer to valid_categories.txt.".format(user_category))

def fetch_user_library(api, steam_id):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	response = get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json".format(api, steam_id), headers=headers)
	# Check for errors in the response
	parsed_html = soup(response.content, "lxml")
	try:
		if parsed_html.h1.text == "Internal Server Error":
			raise ValueError("Internal server error. Bad SteamID? Check config.txt.")
		if parsed_html.h1.text == "Forbidden":
			raise ValueError("Access forbidden. Bad API key? Check config.txt.")
	except AttributeError: # This just means that there is no h1.text, aka error-free
		pass
	# Fetch the library
	parsed_json = loads(response.content)
	user_library = []
	for i in range(parsed_json["response"]["game_count"]):
		user_library.append(str(parsed_json["response"]["games"][i]["appid"]))
	return user_library

def fetch_sales(driver, user_library, return_amount, user_categories):
	# Declare some variables
	first_page_completed = False # This is to avoid going to the next page on the first iteration
	output = [] # This will be written to games.txt
	#
	driver.get(r"https://steamdb.info/sales/")
	# Sort/filter the games
	if not len(user_categories): # == 0
		print("Sorting games by SteamDB's rating system..")
		rating_button = driver.find_element_by_css_selector("""th.sorting_desc:nth-child(6) > span:nth-child(1)""")
		rating_button.click()
		rating_button.click()
	else:
		print("Applying category filters..")
		driver.find_element_by_css_selector("""div.fancy-select:nth-child(4) > div:nth-child(2) > button:nth-child(1)""").click()
		categories_table = driver.find_element_by_css_selector("""div.fancy-select:nth-child(4) > div:nth-child(2) > div:nth-child(2) > ul:nth-child(2)""")
		category_elements = categories_table.find_elements_by_tag_name("span")
		for element in category_elements:
			if element.text.lower().strip() in user_categories:
				element.click()
		driver.find_element_by_css_selector("""#js-filter-submit""").click()
		potential_error_msg = driver.find_element_by_css_selector(""".panel-heading""")
		if potential_error_msg.text == "Nothing found matching your filters":
			raise Exception("No games were found that match your filters")

	#
	print()
	first_game_on_page = ""
	while len(output) < return_amount:
		if first_page_completed: # Go to the next page
			driver.find_element_by_css_selector("""#DataTables_Table_0_next > a:nth-child(1)""").click()
		sales_containers = driver.find_elements_by_class_name("app")
		if sales_containers[0].find_element_by_class_name("b").text.strip() == first_game_on_page:
			print("Out of games!")
			break
		else:
			first_game_on_page = sales_containers[0].find_element_by_class_name("b").text.strip()
		for sale_container in sales_containers:
			sale_game_id = sale_container.get_attribute("data-appid")
			if sale_game_id not in user_library: # Comparison of user library to the game
				game_name = sale_container.find_element_by_class_name("b").text.strip()
				discount, price = [element.text.strip() for element in sale_container.find_elements_by_tag_name("td")[3:5]]
				final = "{}. {} | {} ({})".format(len(output)+1, game_name, price, discount)
				print(final)
				output.append(final)
				if len(output) >= return_amount: # Break prematurely if return amount has been reached
					break
		first_page_completed = True
	return "\n".join(output)

def main():
	steam_id, api, return_amount, user_categories = read_config_values()
	print("SteamID:", steam_id)
	print("API key:", api)
	print("Return amount:", return_amount)
	if len(user_categories): # > 0
		check_user_categories_validity(user_categories)
		print("Categories:", "; ".join(user_categories))
	print()

	print("Fetching your Steam library..")
	user_library = fetch_user_library(api, steam_id)
	print("Found {} in your library.".format(len(user_library)))

	print("Opening PhantomJS..")
	driver = PhantomJS(cwd + r"\dependencies\phantomJS\phantomjs.exe", service_log_path=cwd + r"\dependencies\phantomJS\ghostdriver.log")

	print("Opening SteamDB..")
	output = fetch_sales(driver, user_library, return_amount, user_categories)

	driver.quit()
	with open("games.txt", 'w', encoding='utf-8') as file:
		file.write(output)
	input("\nDone. I also wrote the games to a text file.")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print("Error:", e)
		input()
		exit()