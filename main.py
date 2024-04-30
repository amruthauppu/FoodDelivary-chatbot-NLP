from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import logging
logging.basicConfig(level=logging.INFO)
import db_connector
import json
import generic_helper

app = FastAPI()
inprogress_order = {}
total_food_items = []
new_food_dict = {}
total_added_items = {}

class Request(BaseModel):
    responseId: str
    queryResult: dict
    session: str



@app.post("/")
async def webhook_handler(request: Request):
    query_result = request.queryResult
    intent_name = query_result['intent']['displayName']
    parameters = query_result['parameters']
    output_context = query_result['outputContexts']
    sessionId = generic_helper.pattren_match(output_context[0]['name'])


    if intent_name == 'track.order-context: ongoing-tracking':
        return track_order(parameters,sessionId)
    elif intent_name == 'order.add-context: ongoing-order':
        return handle_order_add(parameters,sessionId)
    elif intent_name == 'order.remove-context: ongoing-order':
        return handle_order_remove(parameters,sessionId)
    elif intent_name == 'order.complete- context: ongoing-order':
        return handle_order_complete(sessionId)
    else:
        raise HTTPException(status_code=400, detail="Unknown intent")
  
    
def track_order(parameters,sessionId):
    # Extract parameters
     orderId = int(parameters['order_Id'])

     order_status = db_connector.get_order_status(orderId)

     if order_status:
        fulfillment_Text = f"order status for {orderId} is {order_status}"
     else:
        fulfillment_Text = f"order details with given order number {orderId} is not found"

     return  JSONResponse(content={
        "fulfillmentText" : fulfillment_Text
    })


def handle_order_add(parameters,sessionId):
    # Extract parameters
    
        print(sessionId)
        quantity = parameters['number']
        food_items = parameters['food-items']
        
        if len(food_items) != len(quantity):
            fulfillment_Text = "can you specify the fod items and quantity correctly"
        else:
            
            new_food_dict = dict(zip(food_items,quantity))
            
            if sessionId in inprogress_order:
                current_food_dict = inprogress_order[sessionId]
                current_food_dict.update(new_food_dict)
                print(current_food_dict)
            else:
                inprogress_order[sessionId] = new_food_dict

            total_added_items = inprogress_order[sessionId]
            total_food_items = generic_helper.food_items_list(inprogress_order[sessionId])
    
            fulfillment_Text = f"so far you have addeed {total_food_items} to the order,do you need anything else?"
        
        
        return  JSONResponse(content={
        "fulfillmentText" : fulfillment_Text
    })
    
def handle_order_complete(sessionId):
    print(inprogress_order)
    if sessionId in inprogress_order:
        
        order = inprogress_order[sessionId]
        print(order)
        new_order_id = save_to_db(order)
        if new_order_id == -1:
            fulfillment_Text = f"unable to process the order due to backend error please place the order again"
        else:
            order_total = db_connector.get_total_order_price_procedure(new_order_id)
            fulfillment_Text = f"Hurahh!! you have placed the order "\
                                f"here is your order Id {new_order_id} "\
                                f"your order total is {order_total} which you can pay at the time of delivary"
            
    else:
        fulfillment_Text = f"Unable to process the order. Apolozies!! can you place the order again"

    del inprogress_order[sessionId]
    return  JSONResponse(content={
        "fulfillmentText" : fulfillment_Text
    })

def save_to_db(order: dict):
    next_order_id = db_connector.get_max_order_id()
    
    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        print(f"{food_item},{quantity},{next_order_id}")
        rcode = db_connector.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1
        
    db_connector.insert_order_tracking(next_order_id, "in progress")


    # Now insert order tracking status

    return next_order_id



def handle_order_remove(parameters: dict, session_id):
    if session_id not in inprogress_order:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    current_order = inprogress_order[session_id]
    print(current_order)
    
    food_items = parameters.get('food-items', [])
    quantities = parameters.get('number', [])
    
    fulfillment_text = ""
    
    for food_item, quantity in zip(food_items, quantities):
        if food_item not in current_order:
            fulfillment_text += f"{food_item} is not present in your order. "
        else:
            current_quantity = current_order[food_item]
            if quantity >= current_quantity:
                del current_order[food_item]
                fulfillment_text += f"Removed {quantity} {food_item} from the order. "
            else:
                current_order[food_item] -= quantity
                fulfillment_text += f"Removed {quantity} {food_item} from the order. {current_order} left in the order. "
    
    if not current_order:
        fulfillment_text += "Your order is empty!"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

