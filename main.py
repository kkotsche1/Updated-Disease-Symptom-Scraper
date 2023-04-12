from bs4 import BeautifulSoup
import requests
import unicodedata

import spacy

import re
import json
url = "https://www.nhs.uk/conditions/"
spacy = spacy.load("en_core_web_sm")
all_stopwords = spacy.Defaults.stop_words
soup = BeautifulSoup(requests.get(url).text, "html.parser")
tokenizer = spacy.tokenizer
links = soup.find_all(class_= "nhsuk-list-panel__link")
y  = 0
final_results = []
for link in links:
    symptoms_for_dictionary = []
    no_stop_words = []
    final_symptoms = []
    url = "https://www.nhs.uk" +link["href"]
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    symptom_link = soup.find("a", string=re.compile("Symptoms"))
    name = soup.find("h1").text
    try:

        if symptom_link:
            symptom_soup = BeautifulSoup(requests.get(url+"symptoms/").text,"html.parser")
            section = None
            try:
                section = symptom_soup.find(id="symptoms").parent
            except:
                pass

            if not section:
                section = symptom_soup.find("p", string=re.compile("symptoms")).parent
            if not section:
                section = symptom_soup.find("p", string=re.compile("Symptoms")).parent
            if not section:
                all = symptom_soup.find_all(["p", "h2", "h1", "h3"])
                for link in all:
                    if "Symptoms" in link.text or "symptoms" in link.text:
                        section = link
            if section:
                list_items = section.find_all("li")
                for item in list_items:
                    final_symptoms.append(item.get_text(strip=True).strip())
    except:
        pass

    try:
        section = soup.find("h3", string="Physical effects").parent
        section = section.find_all("li")
        for _ in section:
            final_symptoms.append(_.get_text(strip=True).strip())
    except:
        pass

    try:
        symptom_header = soup.find(id="symptoms")
        section = symptom_header.parent
        list_items = section.find_all("li")
        for item in list_items:
            final_symptoms.append(item.get_text(strip=True).strip())
    except:
        pass

    if "Overview" in name:
        name = soup.find("span", class_="nhsuk-caption--bottom")
        if name:
            name = name.text.replace("-","")
            name = name.strip()
    try:

        if name:
            symptom_header = soup.find(["h2", "h3"], string=re.compile('Symptom'))

        if symptom_header:
            section = symptom_header.parent
            list_items = section.find_all("li")
            for item in list_items:
                final_symptoms.append(item.get_text(strip=True).strip())

    except:
        pass


    if not symptom_header:
        try:
            if not symptom_header:
                symptoms = soup.find(string="Symptoms")
                if symptoms:
                    x = 1

                    table = symptoms.find_parent("table").find_all("td")
                    for symptom in table:
                        if x%2 == 0:
                            for symptom_ in symptom.get_text().split(", "):
                                if symptom_ != "pain" and symptom_ not in final_symptoms:
                                    final_symptoms.append(symptom_.strip())

                        x+=1
        except:
            pass
    removed_stopwords_symptoms = []
    for symptom in final_symptoms:
        symptom = symptom.replace(u"\xa0", u" ")
        symptom = symptom.strip()
        symptoms_for_dictionary.append(symptom)
        filtered_symptom = []
        doc = spacy(symptom)
        tokenizer = spacy.tokenizer
        for token in tokenizer(symptom):
            if token.text.lower() not in all_stopwords:
                filtered_symptom.append(token.text)
        removed_stopwords_symptoms.append(" ".join(filtered_symptom).replace("that","").replace(" ,","").replace(" away","").strip())

    if symptoms_for_dictionary:
        dictionary = {"name": name, "symptoms_complete" : symptoms_for_dictionary, "symptoms_no_stopwords":removed_stopwords_symptoms}
        final_results.append(dictionary)
        print(dictionary)

with open ("diseases.json", "w") as file:
    json.dump(final_results, file)




