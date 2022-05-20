# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from sympy import N
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # set up variables
    news_title, news_paragraph = mars_news(browser)

    # run all scraping functions and store results in dictionary
    data = {
        "news_title":news_title,
        "news_paragraph":news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified":dt.datetime.now()
    }
    # stop webdriver and return data
    browser.quit()
    return data 

def mars_news(browser):
    # visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # set up the html parser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    slide_elem = news_soup.select_one('div.list_text')
    
    # begin scraping    
    try:
    
        # assign title and summary text to varaibles
        slide_elem.find('div', class_='content_title')

        # use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        

        # use the parent element to find the paragraph text
        new_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, new_p


# ### JPL Space Images Featured Image

def featured_image(browser):
    # visit url
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return  img_url

# ## Mars Facts 

def mars_facts():
    try: 
        # scrape facts table with pandas
        df = pd.read_html('https://galaxyfacts-mars.com')[0] #[0] pulls only the first table it comes across
    except BaseException:
        return None

    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    # convert df back to html, add bootstrap
    return df.to_html(classes="table table=striped")

if __name__ == "__main__":
    # if running as script, print scraped data
    print(scrape_all())