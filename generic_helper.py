import re

def pattren_match(input_string):
    pattern = r"sessions/([^/]+)/contexts"

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    session_id = match.group(1)

    return session_id

    # Check if the pattern is found

def food_items_list(food_dict: dict):
    formatted_string = ", ".join([f"{int(quantity)} {item}" for item, quantity in food_dict.items()])
    
    return formatted_string


#if __name__ == "__main__":
    #string1 = input("Enter the order ID: ")
    #status = pattren_match(string1)
    #print(f"{status}")
    #food_items({'chole': 1,'samosa': 2})

    