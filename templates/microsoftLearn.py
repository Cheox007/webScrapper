import requests
import logics
from urllib.parse import urljoin

def run(soup, url):
    print("--- Microsoft Learn: Sidebar Extraction & Saving ---")
    
    meta_toc = soup.find('meta', attrs={'name': 'toc_rel'})
    
    if meta_toc:
        toc_url = urljoin(url, meta_toc.get('content'))
        try:
            response = requests.get(toc_url)
            if response.status_code == 200:
                data = response.json()
                
                #Target reference section
                reference_section = logics.findInToc(data.get('items', []), "Reference")
                
                if reference_section:
                    print(f"\n[✔] Processing tree for: {reference_section['toc_title']}")
                    
                    # Remove API sections
                    ignore = ["(Api versions)"]
                    clean_children = logics.filterTocData(reference_section.get('children', []), ignore_list=ignore)
                    
               
                    logics.printTocTree(clean_children)
                    
                    # Save Json
                    save_data = {
                        "source_url": url,
                        "section_title": reference_section['toc_title'],
                        "items": clean_children
                    }
                    logics.saveToJson(save_data, "json", "microsoft_sidebar.json")
                else:
                    print("Could not find 'Reference' section.")
            else:
                print("Failed to download sidebar data.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Could not find sidebar metadata.")
