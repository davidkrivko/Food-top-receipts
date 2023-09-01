import os


def get_pdf_file_path(instance, filename=None):
    return os.path.join("pdf", f"{instance.order.id}_{instance.get_type_display()}.pdf")
