from bs4 import BeautifulSoup
import utilities
import logics
import settings
from templates import microsoftLearn

def main():
    ############## BASIC PARAMETERS ######################

    response = utilities.getResponse()
    url = settings.url

    ####################### USAGE #######################
    if response.status_code == 200: 
        soup = BeautifulSoup(response.text, 'html.parser')    
     
        # Using your template
        microsoftLearn.run(soup,url)
        
        # Or use the default logic (currently commented out):
        # logics.donwloadAllImages(soup, settings.url)

    else:
        utilities.showError(response.status_code)

if __name__ == "__main__":
    main()
