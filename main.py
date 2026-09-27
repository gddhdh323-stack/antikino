import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from rollypay import RollyPayClient
from rollypay.exceptions import RollyPayError

load_dotenv()

client = RollyPayClient(api_key=os.environ.get("API_KEY"))

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def main():
    main_page_stream = open("main.html")

    main_page = main_page_stream.read()

    main_page_stream.close()

    return main_page


@app.get("/success", response_class=HTMLResponse)
def success(orderid: str):
    page_stream = open("success.html")

    page = page_stream.read()

    page_stream.close()

    return page.replace("${orderId}", orderid)


@app.post("/createPayment")
def create_payment(price: int):
    orderid = uuid.uuid4()

    try:
        payment = client.payments.create(
            amount=f"{price}.00",
            order_id=str(orderid),
            payment_method="sbp",
            redirect_url=str(os.environ.get("HOST")) + "/success?orderid=" + str(orderid),
        )
        return RedirectResponse(payment['pay_url'])
    except RollyPayError as e:
        return f"Error: {e}"
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
