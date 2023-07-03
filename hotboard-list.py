from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import date

# 创建 Chrome WebDriver 实例
driver = webdriver.Chrome()

# 打开目标网页
driver.get("https://www.ptt.cc/bbs/hotboards.html")

# 等待页面加载完毕
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".board")))

# 获取看板列表
board_elements = driver.find_elements(By.CSS_SELECTOR, ".board")
board_list = []

# 提取看板信息
for element in board_elements:
    board_name = element.find_element(By.CSS_SELECTOR, ".board-name").text
    # 使用 XPath 定位 .board-popularity 元素
    board_popularity = element.find_element(By.XPATH, "./div[2]").text
    board_list.append((board_name, board_popularity))

# 生成保存结果的 CSV 文件名
today = date.today()
csv_file_name = f"hotboards_{today}.csv"

# 将看板信息写入 CSV 文件
with open(csv_file_name, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Board Name", "Popularity"])
    writer.writerows(board_list)

# 关闭浏览器
driver.quit()

print(f"看板清单已保存为 {csv_file_name}")
