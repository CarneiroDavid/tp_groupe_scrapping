import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless=new")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
# Initialiser le driver
driver = webdriver.Chrome(options=options)
driver.get("https://www.imdb.com")
time.sleep(2)

try:
    # Trouver le bouton par classe
    bouton = driver.find_element(By.CLASS_NAME, "icb-btn")
    bouton.click()
    print("Bouton cliqué avec succès.")
except Exception as e:
    print(f"Erreur : {e}")

time.sleep(2)

# Boutou recherche
bouton_search = driver.find_element(By.ID, "suggestion-search-button")
bouton_search.click()
time.sleep(2)

# Filtre film etc
bouton_filtre = driver.find_element(By.CLASS_NAME, "ipc-chip.ipc-chip--on-base")
bouton_filtre.click()
time.sleep(2)

# Accordeon Type de film
filtre_film = driver.find_element(By.CSS_SELECTOR, "[data-testid='accordion-item-titleTypeAccordion']")
actions = ActionChains(driver)
actions.move_to_element(filtre_film).perform()
filtre_film.click()
time.sleep(2)

# type de film
select_film = driver.find_element(By.CSS_SELECTOR, "[data-testid='test-chip-id-movie']")
actions.move_to_element(select_film).perform()
select_film.click()
time.sleep(2)

# note IMDb
filtre_note = driver.find_element(By.CSS_SELECTOR, "[data-testid='accordion-item-ratingsAccordion']")
actions.move_to_element(filtre_note).perform()
filtre_note.click()
time.sleep(2)

# Saisi des notes
input_note_imdb = driver.find_element(By.CSS_SELECTOR, "[data-testid='imdbratings-start']")
actions.move_to_element(input_note_imdb).perform()
input_note_imdb.send_keys("7.0")

input_haute_imdb = driver.find_element(By.CSS_SELECTOR,"[data-testid='imdbratings-end']")
actions.move_to_element(input_haute_imdb).perform()
input_haute_imdb.send_keys("10.0")
time.sleep(2)

# Saisi des nb vote
filtre_review = driver.find_element(By.CSS_SELECTOR, "[data-testid='accordion-item-numOfVotesAccordion']")
actions.move_to_element(filtre_review).perform()
filtre_review.click()
time.sleep(2)

input_review_basse = driver.find_element(By.CSS_SELECTOR,"[data-testid='numofvotes-min']")
actions.move_to_element(input_review_basse).perform()
input_review_basse.send_keys("5000")

input_review_haute = driver.find_element(By.CSS_SELECTOR,"[data-testid='numofvotes-max']")
actions.move_to_element(input_review_haute).perform()
input_review_haute.send_keys("2147483647")
time.sleep(2)

# Validation des filtres
bouton_validation = driver.find_element(By.CSS_SELECTOR, "[data-testid='adv-search-get-results']")
bouton_validation.click()
time.sleep(5)

# Tri des résultats
tri_par_nb_eval = driver.find_element(By.ID, "adv-srch-sort-by")
driver.execute_script("arguments[0].scrollIntoView();", tri_par_nb_eval)
tri_par_nb_eval.click()
time.sleep(2)

# Select du nombre d'eval
select_nb_eval = driver.find_element(By.CSS_SELECTOR, "[value='USER_RATING_COUNT']")
select_nb_eval.click()
time.sleep(2)

# Ordre decroissant
ordre_desc  = driver.find_element(By.CSS_SELECTOR, "[data-testid='test-sort-order']")
ordre_desc.click()
time.sleep(2)

# Charger plus d'éléments
try:
    charger_plus = driver.find_element(By.CLASS_NAME, "ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--button-radius.ipc-btn--on-accent2.ipc-text-button")
    actions.move_to_element(charger_plus).perform()
    charger_plus.click()
    time.sleep(2)
except Exception as e:
    print("Aucun bouton 'Charger plus' trouvé.")

# Sauvegarder les liens
film_links = []
films = driver.find_elements(By.CSS_SELECTOR, "a.ipc-title-link-wrapper")
for film in films:
    href = film.get_attribute("href")
    film_links.append(href)

print(f"Nombre de liens sauvegardés : {len(film_links)}")

# Écrire les données dans un fichier CSV
with open("films_data.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Titre", "Lien", "Genres", "Année", "Durée"])

    for i, link in enumerate(film_links):
        try:
            print(f"Accès au film {i + 1} : {link}")
            
            driver.get(link)
            time.sleep(3)  

            titre = "Titre non disponible"
            try:
                titre = driver.find_element(By.CSS_SELECTOR, "h1").text
                print(f"Titre : {titre}")
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")

            genres = []
            try:
                div_genre = driver.find_elements(By.CSS_SELECTOR, ".ipc-chip.ipc-chip--on-baseAlt")
                genres = [genre.text for genre in div_genre]
                print(f"Genres récupérés : {genres}")
            except Exception as e:
                print(f"Erreur lors de la récupération des genres : {e}")

            annee = "inconnu"
            try:
                annee = driver.find_element(By.CSS_SELECTOR, "a[href*='releaseinfo']").text
                print(f"Année : {annee}")
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")

            durree = "inconnu"
            try:
                parent_div = driver.find_element(By.CSS_SELECTOR, "div.sc-70a366cc-0.bxYZmb")
                durree = parent_div.find_element(By.CSS_SELECTOR, "ul.ipc-inline-list > li:nth-child(3)").text
                print(f"Durée : {durree}")
            except Exception as e:
                print(f"Erreur lors de la récupération du titre : {e}")
            writer.writerow([titre, link, ", ".join(genres), annee, durree])
        
            driver.back()
            time.sleep(3)  
        except Exception as e:
            print(f"Erreur avec le lien {i + 1} : {e}")

driver.quit()
