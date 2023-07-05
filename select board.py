import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_articles(board, start_date=None, end_date=None):
    # 設定Chrome Driver的執行檔路徑
    options = Options()
    options.chrome_executable_path = "C:/Users/05731/OneDrive/桌面/crawler/chromedriver.exe"

    # 建立Driver物件實體，用程式操作瀏覽器運作
    driver = webdriver.Chrome(options=options)

    # 設定起始頁面URL
    base_url = f"https://www.ptt.cc/bbs/{board}/index.html"
    driver.get(base_url)

    # 等待同意條款視窗出現
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[@name='yes']")))

    # 點擊同意條款連結
    agree_button = driver.find_element(By.XPATH, "//button[@name='yes']")
    agree_button.click()

    # 等待文章元素加載
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "title")))

    # 取得當前日期
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # 設定CSV檔案名稱
    filename = f"{board}_articles_{current_date}.csv"

    # 建立CSV檔案並寫入標題行
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["標題", "發文時間", "作者", "內容", "留言"])  # 加入留言欄位

        # 爬取文章
        page_url = base_url
        while True:
            # 取得文章元素列表
            article_elements = driver.find_elements(By.CLASS_NAME, "title")

            for article_element in article_elements:
                # 取得文章標題
                title = article_element.text.strip()

                # 點擊文章連結進入文章頁面
                title_link = article_element.find_element(By.CSS_SELECTOR, "a")
                link = title_link.get_attribute("href")
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])

                # 等待文章頁面加載
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main-content")))

                print("標題:", title)
                print("連結:", link)

                # 取得文章發文時間、作者和內容
                post_time_element = driver.find_element(By.CSS_SELECTOR, "div.article-metaline:nth-child(4) span.article-meta-value")
                post_time = post_time_element.text.strip()
                author_element = driver.find_element(By.CSS_SELECTOR, "div.article-metaline:nth-child(1) span.article-meta-value")
                author = author_element.text.strip()

                content_element = driver.find_element(By.ID, "main-content")
                content = content_element.text.strip()

                # 取得留言內容
                comments_elements = driver.find_elements(By.CSS_SELECTOR, "div.push-content")
                comments = [comment.text.strip() for comment in comments_elements]

                # 寫入CSV檔案
                writer.writerow([title, post_time, author, content, "\n".join(comments)])

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # 翻頁
            previous_page = driver.find_element(By.LINK_TEXT, "‹ 上頁")
            page_url = previous_page.get_attribute("href")
            driver.get(page_url)

            current_date = page_url.split("/")[-1].replace("index", "").replace(".html", "")

            if start_date and end_date:
                if start_date > current_date or current_date > end_date:
                    break

            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "‹ 上頁")))

    driver.quit()

# 指定看板名稱，起始日期和結束日期
scrape_articles("Gossiping", start_date="2023-07-04", end_date="2023-07-05")
