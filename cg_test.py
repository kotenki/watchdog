from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

#print(cg.get_price(ids=tokens_string.lower(), vs_currencies="usd"))
f = open("cg_all_tokens.txt", "a")

for i in cg.get_coins_list():
    f.write(i["id"] + " : "+ i["symbol"])
    f.write("\n")


f.close()
