A webscraping utility for soil moisture and precipitation value extraction from the Michigan Automated Weather Network (MAWN)  
https://mawn.geo.msu.edu/  
# mawnscrape  

Prerequisites:  
1. Python 3  
    Install at:  
        https://www.python.org/downloads/  
2. Selenium for Python 3  
    to install:  
        FOR OSX AND LINUX:  
            $ pip install -U selenium  
        FOR WINDOWS:  
            > python install selenium  
3. Chrome Webdriver needs to be downloaded in directory of script  
    If a compilation error occurs after running web.py  
        Redownload the WebDriver at:  
            https://chromedriver.storage.googleapis.com/index.html?path=74.0.3729.6/  
4. BeautifulSoup for Python 3  
    to install:  
        FOR OSX AND LINUX:  
            $ pip install beautifulsoup4  
        FOR WINDOWS:  
            > python install beautifulsoup4  
5. LXML for Python 3  
    to install:  
        FOR OSX AND LINUX:  
            $ pip install lxml  
        FOR WINDOWS:  
            > python install lxml  
6. TinyDB for Python 3  
    to install:  
        FOR OSX AND LINUX:  
            $ pip install tinydb  
        FOR WINDOWS:  
            > python install tinydb  


To Run:  
    Run web.py as a python3 file  
        To run:  
            FOR OSX AND LINUX:  
                $ python web.py  
            FOR WINDOWS:  
                > python web.py  
        and let chrome run in the background  

To get csv's, they will be stored in the folder StationCSVs  
