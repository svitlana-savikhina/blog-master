import sqlite3
import logging

from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException

logging.basicConfig(
    filename="parser.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_news_data():
    driver = None
    try:
        chrome_options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://news.ycombinator.com/")
        button1 = driver.find_element("xpath", '//a[@href="newest"]')
        button1.click()
        element = driver.find_element("xpath", '//span[@class="titleline"]/a').text
        logging.info("Data fetched successfully: %s", element)
        return element
    except NoSuchElementException as e:
        logging.error("Element not found: %s", e)
    except WebDriverException as e:
        logging.error("WebDriver error: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
    finally:
        if driver is not None:
            try:
                driver.close()
            except Exception as e:
                logging.error("Failed to close WebDriver: %s", e)
    return None


def save_to_database(data):
    if data is None:
        logging.warning("No data to save to database.")
        return

    try:
        conn = sqlite3.connect("../news_data.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            INSERT INTO news (title) VALUES (?)
        """,
            (data,),
        )

        conn.commit()
        logging.info("Data saved to database successfully: %s", data)

    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred while saving to database: %s", e)
    finally:
        try:
            conn.close()
        except Exception as e:
            logging.error("Failed to close the database connection: %s", e)


if __name__ == "__main__":
    news_data = get_news_data()
    save_to_database(news_data)
    if news_data:
        print("Data saved to database:", news_data)
    else:
        print("Failed to fetch or save data.")
