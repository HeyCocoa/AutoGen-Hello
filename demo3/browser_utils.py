# -*- coding: utf-8 -*-
"""
NMPA医疗器械数据采集 - 浏览器工具模块
"""

import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_browser(version_main=143):
    """创建浏览器实例"""
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    driver = uc.Chrome(options=options, version_main=version_main)
    return driver


def random_delay(min_sec=1, max_sec=3):
    """随机延迟"""
    time.sleep(random.uniform(min_sec, max_sec))


def close_intro_overlay(driver):
    """关闭引导层"""
    try:
        driver.execute_script("""
            var overlay = document.querySelector('.introjs-overlay');
            if(overlay) overlay.remove();
            var tooltip = document.querySelector('.introjs-tooltipReferenceLayer');
            if(tooltip) tooltip.remove();
            var helperLayer = document.querySelector('.introjs-helperLayer');
            if(helperLayer) helperLayer.remove();
        """)
    except:
        pass
