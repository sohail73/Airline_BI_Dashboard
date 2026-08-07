# database.py
import sqlite3
import pandas as pd


class DB:
    def __init__(self):
        # Database file ka naam (ye file convert_db script se banegi)
        self.db_path = "flights.db"
        print('SQLite connection initialized')

    def fetch_city_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT(destination_city) AS City FROM ticket_prices
            UNION
            SELECT DISTINCT(source_city) AS City FROM ticket_prices
            ORDER BY City
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        return [item[0] for item in data]

    def fetch_filtered_flights(self, source='All', destination='All', travel_class='All'):
        conn = sqlite3.connect(self.db_path)

        query = "SELECT airline, flight, source_city, departure_time, stops, arrival_time, destination_city, class, duration, days_left, price FROM ticket_prices WHERE 1=1"
        params = []

        if source != 'All':
            query += " AND source_city = ?"
            params.append(source)
        if destination != 'All':
            query += " AND destination_city = ?"
            params.append(destination)
        if travel_class != 'All':
            query += " AND class = ?"
            params.append(travel_class)

        # Pandas directly SQLite se data DataFrame me convert kar deta hai
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def fetch_airline_frequency(self):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT airline, COUNT(*) as Count FROM ticket_prices GROUP BY airline ORDER BY Count DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def fetch_price_vs_days_left(self):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT days_left, AVG(price) as avg_price FROM ticket_prices GROUP BY days_left ORDER BY days_left DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def fetch_stops_pricing(self):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT stops, AVG(price) as avg_price FROM ticket_prices GROUP BY stops"
        df = pd.read_sql_query(query, conn)
        conn.close()

        return df