from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests 
from bs4 import BeautifulSoup
from utiles import DataBase
import sqlalchemy as db
import pandas as pd
from PIL import Image
import time 
import sys

#get elements with attribute
def get_info1(soup,url,tag,className,attribus):
  try:
    return soup.find(tag,class_=className)[attribus]
  except:
    return ''

#get text elements
def get_info2(soup,url,tag,className):
  try:
    return soup.find(tag,class_=className).text.strip()
  except:
    return ''

#get description list and join it to list just one
def get_descriptions(soup,tag,className):
  try:
    description=soup.find_all(tag,class_=className)
    return (','.join([describe.text.strip() for describe in description]))
  except:
    return""


#get result of serach job gethring 
def collect_data_job(url):
  response=requests.get(url)
  soup=BeautifulSoup(response.text, "lxml")
  time.sleep(1)
  job_details={
    "title":get_info2(soup,url,'h1','top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title'),
    "entreprise":get_info2(soup,url,'a','topcard__org-name-link topcard__flavor--black-link'),
    "localisation":get_info2(soup,url,'span','topcard__flavor topcard__flavor--bullet'),
    "date":get_info2(soup,url,'span','posted-time-ago__text topcard__flavor--metadata'),
    "url to apply":get_info1(soup,url,'a','apply-button apply-button--link top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary','href'),
    "details":get_info2(soup,url,'div','show-more-less-html__markup'),
    "job description":get_descriptions(soup,'span','description__job-criteria-text description__job-criteria-text--criteria'),
    
  }
  return job_details
  
  

#def to collect data
def collect_data(search_term):
  driver.get('https://www.linkedin.com/jobs/')
  driver.find_element(By.CLASS_NAME,'artdeco-global-alert-action.artdeco-button.artdeco-button--inverse.artdeco-button--2.artdeco-button--primary').click()
  #select input tag element and send search term
  input_ = driver.find_elements(By.TAG_NAME, 'input')
  input_[3].send_keys(search_term+Keys.ENTER)
  #getting element of all job list
  liste=driver.find_element(By.CLASS_NAME,'jobs-search__results-list')
  #get the number of charging job list to compare with last list
  list_job_number=len(liste.find_elements(By.TAG_NAME,'li'))
  ancien_liste=0
  #while we can scroll that we can collect other results
  while list_job_number > ancien_liste :
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #if 
    ancien_liste=list_job_number
    time.sleep(2)
    list_job_number=len(liste.find_elements(By.TAG_NAME,'li'))
  
  jobs=liste.find_elements(By.TAG_NAME,'li');
  urls_job_list=[job.find_element_by_tag_name('a').get_attribute('href') for job in jobs]
  #create dataFrame && save in csv file
  df=[collect_data_job(url) for url in urls_job_list]
  pd.DataFrame(df).to_csv('Job_Board_'+search_term)
  for url in urls_job_list:
    data=collect_data_job(url)
    # Ajout d'une ligne dans la base de données 'database.db'
    base.add_row('Job_Board_'+search_term,
              title=data['title'],
              entreprise=data['entreprise'],
              localisation=data['localisation'],  
              date=data['date'],  
              url_apply=data['url to apply'], 
              details=data['details'],
              descriptions=data['job description']
            )
  

driver = webdriver.Chrome('../chromedriver')
search_term=' '.join(sys.argv[1:])
# Instaciation de la base de données 'database.db'
base = DataBase('database')
# Création d'une table nommée "Table_Test" dans la base de données 'database.db'
base.create_table('Job_Board_'+search_term, 
                 title=db.String,
                 entreprise=db.String,
                 localisation=db.String,                
                 date=db.String,                
                 url_apply=db.String, 
                 details=db.String,               
                 descriptions=db.String,                
                 )
collect_data(search_term)
