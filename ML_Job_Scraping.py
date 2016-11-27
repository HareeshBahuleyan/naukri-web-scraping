import bs4
import urllib2
import pandas as pd
import math
import time
from pandas import DataFrame
from collections import OrderedDict
import cPickle

# Base URL + Location
base_url = 'http://www.naukri.com/machine-learning-jobs-'
source = urllib2.urlopen(base_url).read()

soup = bs4.BeautifulSoup(source, "lxml")
num_jobs = int(soup.find("div", { "class" : "count" }).h1.contents[1].getText().split(' ')[-1])
num_pages = int(math.ceil(num_jobs/50.0))

# Together into one function
labels = ['Salary', 'Industry', 'Functional Area', 'Role Category', 'Design Role']
edu_labels = ['UG', 'PG', 'Doctorate']
naukri_df = pd.DataFrame()
           
for page in range(1,num_pages+1):
    page_url = base_url+str(page)
    source = urllib2.urlopen(page_url).read()
    soup = bs4.BeautifulSoup(source,"lxml")
    all_links = [link.get('href') for link in soup.findAll('a') if 'job-listings' in  str(link.get('href'))]
    for url in all_links:
        jd_source = urllib2.urlopen(url).read()
        jd_soup = bs4.BeautifulSoup(jd_source,"lxml")
        try:
            jd_text = jd_soup.find("ul",{"itemprop":"description"}).getText().strip()
            location = jd_soup.find("div",{"class":"loc"}).getText().strip()
            experience = jd_soup.find("span",{"itemprop":"experienceRequirements"}).getText().strip()
            
            role_info = [content.getText().split(':')[-1].strip() for content in jd_soup.find("div",{"class":"jDisc mt20"}).contents if len(str(content).replace(' ',''))!=0]
            role_info_dict = {label: role_info for label, role_info in zip(labels, role_info)}
            
            key_skills = '|'.join(jd_soup.find("div",{"class":"ksTags"}).getText().split('  '))[1:]

            edu_info = [content.getText().split(':') for content in jd_soup.find("div",{"itemprop":"educationRequirements"}).contents if len(str(content).replace(' ',''))!=0]
            edu_info_dict = {label.strip(): edu_info.strip() for label, edu_info in edu_info}
            for l in edu_labels:
                if l not in edu_info_dict.keys():
                    edu_info_dict[l] = ''

            company_name = jd_soup.find("div",{"itemprop":"hiringOrganization"}).contents[1].p.getText().strip()
        
        except AttributeError:
            continue
        df_dict = OrderedDict({'Location':location, 'Link':url,'Job Description':jd_text,'Experience':experience,'Skills':key_skills,'Company Name':company_name})
        df_dict.update(role_info_dict)
        df_dict.update(edu_info_dict)
        naukri_df = naukri_df.append(df_dict,ignore_index=True)
        time.sleep(1)
    print page
    
column_names = ['Location', 'Link', 'Job Description', 'Experience','Salary', 'Industry', 'Functional Area', 'Role Category', 
                'Design Role', 'Skills', 'Company Name',
                'UG','PG','Doctorate']

naukri_df = naukri_df.reindex(columns=column_names)        
with open('naukri_dataframe.pkl', 'wb') as f:
    cPickle.dump(naukri_df, f)