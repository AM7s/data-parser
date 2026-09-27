import requests
from bs4 import BeautifulSoup
import sqlite3
from typing import List, Dict, Optional


# 2. Создание класса
class BlogArticle:
    def __init__(self, title: str, text: str):
        self.title = title
        self.text = text
    
    def __repr__(self) -> str:
        return f"Title: {self.title}, Text: {self.text}"
    
    def __str__(self) -> str:
        return f"Title: {self.title}, Text: {self.text}"
    
    def to_dict(self) -> Dict[str, str]:
        """Конвертирует объект в словарь"""
        return {"title": self.title, "text": self.text}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'BlogArticle':
        """Создает объект из словаря"""
        return cls(title=data['title'], text=data['text'])


def parse_blog_articles(url: str = "https://msk.top-academy.ru/blog") -> List[BlogArticle]:
    """
    Парсит статьи с сайта Top Academy
    
    Args:
        url: URL страницы 
        
    Returns:
        Список объектов BlogArticle
    """
    try:
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Парсинг HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Поиск блоков со статьями
        article_blocks = soup.find_all('div', class_='styles_cardBody__qP0jN')
        
        articles = []
        
        for block in article_blocks:
            # Поиск всех параграфов в блоке
            paragraphs = block.find_all("p")
            
            # Проверяем, что есть как минимум 2 параграфа (заголовок и текст)
            if len(paragraphs) >= 2:
                title = paragraphs[0].text.strip()
                text = paragraphs[1].text.strip()
                
                # Создаем объект статьи
                article = BlogArticle(title=title, text=text)
                articles.append(article)
        
        print(f"Найдено статей: {len(articles)}")
        return articles
        
    except requests.RequestException as e:
        print(f"Ошибка при парсинге: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []


def init_database(db_path: str = "top_academy_blog.db"):
    """
    Инициализирует базу данных и создает таблицу
    
    Args:
        db_path: Путь к файлу базы данных
        
    Returns:
        Объект соединения с БД
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создание таблицы, если она не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL
        )
    """)
    
    conn.commit()
    return conn


def save_articles_to_db(conn: sqlite3.Connection, articles: List[BlogArticle]) -> int:
    """
    Сохраняет статьи в базу данных, избегая дубликатов
    
    Args:
        conn: Соединение с БД
        articles: Список статей для сохранения
        
    Returns:
        Количество сохраненных статей
    """
    cursor = conn.cursor()
    saved_count = 0
    
    for article in articles:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO articles (title, text)
                VALUES (?, ?)
            """, (article.title, article.text))
            
            if cursor.rowcount > 0:
                saved_count += 1
                
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении статьи '{article.title}': {e}")
    
    conn.commit()
    return saved_count


def get_first_n_articles(conn: sqlite3.Connection, n: int = 5) -> List[BlogArticle]:
    """
    Получает первые n статей из базы данных
    
    Args:
        conn: Соединение с БД
        n: Количество статей для получения
        
    Returns:
        Список статей
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, text FROM articles
        ORDER BY id
        LIMIT ?
    """, (n,))
    
    rows = cursor.fetchall()
    return [BlogArticle(title=row[0], text=row[1]) for row in rows]


def main():
    """Основная функция программы"""
    print("=" * 50)
    print("Парсер блога Top Academy")
    print("=" * 50)
    
    # 1. Парсинг статей
    print("\n1. Сбор данных с блога...")
    articles = parse_blog_articles()
    
    if not articles:
        print("Не удалось получить статьи. Программа завершена.")
        return
    
    # 2. Демонстрация работы методов класса
    print("\n2. Пример работы методов BlogArticle:")
    if articles:
        print("  to_dict():", articles[0].to_dict())
        # Создание из словаря
        article_dict = articles[0].to_dict()
        restored_article = BlogArticle.from_dict(article_dict)
        print("  from_dict():", restored_article)
    
    # 3. Работа с базой данных
    print("\n3. Сохранение в базу данных...")
    conn = init_database()
    
    saved_count = save_articles_to_db(conn, articles)
    print(f"  Сохранено новых статей: {saved_count} (всего в БД: {len(articles)})")
    
    # 4. Проверка сохраненных данных
    print("\n4. Первые 5 записей из базы данных:")
    first_articles = get_first_n_articles(conn, min(5, saved_count))
    
    for i, article in enumerate(first_articles, 1):
        print(f"\n  Запись {i}:")
        print(f"    Заголовок: {article.title[:50]}..." if len(article.title) > 50 else f"    Заголовок: {article.title}")
        print(f"    Текст: {article.text[:100]}..." if len(article.text) > 100 else f"    Текст: {article.text}")
    
    # Закрытие соединения с БД
    conn.close()
    print("\n" + "=" * 50)
    print("Программа завершена успешно!")


if __name__ == "__main__":
    main()