# database.py
import mysql.connector
import pandas as pd
from config import DB_PASSWORD

password = DB_PASSWORD
class DB:
    def __init__(self):
        # connect to the database
        try:
            self.conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=password,
                database="flights"
            )
            self.mycursor = self.conn.cursor()
            print('connection established')
        except mysql.connector.Error as err:
            print("Connection failed")
            print(err)

    def fetch_city_names(self):
        if not self.conn.is_connected():
            return []

        query = """
            SELECT DISTINCT(destination_city) AS City FROM ticket_prices
            UNION
            SELECT DISTINCT(source_city) AS City FROM ticket_prices
            ORDER BY City
        """
        self.mycursor.execute(query)
        data = self.mycursor.fetchall()
        return [item[0] for item in data]

    def fetch_filtered_flights(self, source='All', destination='All', travel_class='All'):
        if not self.conn.is_connected():
            return pd.DataFrame()

        query = "SELECT airline, flight, source_city, departure_time, stops, arrival_time, destination_city, class, duration, days_left, price FROM ticket_prices WHERE 1=1"
        params = []

        if source != 'All':
            query += " AND source_city = %s"
            params.append(source)
        if destination != 'All':
            query += " AND destination_city = %s"
            params.append(destination)
        if travel_class != 'All':
            query += " AND class = %s"
            params.append(travel_class)

        self.mycursor.execute(query, tuple(params))
        data = self.mycursor.fetchall()

        cols = ['airline', 'flight', 'source_city', 'departure_time', 'stops', 'arrival_time', 'destination_city',
                'class', 'duration', 'days_left', 'price']
        return pd.DataFrame(data, columns=cols)

    def fetch_airline_frequency(self):
        if not self.conn.is_connected():
            return pd.DataFrame()

        query = "SELECT airline, COUNT(*) as Count FROM ticket_prices GROUP BY airline ORDER BY Count DESC"
        self.mycursor.execute(query)
        data = self.mycursor.fetchall()
        return pd.DataFrame(data, columns=['airline', 'Count'])

    def fetch_price_vs_days_left(self):
        if not self.conn.is_connected():
            return pd.DataFrame()

        query = "SELECT days_left, AVG(price) as avg_price FROM ticket_prices GROUP BY days_left ORDER BY days_left DESC"
        self.mycursor.execute(query)
        data = self.mycursor.fetchall()
        return pd.DataFrame(data, columns=['days_left', 'avg_price'])

    def fetch_stops_pricing(self):
        if not self.conn.is_connected():
            return pd.DataFrame()

        query = "SELECT stops, AVG(price) as avg_price FROM ticket_prices GROUP BY stops"
        self.mycursor.execute(query)
        data = self.mycursor.fetchall()
        return pd.DataFrame(data, columns=['stops', 'avg_price'])