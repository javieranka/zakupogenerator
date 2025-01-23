import backend.zakupogenerator as zakupogenerator

data = """https://aniagotuje.pl/przepis/ciasto-czekoladowe-z-jablkami
https://aniagotuje.pl/przepis/ciasto-czekoladowe-ze-sliwkami
https://aniagotuje.pl/przepis/brownie-z-maslem-orzechowym
"""

zakupogenerator.return_result_shopping_list_json(data)
