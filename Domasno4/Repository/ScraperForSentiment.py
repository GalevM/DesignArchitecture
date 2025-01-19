import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

base_url = "https://www.mse.mk/mk/issuer/"

issuers = ['komercijalna-banka-ad-skopje/',
           'alkaloid-ad-skopje/', 'vv-tikves-ad-skopje/', 'vitaminka-ad-prilep/', 'granit-ad-skopje/',
           'ds-smith-ad-skopje/', 'zito-luks-ad-skopje/', 'zk-pelagonija-ad-bitola/', 'internesnel-hotels-ad-skopje/',
           'makedonijaturist-ad-skopje/', 'makoteks-ad-skopje/', 'makosped-ad-skopje/', 'makpetrol-ad-skopje/',
           'makstil-ad-skopje/',
           'replek-ad-skopje/', 'rz-inter-transsped-ad-skopje/', 'rz-inter-transsped-ad-skopje/',
           'rz-uslugi-ad-skopje/',
           'skopski-pazar-ad-skopje/', 'stopanska-banka-ad-bitola/', 'teteks-ad-tetovo/', 'ttk-banka-ad-skopje/',
           'tutunski-kombinat-ad-prilep/', 'fersped-ad-skopje/', 'hoteli-metropol-ohrid/', 'agromehanika-ad-skopje/',
           'ading-ad--skopje/', 'angropromet-tikvesanka-ad-kavadarci/', 'arcelormittal-(hrm)-ad-skopje/',
           'automakedonija-ad-skopje/',
           'bim-ad-sveti-nikole/', 'blagoj-tufanov-ad-radovis/', 'vabtek-mzt-ad-skopje/', 'veteks-ad-veles/',
           'gd-tikves-ad-kavadarci/',
           'geras-cunev-konfekcija-ad-strumica/', 'geras-cunev-trgovija-ad-strumica/', 'grozd-ad-strumica/',
           'gtc-ad-skopje/',
           'debarski-bani-–capa-ad--debar/', 'dimko-mitrev-veles/', 'evropa-ad-skopje/', 'zas-ad-skopje/',
           'zito-karaorman-ad-kicevo/', 'zito-polog-ad-tetovo/', 'interpromet-ad-tetovo/',
           'klanica-so-ladilnik-ad-strumica/',
           'blagoj-gorev-ad-veles/', 'liberti-ad-skopje/', 'lotarija-na-makedonija-ad-skopje/',
           'osiguruvane-makedonija-ad-skopje---viena-insurens-grup/',
           'makedonski-telekom-ad-–-skopje/', 'makpromet-ad-stip/', 'mermeren-kombinat-ad-prilep/',
           'mzt-pumpi-ad-skopje/', 'moda-ad-sveti-nikole/',
           'nematali-ograzden-ad-strumica/', 'nlb-banka-ad-skopje/', 'nova-stokovna-kuka-ad-strumica/',
           'oilko-kda-skopje/', 'okta-ad-skopje/',
           'oranzerii-hamzali-strumica/', 'patnicki-soobrakaj-transkop-ad-bitola/', 'pekabesko-ad-kadino-ilinden/',
           'pelisterka-ad-skopje/',
           'popova-kula-ad-demir-kapija/', 'prilepska-pivarnica-ad-prilep/', 'rade-koncar--aparatna-tehnika-ad-skopje/',
           'rz-ekonomika-ad-skopje/',
           'rz-tehnicka-kontrola-ad-skopje/', 'rudnici-banani-ad-skopje/', 'sigurnosno-staklo-ad-prilep/',
           'sileks-ad-kratovo/', 'slavej--ad-skopje/',
           'sovremen-dom-ad-prilep/', 'stokopromet-ad-skopje/', 'stopanska-banka-ad-skopje/',
           'strumicko-pole-s-vasilevo/', 'tajmiste-ad-kicevo/',
           'teal-ad--tetovo/', 'tehnokomerc-ad-skopje/', 'trgotekstil-maloprodazba-ad-skopje/',
           'triglav-osiguruvane-ad-skopje/', 'trudbenik-ad-ohrid/',
           'ugotur-ad-skopje/', 'unibanka-ad-skopje/', 'fabrika-karpos-ad-skopje/', 'fakom-ad-skopje/',
           'fzc-11-ti-oktomvri-ad-kumanovo/',
           'fruktal-mak-ad-skopje/', 'fustelarko-borec-ad-bitola/', 'cementarnica-usje-ad-skopje/',
           'centralna-kooperativna-banka-ad-skopje/']


with open('../../DesignArchitecture-master/Domashno3/scraped_data_sentiment.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Issuer', 'Title', 'Content'])

    def scrape_issuer(issuer):
        driver.get(base_url + issuer)
        time.sleep(3)

        try:
            titleSelector = driver.find_element(By.CSS_SELECTOR, "div.col-md-8.title")
            title = titleSelector.text
        except Exception as e:
            print(f"Грешка при земање на насловот за {issuer}: {e}")
            title = "Неуспешно да се најде наслов"

        try:
            news_items = driver.find_elements(By.CSS_SELECTOR, "div.container-seinet > a")
        except Exception as e:
            print(f"Грешка при наоѓање на линковите за {issuer}: {e}")
            return

        for item in news_items:
            link = item.get_attribute("href")
            driver.get(link)
            time.sleep(8)

            try:
                content = driver.find_element(By.CSS_SELECTOR, "div.text-left.ml-auto.mr-auto.col-md-11")
                paragraphs = content.find_elements(By.TAG_NAME, "p")
                for p in paragraphs:
                    print(p.text)
                full_content = "".join([p.text for p in paragraphs])
            except Exception as e:
                print("Грешка при скрепување на содржината:", e)
                full_content = "Неуспешно да се земе содржина"

            csvwriter.writerow([issuer, title, full_content])

            driver.back()
            time.sleep(2)

    for issuer in issuers:
        scrape_issuer(issuer)

driver.quit()
