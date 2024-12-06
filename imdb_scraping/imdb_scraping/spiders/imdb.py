import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import csv

class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["imdb.com"]
    start_urls = ["https://www.imdb.com/"]

    def __init__(self, *args, **kwargs):
        super(ImdbSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()
        self.movie_data = []

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(1.5)

        # Refuser les cookies (si présent)
        try:
            decline_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="reject-button"]')
            self.log("Bouton 'Decline' done.")
            decline_button.click()
            time.sleep(1)
        except Exception as e:
            self.log("Bouton 'Decline' introuvable.")

        try:
            # Page de recherche IMDB
            search_button = self.driver.find_element(By.ID, "suggestion-search-button")
            ActionChains(self.driver).move_to_element(search_button).click(search_button).perform()
            time.sleep(1)

            # Récupérer le HTML mis à jour (bouton de recherche pour films et séries gérer par du javascript)
            updated_html = self.driver.page_source
            updated_response = HtmlResponse(url=self.driver.current_url, body=updated_html, encoding='utf-8')
            yield scrapy.Request(
                url=self.driver.current_url,
                callback=self.parse_advanced_search_page,
                dont_filter=True,
                meta={'selenium_response': updated_response}
            )
        except Exception as e:
            self.log(f"Erreur lors du clic sur le bouton de recherche : {e}")

    def parse_advanced_search_page(self, response):
        selenium_response = response.meta.get('selenium_response')
        self.driver.get(selenium_response.url)
        time.sleep(2)

        try:
            advanced_link = self.driver.find_element(By.CSS_SELECTOR, "a[data-testid='advanced-search-chip-tt']")
            advanced_url = advanced_link.get_attribute("href")

            self.driver.get(advanced_url)
            time.sleep(2)

            self.apply_advanced_filters()
            self.fetch_results()
        except Exception as e:
            self.log(f"Erreur lors de la navigation vers la recherche avancée : {e}")

    def apply_advanced_filters(self):
        try:
            # Accordion 'Type'
            accordion = self.driver.find_element(By.ID, "titleTypeAccordion")
            accordion.click()
            time.sleep(1)
            btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='test-chip-id-movie']")
            btn.click()
            time.sleep(1)

            # Accordion 'Ratings'
            accordion = self.driver.find_element(By.ID, "ratingsAccordion")
            accordion.click()
            time.sleep(1)
            rating_min = self.driver.find_element(By.CSS_SELECTOR, "input[name='imdb-ratings-max-input']")
            rating_min.send_keys("7")
            rating_max = self.driver.find_element(By.CSS_SELECTOR, "input[name='imdb-ratings-min-input']")
            rating_max.send_keys("10")
            time.sleep(1)

            # Accordion 'Numbre of Votes'
            accordion = self.driver.find_element(By.ID, "numOfVotesAccordion")
            accordion.click()
            time.sleep(1)
            votes_min = self.driver.find_element(By.CSS_SELECTOR, "input[name='numofvotes-max-input']")
            votes_min.send_keys("1000")
            votes_max = self.driver.find_element(By.CSS_SELECTOR, "input[name='numofvotes-min-input']")
            votes_max.send_keys("1000000")
            time.sleep(1)

        except Exception as e:
            self.log(f"Erreur lors de l'application des filtres : {e}")

    def fetch_results(self):
        try:
            # Application des filtres pour la recherche
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='adv-search-get-results']")
            submit_button.click()
            time.sleep(3)

            # Ordonner par nombre de reviews
            sort_select = self.driver.find_element(By.ID, "adv-srch-sort-by")
            sort_select.click()
            time.sleep(3)
            sort_option = self.driver.find_element(By.CSS_SELECTOR, "option[value='USER_RATING_COUNT']")
            sort_option.click()
            self.log("Tri par nombre d'évaluations sélectionné.")
            time.sleep(3)

            # Ordre décroissant
            sort_order_button = self.driver.find_element(By.ID, "adv-srch-sort-order")
            sort_order_button.click()
            self.log("Tri par ordre croissant activé.")
            time.sleep(5)

            # Charge 50 films supplémentaires
            # load_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.ipc-see-more__button")
            # load_more_button.click()
            # self.log("50 films supplémentaires chargés.")
            # time.sleep(3)

            self.extract_movie_links()
        except Exception as e:
            self.log(f"Erreur lors de la récupération des résultats : {e}")

    # Récupère les links des films
    def extract_movie_links(self):
        try:
            results_html = self.driver.page_source
            results_response = HtmlResponse(url=self.driver.current_url, body=results_html, encoding='utf-8')

            self.movie_links = results_response.css(
                "li.ipc-metadata-list-summary-item a.ipc-lockup-overlay::attr(href)"
            ).getall()[:25]
            self.movie_links = [f"https://www.imdb.com{link}" for link in self.movie_links]

            self.log("Liens des films extraits.")
            for link in self.movie_links:
                self.driver.get(link)
                time.sleep(2)
                self.extract_movie_details(link)
        except Exception as e:
            self.log(f"Erreur lors de l'extraction des liens : {e}")

    # Parcourt les links pour récupérer les données sur les pages des films
    def extract_movie_details(self, url):
        try:
            movie_html = self.driver.page_source
            movie_response = HtmlResponse(url=self.driver.current_url, body=movie_html, encoding='utf-8')

            title = movie_response.css("span.hero__primary-text::text").get()
            year = movie_response.css("a[href*='releaseinfo']::text").get()
            duration = movie_response.css("li.ipc-inline-list__item::text").get()
            imdb_rating = movie_response.css("span.sc-d541859f-1::text").get()
            genres = movie_response.css("div.ipc-chip-list__scroller span.ipc-chip__text::text").getall()

            self.movie_data.append({
                "Title": title,
                "Year": year,
                "Duration": duration,
                "IMDB_Rating": imdb_rating,
                "Genres": ", ".join(genres)
            })
            self.log(f"Détails extraits pour {title}.")
        except Exception as e:
            self.log(f"Erreur lors de l'extraction des détails pour {url} : {e}")

    def closed(self, reason):
        self.driver.quit()
        self.save_to_csv()

    def save_to_csv(self):
        # Créer un DataFrame Pandas à partir des données
        df = pd.DataFrame(self.movie_data)
        df.to_csv("movies.csv", index=False, encoding="utf-8")
        self.log("Données sauvegardées dans movies.csv.")