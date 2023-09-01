import base64
import json
import os

import requests
from django.conf import settings
from django.template.loader import render_to_string

from receipts_service.celery import app
from restaurants.file_path import get_pdf_file_path
from restaurants.models import ReceiptModel, OrderModel, PrinterModel


@app.task
def generate_receipts_for_order(order_id):
    try:
        order = OrderModel.objects.get(pk=order_id)
    except OrderModel.DoesNotExist:
        return f"Order with ID {order_id} does not exist."

    # Check if receipts for this order have already been created
    if ReceiptModel.objects.filter(order=order).exists():
        return f"Receipts for order {order_id} have already been generated."

    printers = PrinterModel.objects.filter(restaurant=order.restaurant)
    if not printers.exists():
        return f"No printers available for the restaurant of order {order_id}."

    receipt_types = [0, 1]
    for r_type in receipt_types:
        receipt = ReceiptModel.objects.create(type=r_type, order=order)
        generate_receipt_pdf.delay(receipt.id)


@app.task
def generate_receipt_pdf(receipt_id):
    try:
        receipt_instance = ReceiptModel.objects.get(pk=receipt_id)
    except ReceiptModel.DoesNotExist:
        return f"Receipt with ID {receipt_id} does not exist."

    url = "http://localhost:32768/"

    if receipt_instance.type == 0:
        context = {
            "order_dishes": receipt_instance.order.order_dishes.all(),
            "order_number": receipt_instance.order.id,
            "total": receipt_instance.order.total,
            "restaurant": receipt_instance.order.restaurant,
        }
        html_content = render_to_string("receipts/client_pattern.html", context)
    else:
        context = {
            "order_dishes": receipt_instance.order.order_dishes.all(),
            "order_number": receipt_instance.order.id,
        }
        html_content = render_to_string("receipts/kitchen_pattern.html", context)

    encoded_html = base64.b64encode(html_content.encode()).decode("utf-8")

    data = {
        "contents": encoded_html,
    }
    headers = {
        "Content-Type": "application/json",
    }
    output_pdf_path = get_pdf_file_path(receipt_instance, "")
    absolute_output_path = os.path.join(settings.MEDIA_ROOT, output_pdf_path)

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        with open(absolute_output_path, "wb") as f:
            f.write(response.content)
        receipt_instance.pdf_file = output_pdf_path
        receipt_instance.save()
        return True
    except requests.RequestException as e:
        raise Exception(f"Error occurred while generating PDF: {e}")
