# -*- coding: utf-8 -*-
"""
第一阶段：收集列表页信息并筛选
输出：phase1_result.xlsx（筛选后的数据，供人工复核）
"""

import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browser_utils import create_browser, random_delay, close_intro_overlay
from keywords import ALL_KEYWORDS, filter_product, get_product_id_by_keyword


def collect_list_data(driver, wait, keyword):
    """收集某个关键词的所有列表页数据"""
    results = []

    print(f"\n{'='*60}")
    print(f"搜索关键词: {keyword}")
    print(f"{'='*60}")

    # 访问首页
    driver.get('https://www.nmpa.gov.cn/datasearch/home-index.html')
    random_delay(5, 7)
    close_intro_overlay(driver)

    # 点击医疗器械分类
    try:
        device_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'yiliaoqixie')]")))
        driver.execute_script("arguments[0].click();", device_tab)
        random_delay(3, 4)
        close_intro_overlay(driver)
    except Exception as e:
        print(f"   选择分类失败: {e}")
        return results

    # 点击境内医疗器械（注册）
    try:
        domestic_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@title='境内医疗器械（注册）']")))
        driver.execute_script("arguments[0].click();", domestic_link)
        random_delay(3, 4)
    except Exception as e:
        print(f"   选择数据库失败: {e}")
        return results

    # 输入搜索关键词
    try:
        search_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".search-input input.el-input__inner")))
        driver.execute_script("""
            var input = arguments[0];
            input.focus();
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
        """, search_input, keyword)
        random_delay(1, 2)
    except Exception as e:
        print(f"   输入关键词失败: {e}")
        return results

    # 点击搜索
    try:
        search_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".el-input-group__append button")))
        driver.execute_script("arguments[0].click();", search_btn)
        random_delay(5, 8)
    except Exception as e:
        print(f"   点击搜索失败: {e}")
        return results

    # 等待跳转
    try:
        wait.until(EC.url_contains("search-result.html"))
    except:
        print(f"   未跳转到结果页")
        return results

    random_delay(3, 5)

    # 等待表格
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".el-table__body tbody tr")))
    except:
        print(f"   没有搜索结果")
        return results

    # 遍历所有页面
    page_num = 0
    while True:
        page_num += 1
        random_delay(1, 2)

        rows = driver.find_elements(By.CSS_SELECTOR, ".el-table__body tbody tr")
        row_count = len(rows)

        if row_count == 0:
            break

        # 收集当前页数据
        page_results = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) >= 4:
                reg_no = cells[1].text.strip()
                company = cells[2].text.strip()
                product_name = cells[3].text.strip()

                if reg_no:
                    page_results.append({
                        "注册证编号": reg_no,
                        "注册人名称": company,
                        "产品名称": product_name,
                        "搜索关键词": keyword,
                        "产品ID": get_product_id_by_keyword(keyword),
                    })

        results.extend(page_results)
        print(f"   第{page_num}页: {len(page_results)}条 (累计{len(results)})")

        # 尝试翻页
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-next:not([disabled])")
            driver.execute_script("arguments[0].click();", next_btn)
            random_delay(2, 4)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".el-table__body tbody tr")))
        except:
            print(f"   已到最后一页")
            break

    print(f"   关键词 '{keyword}' 共收集 {len(results)} 条")
    return results


def main():
    print("=" * 60)
    print("第一阶段：收集列表页信息")
    print("=" * 60)

    driver = create_browser(version_main=143)
    wait = WebDriverWait(driver, 30)

    all_data = []
    seen_reg_numbers = set()  # 用于去重

    try:
        for i, keyword in enumerate(ALL_KEYWORDS):
            print(f"\n进度: {i+1}/{len(ALL_KEYWORDS)}")

            keyword_data = collect_list_data(driver, wait, keyword)

            # 去重并筛选
            for item in keyword_data:
                reg_no = item["注册证编号"]
                if reg_no not in seen_reg_numbers:
                    # 应用筛选条件
                    if filter_product(item["产品名称"], item["搜索关键词"]):
                        seen_reg_numbers.add(reg_no)
                        all_data.append(item)

            # 关键词之间延迟
            if i < len(ALL_KEYWORDS) - 1:
                delay = random.uniform(10, 20)
                print(f"等待 {delay:.1f} 秒...")
                time.sleep(delay)

        print(f"\n{'='*60}")
        print(f"第一阶段完成！")
        print(f"筛选后共 {len(all_data)} 条数据")
        print(f"{'='*60}")

        # 保存结果（按产品ID分sheet）
        if all_data:
            df = pd.DataFrame(all_data)
            df = df[["注册证编号", "产品名称", "注册人名称", "搜索关键词", "产品ID"]]

            with pd.ExcelWriter("phase1_result.xlsx", engine="openpyxl") as writer:
                for product_id in [1, 2, 3, 4]:
                    df_product = df[df["产品ID"] == product_id]
                    if not df_product.empty:
                        df_product.to_excel(writer, sheet_name=f"product{product_id}", index=False)
                        print(f"产品{product_id}: {len(df_product)}条")

            print(f"\n已保存到 phase1_result.xlsx（4个sheet）")
            print(f"请检查数据，确认后运行 phase2_detail.py 获取详情")
        else:
            print("没有符合条件的数据")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
