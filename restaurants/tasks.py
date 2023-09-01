import base64
import json
import os

import requests
from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string

from receipts_service.celery import app
from restaurants.file_path import get_pdf_file_path
from restaurants.models import ReceiptModel, OrderModel, PrinterModel


@app.task
def generate_receipts_for_order(order_id):
    try:
        order = OrderModel.objects.get(pk=order_id)
    except OrderModel.DoesNotExist:
        raise Exception(f"Order with ID {order_id} does not exist.")

    # Check if receipts for this order have already been created
    if ReceiptModel.objects.filter(order=order).exists():
        raise Exception(f"Receipts for order {order_id} have already been generated.")

    printers = PrinterModel.objects.filter(restaurant=order.restaurant)
    if not printers.exists():
        raise Exception(f"No printers available for the restaurant of order {order_id}.")

    receipts_to_create = []

    # Prepare the data for bulk creation
    for r_type in [0, 1]:
        for printer in printers:
            receipts_to_create.append(ReceiptModel(type=r_type, order=order, printer=printer))

    with transaction.atomic():
        created_receipts = ReceiptModel.objects.bulk_create(receipts_to_create)

    # Trigger the asynchronous tasks
    for receipt in created_receipts:
        generate_receipt_pdf.delay(receipt.order.id, receipt.type)


@app.task
def generate_receipt_pdf(order_id: int, r_type: int):
    try:
        receipt_instance = ReceiptModel.objects.get(order_id=order_id, type=r_type)
    except ReceiptModel.DoesNotExist:
        raise Exception(f"Receipt for order ID {order_id} does not exist.")

    url = "http://localhost:32769/"

    if r_type == 0:
        context = {
            "order_dishes": receipt_instance.order.order_dishes.all(),
            "order_number": receipt_instance.order.id,
            "total": receipt_instance.order.total,
            "restaurant": receipt_instance.order.restaurant,
            "created": receipt_instance.order.created_at,
        }
        html_content = render_to_string("receipts/client_pattern.html", context)
    else:
        context = {
            "order_dishes": receipt_instance.order.order_dishes.all(),
            "order_number": receipt_instance.order.id,
            "created": receipt_instance.order.created_at,
        }
        html_content = render_to_string("receipts/kitchen_pattern.html", context)

    encoded_html = base64.b64encode(html_content.encode()).decode("utf-8")

    data = {
        "contents": encoded_html,
    }
    headers = {
        "Content-Type": "application/json",
    }
    output_pdf_path = get_pdf_file_path(receipt_instance)
    absolute_output_path = os.path.join(settings.MEDIA_ROOT, output_pdf_path)

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        with open(absolute_output_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        raise Exception(f"Error occurred while generating PDF: {e}")

    receipt_instance.pdf_file = output_pdf_path
    receipt_instance.status = 1
    receipt_instance.save()

    return True
