import mysql.connector

config = {
        'user': 'root',
        'password': '*****',
        'host': '127.0.0.1',
        'database': 'pandeyji_eatery',
        'raise_on_warnings': True
    }

def get_order_status(order_id):
    # Database connection configuration
    

    # Connect to the database
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Query to fetch status based on order_id
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        
        # Fetch the status
        status = cursor.fetchone()

        if status:
            return status[0]  # Return the status value
        else:
            return "Order not found"

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Test the function

#if __name__ == "__main__":
  #  order_id = input("Enter the order ID: ")
    #status = get_order_status(order_id)
    
    #if status:
        #print(f"Status for order {order_id}: {status}")
   # else:
        #print("Failed to retrieve order status.")

def get_max_order_id():
    # MySQL database configuration
    

    # Connect to MySQL database
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Execute SQL query to get max order_id
        query = "SELECT MAX(order_id) FROM `orders`;"
        cursor.execute(query)

        # Fetch the result
        max_order_id = cursor.fetchone()[0]

        # Print the max order_id
        print(f"Max order_id: {max_order_id}")
        next_order_id = max_order_id + 1 if max_order_id is not None else 1

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return next_order_id

def insert_order_item(food_item,quantity, next_order_id):
    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Call the stored procedure
        cursor.callproc('insert_order_item', (food_item, quantity, next_order_id))

        # Commit the transaction
        conn.commit()
        print("Successfully inserted values using stored procedure.")
        return 1

    except mysql.connector.Error as err:
        return -1
        print(f"Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_total_order_price_procedure(order_id):
    
        # Connect to MySQL database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Call the stored procedure
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)

# Fetch the result
        result = cursor.fetchone()[0]
        cursor.close()
        return result
        


       
       

       



# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    conn.commit()

    # Closing the cursor
    cursor.close()
            



# Call the function to get max order_id

#if __name__ == "__main__":
   
    #max_oid = get_max_order_id()
    #print(max_oid)
    
