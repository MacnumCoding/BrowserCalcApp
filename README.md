## About This Project
This is my attempt at starting to learn about browser applications, i foresee a future where i add to this project so it may one day cover as much functionality as the Windows Calculator, but it is not a priority.

## Running The Project
To run this project, there are some prerequisits, one is setting up an API id and key from nutritionix, i've set it up so it fetches them from ones system environment if you have created them with the given names "NUTRITIONIX_APP_ID" and "NUTRITIONIX_APP_KEY".

Secondly, to create an executable of this project, make use of pyinstaller (pip install pyinstaller) and use pyinstaller --onefile --name=YourAppName main.py to create an executable that you may create shortcuts to to access from wherever you set it.

## Plans For The Future
I want to make it so the application wont rely on every user having their own API id and key, and im currently researching what is the proper way to do so, current ideas are:
- Fetch Nutritinionix food item database to accompany product (Downside: Would take up a lot of space, seems unwise)
- Include a smaller database of generic food items for searching (Downside: Users might not find desired item)
- Allow users to register food items in database for easy reuse (Downside: Users might be discouraged as this requires them to research food items many times, Upside: Users can get as specific with their preferences and niche uses as they want.)