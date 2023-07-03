from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_articles(start_date=None, end_date=None):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    base_url = 'https://www.ptt.cc/bbs/Gossiping/index.html'  # 将此处替换为您要访问的网站URL
    driver.get(base_url)

    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'r-ent')))

    article_elements = driver.find_elements(By.CLASS_NAME, 'r-ent')

    for article_element in article_elements:
        
        title_element = article_element.find_element(By.CLASS_NAME, 'title')
        title_link = title_element.find_element(By.TAG_NAME, 'a')
        title = title_link.text

        meta_element = article_element.find_element(By.CLASS_NAME, 'meta')
        author = meta_element.find_element(By.CLASS_NAME, 'author').text
        date = meta_element.find_element(By.CLASS_NAME, 'date').text

        if start_date and end_date:
            if start_date <= date <= end_date:
                article_link = title_link.get_attribute('href')
                driver.get(article_link)

                content_element = driver.find_element(By.CSS_SELECTOR, '.article-content')
                content = content_element.text

                print('标题:', title)
                print('作者:', author)
                print('发文时间:', date)
                print('内容:', content)
                print('-----------------------------------')
        else:
            article_link = title_link.get_attribute('href')
            driver.get(article_link)

            content_element = driver.find_element(By.CSS_SELECTOR, '.article-content')
            content = content_element.text

            print('标题:', title)
            print('作者:', author)
            print('发文时间:', date)
            print('内容:', content)
            print('-----------------------------------')

    driver.quit()

# 示例用法：
# 爬取当日文章
scrape_articles()

# 爬取指定时间范围内的文章
scrape_articles(start_date='2023-07-01', end_date='2023-07-03')
