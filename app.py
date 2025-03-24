from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import streamlit as st

# הגדרת Streamlit
st.title("🔍 בוט לשליפת נתוני צ'אנס")

# פונקציה לפתיחת דפדפן וכניסה לאתר
@st.cache_data
def fetch_chance_data():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ריצה ללא ממשק גרפי
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.pais.co.il/chance/archive.aspx")
    time.sleep(3)  # המתנה לטעינת העמוד
    
    # שליפת נתוני ההגרלות
    results = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for row in rows[:50]:  # לוקח את 50 ההגרלות האחרונות
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:
            date = cols[0].text.strip()
            draw_number = cols[1].text.strip()
            cards = [cols[i].text.strip() for i in range(2, 6)]
            results.append([date, draw_number] + cards)
    
    driver.quit()
    
    # הפיכת הנתונים לטבלה
    df = pd.DataFrame(results, columns=["תאריך", "מספר הגרלה", "לב שחור", "לב אדום", "יהלום", "תלתן"])
    return df

if st.button("🔍 שלוף נתוני צ'אנס"):  
    df = fetch_chance_data()
    st.write("### טבלת 50 ההגרלות האחרונות:")
    st.dataframe(df)
