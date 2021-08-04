import pandas as pd 
import numpy as np
import math
#from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

PATH = '<Path to chromedriver here!'
#driver = webdriver.Chrome(PATH)
driver = webdriver.Chrome(ChromeDriverManager().install())

Time_delay = 5

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def best_opt(opt_list, name, city, state):
    #print("FIND BEST OP FOR REAL!\n")
    #opt_list[] tuple is (Name_0, Industry_1, City_2, State_3, Country_4)
    industry = "" 
    best_name = ""
    best_city = ""
    sim_val = 0
    #print("check for city:", city, "; state:", state)

    #Note: remember to parse name before comparing

    for dic in opt_list:
        #dont check for state cuz diff between eg: "California" vs "CA"
        curr_sim = similar(dic[0], name) + similar(dic[2], city)
        #curr_sim = similar(dic[2], city)
        if(curr_sim > sim_val):
            industry = dic[1]
            best_name = dic[0]
            best_city = dic[2]
            sim_val = curr_sim

    print("search_name vs best_name: ", name," VS ",best_name , " nameval:",  similar(best_name, name))
    print("search_city vs best_city: ", city, " VS ", best_city, " CityVal: ", similar(best_city, city) )
    print("total_val: ", sim_val)

    if (similar(best_name, name) < 0.4):
        print("WARNING: NAME VALUE LOW!!!!")
        #return ""

    if (similar(best_city, city) < 0.50) and (city is not np.nan) and (city != "") and (city != "nan"):
        #^ != "nan" is a REALLY jank way of getting the job done but hey it works for now
        #np.isfinite(a) to avoid nan?
        #(not pd.na(city)) ???
        print("CITY VALUE TOO LOW!!!")
        return""
    return industry

def dnb_scrape(name, city, state):
    #base = "https://www.dnb.com/business-directory/top-results.html?term="
    base = "https://www.dnb.com/business-directory/company-search.html?term="

    industry = ""
    options = []

    #parse the name into mod_name

    #mod_name = name
    #mod_name = name.replace("&", " and ")
    # print("wtf:", name, "lower!?:", name.lower())
    mod_name = name

    #driver url search method?
    # url = base+mod_name
    # driver.get(url)

    driver.get("https://www.dnb.com/")
    # time.sleep(2)

    #NOTE: do NOT minimize chromium window in anyway, because that will change the html display to not use "search button" try to resolve this wiht a try stmt later
    #have to click on dnb.com search button to make search bar interactable
    # init_input = driver.find_element_by_id("search_button")

    init_input = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "search_button"))
        )
    init_input.click()
    #error: have to make it interactable first
    #select search bar to type shit in
    input_elems = driver.find_elements_by_css_selector('input[id=search_query]')
    for inputElem in input_elems:
        #clear field just in case
        # inputElem.send_Keys(Keys.CONTROL + "a")
        # inputElem.send_Keys(Keys.DELETE)
        inputElem.clear()
        # time.sleep(5)
        inputElem.send_keys(mod_name)
        # time.sleep(5)
        inputElem.send_keys(Keys.ENTER)

    time.sleep(Time_delay)#give time for shit to load
    try:

        #am lazy, use this to try and trigger search for company_results and shit
        # check_li = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.TAG_NAME, "li"))
        # )
        # print("li DETECTED !!!!! :D")

        company_res = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "company_results"))
        )
        row_res = company_res.find_elements_by_tag_name("li")
        #if we have at least 1 returned result
        if (len(row_res)>0):
            for dic in row_res:
                #prim_name is actual name of thing
                try:
                    prim_name = dic.find_element_by_class_name("primary_name").text
                except:
                    prim_name = ""
                #Indus_ov = dic.find_element_by_class_name("col-md-2")
                try:
                    indus_Name = dic.find_element_by_class_name("industry").text
                except:
                    indus_Name = ""
                try:
                    city_Name = dic.find_element_by_class_name("city").text
                except:
                    city_Name = ""
                try:
                    State_Name = dic.find_element_by_class_name("region").text
                except:
                    State_Name = ""
                try:
                    Country_Name = dic.find_element_by_class_name("country").text
                except:
                    Country_Name = ""

                #add to options[] tuple is (Name, Industry, City, State, Country)
                options.append(
                    (prim_name, indus_Name, city_Name, State_Name, Country_Name)
                )
            #for dic in options:
                #print("options: ", dic)
            
            if len(options)>0:
                #print("find best op !?!? ", city, state, "\n")
                industry = best_opt(options, mod_name, city, state)
        else:
            print("NO RESULTS FOUND ON DNB!")
            

    # finally:
    #     driver.quit()
    # driver.quit()
    except:
        return np.nan
    return industry


pd.set_option('display.max_row', 10000)
pd.set_option('display.max_columns', 50)

#print(gev2.head())
#only keep required stuff


gbv1 = pd.read_csv('<Input csv list of companies>')
gevOnly = gbv1[['Account Name','Billing City', 'Billing state','Industry']]
gevOnly = gevOnly.drop_duplicates()

dnb_output = pd.DataFrame(columns=['Account Name','Billing City', 'Billing City','Industry'])
dnb_index = 0

gevOnly.to_csv (r'input own path here', index = False, header=True)



for index, row in gevOnly.iterrows():
    if pd.isna(row['Industry']):
        if not pd.isna(row['Account Name']):
            Indus = dnb_scrape(str(row['Account Name']), str(row['Billing City']), str(row['Billing state']))
            # print(index, row['Company'])
            Indus = str(Indus).replace("INDUSTRY:", "")
            print("Company:", str(row['Account Name']), "; Industry:", Indus)
            print("")
            # print("\n")
            dnb_output.loc[dnb_index] = [str(row['Account Name']), str(row['Billing City']), str(row['Billing state']), Indus]
            dnb_index = dnb_index + 1

            dnb_output.to_csv (r'input own path here', index = False, header=True)
        

driver.close()

dnb_output.to_csv (r'input own path here', index = False, header=True)
