from bs4 import BeautifulSoup 
import requests

game_name = input("Enter the game name: ") 
search_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ','+')}"
response = requests.get(search_url)

soup = BeautifulSoup(response.text,"html.parser")

wrapper = soup.find("div", id="search_resultsRows")

# Get the first result
result = wrapper.find("a", class_="search_result_row")

gameTitle = result.find("span").text
gameOriginalPrice = result.find("div", class_="discount_original_price")
gameDiscountPer = result.find("div", class_="discount_pct")
gameFinalPrice = result.find("div", class_="discount_final_price")


print(gameTitle)
print(f"Original price: {gameOriginalPrice.text}")
print(f"Discount amount: {gameDiscountPer.text}")
print(f"Final price with discount: {gameFinalPrice.text}")