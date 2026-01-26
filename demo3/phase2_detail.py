# -*- coding: utf-8 -*-
"""
第二阶段：根据注册证编号获取详情页数据
输入：phase1_result.xlsx（或你筛选后的文件）
输出：nmpa_data.xlsx（完整详情数据）
"""

import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browser_utils import create_browser, random_delay, close_intro_overlay


def get_detail_by_reg_number(driver, wait, reg_number):
    """通过注册证编号搜索并获取详情"""
    detail_data = {}

    # 访问首页
    driver.get('https://www.nmpa.gov.cn/datasearch/home-index.html')
    random_delay(4, 6)
    close_intro_overlay(driver)

    # 点击医疗器械分类
    try:
        device_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'yiliaoqixie')]")))
        driver.execute_script("arguments[0].click();", device_tab)
        random_delay(2, 3)
        close_intro_overlay(driver)
    except:
        return detail_data

    # 点击境内医疗器械（注册）
    try:
        domestic_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@title='境内医疗器械（注册）']")))
        driver.execute_script("arguments[0].click();", domestic_link)
        random_delay(2, 3)
    except:
        return detail_data

    # 输入注册证编号搜索
    try:
        search_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".search-input input.el-input__inner")))
        driver.execute_script("""
            var input = arguments[0];
            input.focus();
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
        """, search_input, reg_number)
        random_delay(1, 2)
    except:
        return detail_data

    # 点击搜索
    try:
        search_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".el-input-group__append button")))
        driver.execute_script("arguments[0].click();", search_btn)
        random_delay(4, 6)
    except:
        return detail_data

    # 等待跳转
    try:
        wait.until(EC.url_contains("search-result.html"))
        random_delay(2, 3)
    except:
        return detail_data

    # 等待表格并点击详情
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".el-table__body tbody tr")))
        row = driver.find_element(By.CSS_SELECTOR, ".el-table__body tbody tr")
        detail_btn = row.find_element(By.CSS_SELECTOR, "td:last-child button, td:last-child a")
        driver.execute_script("arguments[0].click();", detail_btn)
        random_delay(3, 5)
    except:
        return detail_data

    # 获取详情页数据
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#dataTable tbody tr")))
        random_delay(1, 2)

        rows = driver.find_elements(By.CSS_SELECTOR, "#dataTable tbody tr")
        for row in rows:
            tds = row.find_elements(By.CSS_SELECTOR, "td")
            if len(tds) >= 2:
                key_elem = tds[0].find_element(By.CSS_SELECTOR, ".cell")
                val_elem = tds[1].find_element(By.CSS_SELECTOR, ".cell")
                key = key_elem.text.strip()
                value = val_elem.text.strip()
                if key and key != "注":
                    detail_data[key] = value
    except Exception as e:
        print(f"      获取详情失败: {e}")

    return detail_data


def main():
    # 读取第一阶段结果（支持多sheet）
    input_file = "phase1_result.xlsx"
    try:
        # 读取所有sheet并合并
        xlsx = pd.ExcelFile(input_file)
        df_list = []
        for sheet_name in xlsx.sheet_names:
            df_sheet = pd.read_excel(xlsx, sheet_name=sheet_name)
            df_list.append(df_sheet)
        df_input = pd.concat(df_list, ignore_index=True)
    except FileNotFoundError:
        print(f"找不到文件 {input_file}")
        print("请先运行 phase1_collect.py 或准备好筛选后的Excel文件")
        return

    reg_numbers = df_input["注册证编号"].tolist()
    # 保留搜索关键词映射
    keyword_map = dict(zip(df_input["注册证编号"], df_input["搜索关键词"]))
    # 保留产品ID映射
    product_id_map = dict(zip(df_input["注册证编号"], df_input.get("产品ID", [None]*len(df_input))))

    print("=" * 60)
    print("第二阶段：获取详情页数据")
    print(f"共 {len(reg_numbers)} 条记录待处理")
    print("=" * 60)

    driver = create_browser(version_main=143)
    wait = WebDriverWait(driver, 30)

    all_data = []

    try:
        for i, reg_no in enumerate(reg_numbers):
            print(f"\n[{i+1}/{len(reg_numbers)}] {reg_no}")

            detail_data = get_detail_by_reg_number(driver, wait, reg_no)

            if detail_data:
                detail_data["搜索关键词"] = keyword_map.get(reg_no, "")
                detail_data["产品ID"] = product_id_map.get(reg_no, "")
                all_data.append(detail_data)
                print(f"   OK: {detail_data.get('产品名称', 'N/A')[:40]}...")
            else:
                print(f"   FAILED")

            # 每10条保存一次
            if (i + 1) % 10 == 0:
                save_data(all_data)
                print(f"   [已保存 {len(all_data)} 条]")

            # 延迟
            if i < len(reg_numbers) - 1:
                random_delay(3, 6)

        # 最终保存
        save_data(all_data)
        print(f"\n{'='*60}")
        print(f"采集完成！共 {len(all_data)} 条数据")
        print(f"已保存到 nmpa_data.xlsx")
        print(f"{'='*60}")

    finally:
        driver.quit()


def save_data(data, filename="nmpa_data.xlsx"):
    """保存数据到Excel"""
    if data:
        df = pd.DataFrame(data)
        priority_cols = ['注册证编号', '产品名称', '注册人名称', '注册人住所', '生产地址',
                        '管理类别', '型号规格', '结构及组成/主要组成成分', '适用范围/预期用途',
                        '产品储存条件及有效期', '批准日期', '有效期至', '搜索关键词', '产品ID']
        existing_cols = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[existing_cols + other_cols]
        df.to_excel(filename, index=False)


if __name__ == "__main__":
    main()
