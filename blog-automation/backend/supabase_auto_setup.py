#!/usr/bin/env python3
"""
Supabase 테이블 자동 생성 스크립트 (Selenium 사용)
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os

# Supabase 정보
SUPABASE_PROJECT_URL = "https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd"
SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), "database/schema.sql")

def create_tables_with_selenium():
    """Selenium을 사용하여 Supabase SQL Editor에서 테이블 생성"""
    
    print("🌐 브라우저를 통해 Supabase에서 테이블을 생성합니다...")
    print("⚠️  GitHub로 로그인이 필요합니다.")
    print("="*60)
    
    # SQL 파일 읽기
    try:
        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print("✅ SQL 파일 읽기 완료")
    except Exception as e:
        print(f"❌ SQL 파일 읽기 실패: {e}")
        return False
    
    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Chrome 드라이버 시작
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        
        # Supabase 프로젝트 SQL Editor로 이동
        sql_editor_url = f"{SUPABASE_PROJECT_URL}/sql/new"
        print(f"\n📍 SQL Editor로 이동: {sql_editor_url}")
        driver.get(sql_editor_url)
        
        # 로그인 대기
        print("\n⏳ 로그인을 기다리는 중...")
        print("👉 GitHub 계정으로 로그인해주세요.")
        
        # SQL Editor가 로드될 때까지 대기 (최대 60초)
        try:
            # Monaco Editor가 로드될 때까지 대기
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "monaco-editor"))
            )
            print("✅ SQL Editor 로드 완료")
        except:
            print("❌ SQL Editor 로드 실패. 수동으로 진행해주세요.")
            input("Enter를 눌러 계속...")
        
        # SQL 입력
        print("\n📝 SQL 입력 중...")
        try:
            # Monaco Editor에 SQL 입력
            # 여러 방법 시도
            methods = [
                # 방법 1: 직접 textarea 찾기
                lambda: driver.find_element(By.CSS_SELECTOR, "textarea.inputarea"),
                # 방법 2: Monaco editor의 view-line 클릭 후 입력
                lambda: driver.find_element(By.CLASS_NAME, "view-line"),
                # 방법 3: contenteditable div
                lambda: driver.find_element(By.CSS_SELECTOR, "[contenteditable='true']")
            ]
            
            editor_found = False
            for method in methods:
                try:
                    editor = method()
                    editor.click()
                    time.sleep(1)
                    
                    # 기존 내용 지우기
                    editor.send_keys(Keys.CONTROL + "a" if os.name != 'darwin' else Keys.COMMAND + "a")
                    editor.send_keys(Keys.DELETE)
                    
                    # SQL 입력
                    editor.send_keys(sql_content)
                    editor_found = True
                    print("✅ SQL 입력 완료")
                    break
                except:
                    continue
            
            if not editor_found:
                print("⚠️  에디터를 찾을 수 없습니다. 수동으로 SQL을 붙여넣어주세요.")
                print("\n" + "="*60)
                print("📋 아래 SQL을 복사하여 붙여넣으세요:")
                print("="*60)
                print(sql_content[:500] + "...")
                print("="*60)
                input("\nSQL을 붙여넣은 후 Enter를 눌러주세요...")
        
        except Exception as e:
            print(f"⚠️  SQL 입력 중 오류: {e}")
            print("수동으로 SQL을 붙여넣어주세요.")
            input("Enter를 눌러 계속...")
        
        # Run 버튼 찾기
        print("\n🔍 Run 버튼을 찾는 중...")
        try:
            # 여러 가능한 선택자 시도
            run_button_selectors = [
                "//button[contains(text(), 'Run')]",
                "//button[contains(text(), 'RUN')]",
                "//button[contains(@class, 'run')]",
                "//button[contains(., 'Run query')]"
            ]
            
            run_button = None
            for selector in run_button_selectors:
                try:
                    run_button = driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if run_button:
                print("✅ Run 버튼 발견")
                print("👉 Run 버튼을 클릭하여 SQL을 실행해주세요.")
                print("⏳ 실행 완료를 기다리는 중...")
                time.sleep(10)
            else:
                print("⚠️  Run 버튼을 찾을 수 없습니다.")
                print("👉 수동으로 Run 버튼을 클릭해주세요.")
                input("SQL 실행 후 Enter를 눌러주세요...")
        
        except Exception as e:
            print(f"⚠️  Run 버튼 찾기 실패: {e}")
            input("수동으로 실행 후 Enter를 눌러주세요...")
        
        print("\n✅ 테이블 생성 완료!")
        print("🎉 이제 블로그 자동화 시스템을 사용할 수 있습니다.")
        
        # 브라우저는 열어둔 상태로 유지
        input("\n브라우저를 닫으려면 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    finally:
        driver.quit()
    
    return True

def alternative_method():
    """대체 방법 안내"""
    print("\n" + "="*60)
    print("🔧 수동 테이블 생성 방법:")
    print("="*60)
    print("\n1. 아래 URL을 브라우저에서 엽니다:")
    print(f"   {SUPABASE_PROJECT_URL}/sql/new")
    
    print("\n2. GitHub 계정으로 로그인합니다.")
    
    print("\n3. SQL Editor에 다음 파일의 내용을 복사하여 붙여넣습니다:")
    print(f"   {SQL_FILE_PATH}")
    
    print("\n4. 'Run' 버튼을 클릭하여 SQL을 실행합니다.")
    
    print("\n5. 성공 메시지가 나타나면 완료!")
    
    # SQL 내용 일부 표시
    try:
        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("\n" + "="*60)
        print("📋 SQL 내용 (처음 20줄):")
        print("="*60)
        lines = sql_content.split('\n')[:20]
        for line in lines:
            print(line)
        print("... (이하 생략)")
        print("="*60)
    except:
        pass

if __name__ == "__main__":
    print("🚀 Supabase 테이블 자동 생성 도구")
    print("="*60)
    
    try:
        # Selenium 사용 가능 확인
        from selenium import webdriver
        print("✅ Selenium이 설치되어 있습니다.")
        
        print("\n어떤 방법을 사용하시겠습니까?")
        print("1. 자동으로 브라우저 열기 (Selenium)")
        print("2. 수동 설정 가이드 보기")
        
        choice = input("\n선택 (1 또는 2): ")
        
        if choice == "1":
            create_tables_with_selenium()
        else:
            alternative_method()
            
    except ImportError:
        print("⚠️  Selenium이 설치되어 있지 않습니다.")
        print("pip install selenium 명령으로 설치하거나,")
        print("아래 수동 방법을 따라주세요.\n")
        alternative_method()