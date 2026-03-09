import os
import requests
import settings
import json
from urllib.parse import urljoin, urlparse
from utilities import showError
from utilities import getFolderName

# Global Variables

headers = settings.headers


# Functions

# Finders 

def getFinding(find):
    if find:
        print(f"Result of getFinding: {find.get_text(strip=True)}")
    else:
        print("Not found")

def getImages(soup):
    images = soup.find_all('img')
    print(f"\n  Found {len(images)} Images")
    for img in images:
        src = img.get('src')
        alt = img.get('alt', 'No description')
        print(f"Source: {src}| Alt: {alt}")

# Downloaders

def donwloadAllImages(soup, baseUrl, allowSvg=False):
    folderName = getFolderName(baseUrl)
    target_dir = os.path.join("data/harvestedPictures", folderName)
    os.makedirs(target_dir, exist_ok=True)

    images = soup.find_all('img')   

    for i, img in enumerate(images):
        raw_url = (
            img.get('data-lazy-src') or 
            img.get('data-src') or 
            img.get('data-original') or 
            img.get('src')
        )

        if not raw_url or "data:image" in raw_url:
            continue

        clean_path = raw_url.split('?')[0].lower()

        if clean_path.endswith('.svg') and not allowSvg:
            continue

        full_url = urljoin(baseUrl, raw_url)

        try:
            path = urlparse(full_url).path
            ext = os.path.splitext(path)[1] or ".jpg" 
            
            img_response = requests.get(full_url, headers=headers, timeout=10)

            if img_response.status_code == 200:
                fileName = f"image_{i}{ext}"
                filePath = os.path.join(target_dir, fileName)

                with open(filePath, 'wb') as f:
                    f.write(img_response.content)

                print(f"Successfully saved: {fileName}")
            else:
                showError(img_response.status_code) 

        except Exception as e: 
            print(f"Could not download {full_url}: {e}")

# TOC Helpers

def findInToc(items, target_text):
    """Recursively searches for an item in the TOC JSON."""
    for item in items:
        if item.get('toc_title') == target_text:
            return item
        if 'children' in item:
            result = findInToc(item['children'], target_text)
            if result:
                return result
    return None

def printTocTree(items, level=0, ignore_list=None):
    """Recursively prints the TOC tree, skipping ignored titles."""
    if ignore_list is None:
        ignore_list = []
        
    for item in items:
        title = item.get('toc_title', 'No Title')
        
        if title in ignore_list:
            continue
            
        indent = "  " * level
        print(f"{indent}- {title}")
        
        if 'children' in item:
            printTocTree(item['children'], level + 1, ignore_list)

def saveToJson(data, folder, fileName):
    """Saves a dictionary/list to a JSON file in the specified data subfolder."""
    target_dir = os.path.join("data", folder)
    os.makedirs(target_dir, exist_ok=True)
    filePath = os.path.join(target_dir, fileName)
    
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved JSON to: {filePath}")

def filterTocData(items, ignore_list=None):
    """Returns a new list of items excluding those in the ignore_list."""
    if ignore_list is None:
        ignore_list = []
    
    clean_items = []
    for item in items:
        if item.get('toc_title') in ignore_list:
            continue
            
        new_item = item.copy()
        if 'children' in new_item:
            new_item['children'] = filterTocData(new_item['children'], ignore_list)
            
        clean_items.append(new_item)
    return clean_items


#####################################################################

