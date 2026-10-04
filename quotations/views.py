from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from django.contrib import messages
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .db import execute, execute_insert, fetch_all, fetch_one
from .pdf import generate_quotation_pdf


def money(value):
    try:
        return Decimal(str(value or "0"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def generate_quotation_number():
    with transaction.atomic():
        row = fetch_one(
            "SELECT last_number FROM quotation_sequence WHERE id = 1 FOR UPDATE"
        )
        next_number = int(row["last_number"]) + 1
        execute(
            "UPDATE quotation_sequence SET last_number = %s WHERE id = 1",
            [next_number],
        )
        return f"VNPJ{next_number:04d}"


def dashboard(request):
    stats = {
        "customer_count": fetch_one(
            "SELECT COUNT(*) AS count FROM quotation_customer"
        )["count"],
        "quotation_count": fetch_one(
            "SELECT COUNT(*) AS count FROM quotation"
        )["count"],
        "quotation_value": fetch_one(
            "SELECT COALESCE(SUM(grand_total),0) AS total FROM quotation"
        )["total"],
    }

    quotations = fetch_all(
        """
        SELECT q.id, q.quotation_number, q.quotation_date,
               q.grand_total, q.status, c.name AS customer_name
        FROM quotation q
        JOIN quotation_customer c ON c.id = q.customer_id
        ORDER BY q.id DESC
        LIMIT 10
        """
    )

    return render(
        request,
        "quotations/dashboard.html",
        {"stats": stats, "quotations": quotations},
    )


def customer_list(request):
    customers = fetch_all(
        """
        SELECT id, name, whatsapp_number, email, address
        FROM quotation_customer
        ORDER BY name
        """
    )
    return render(
        request,
        "quotations/customer_list.html",
        {"customers": customers},
    )


def customer_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        whatsapp = request.POST.get("whatsapp_number", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()

        if not name or not whatsapp:
            messages.error(request, "Customer name and WhatsApp number are required.")
        else:
            execute_insert(
                """
                INSERT INTO quotation_customer
                    (name, whatsapp_number, email, address)
                VALUES (%s, %s, %s, %s)
                """,
                [name, whatsapp, email or None, address],
            )
            messages.success(request, "Customer created successfully.")
            return redirect("customer_list")

    return render(request, "quotations/customer_form.html", {"customer": None})


def customer_edit(request, customer_id):
    customer = get_object_or_404_customer(customer_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        whatsapp = request.POST.get("whatsapp_number", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()

        execute(
            """
            UPDATE quotation_customer
            SET name=%s, whatsapp_number=%s, email=%s, address=%s
            WHERE id=%s
            """,
            [name, whatsapp, email or None, address, customer_id],
        )
        messages.success(request, "Customer updated successfully.")
        return redirect("customer_list")

    return render(
        request,
        "quotations/customer_form.html",
        {"customer": customer},
    )


def customer_delete(request, customer_id):
    if request.method == "POST":
        try:
            execute(
                "DELETE FROM quotation_customer WHERE id=%s",
                [customer_id],
            )
            messages.success(request, "Customer deleted.")
        except Exception:
            messages.error(
                request,
                "This customer cannot be deleted because quotations exist for this customer.",
            )
    return redirect("customer_list")


def get_object_or_404_customer(customer_id):
    customer = fetch_one(
        """
        SELECT id, name, whatsapp_number, email, address
        FROM quotation_customer
        WHERE id=%s
        """,
        [customer_id],
    )
    if not customer:
        raise Http404("Customer not found.")
    return customer


def product_list(request):
    products = fetch_all(
        """
        SELECT id, name, category, unit, default_price,
               tax_percentage, is_active
        FROM quotation_product
        ORDER BY name
        """
    )
    return render(
        request,
        "quotations/product_list.html",
        {"products": products},
    )


def product_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        unit = request.POST.get("unit", "NOS").strip()
        price = money(request.POST.get("default_price"))
        tax = money(request.POST.get("tax_percentage"))

        if not name:
            messages.error(request, "Product name is required.")
        else:
            execute_insert(
                """
                INSERT INTO quotation_product
                    (name, category, unit, default_price, tax_percentage)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [name, category, unit, price, tax],
            )
            messages.success(request, "Product created successfully.")
            return redirect("product_list")

    return render(request, "quotations/product_form.html", {"product": None})


def product_edit(request, product_id):
    product = fetch_one(
        """
        SELECT id, name, category, unit, default_price, tax_percentage
        FROM quotation_product
        WHERE id=%s
        """,
        [product_id],
    )
    if not product:
        raise Http404("Product not found.")

    if request.method == "POST":
        execute(
            """
            UPDATE quotation_product
            SET name=%s, category=%s, unit=%s,
                default_price=%s, tax_percentage=%s
            WHERE id=%s
            """,
            [
                request.POST.get("name", "").strip(),
                request.POST.get("category", "").strip(),
                request.POST.get("unit", "NOS").strip(),
                money(request.POST.get("default_price")),
                money(request.POST.get("tax_percentage")),
                product_id,
            ],
        )
        messages.success(request, "Product updated successfully.")
        return redirect("product_list")

    return render(
        request,
        "quotations/product_form.html",
        {"product": product},
    )


def product_delete(request, product_id):
    if request.method == "POST":
        execute(
            "UPDATE quotation_product SET is_active=0 WHERE id=%s",
            [product_id],
        )
        messages.success(request, "Product deactivated.")
    return redirect("product_list")


def quotation_create(request):
    customers = fetch_all(
        """
        SELECT id, name, whatsapp_number, email, address
        FROM quotation_customer
        ORDER BY name
        """
    )
    products = fetch_all(
        """
        SELECT id, name, unit, default_price, tax_percentage
        FROM quotation_product
        WHERE is_active=1
        ORDER BY name
        """
    )

    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        descriptions = request.POST.getlist("description[]")
        quantities = request.POST.getlist("quantity[]")
        units = request.POST.getlist("unit[]")
        prices = request.POST.getlist("price[]")
        tax_rates = request.POST.getlist("tax[]")

        if not customer_id:
            messages.error(request, "Please select a customer.")
            return render(
                request,
                "quotations/quotation_create.html",
                {"customers": customers, "products": products},
            )

        if not descriptions:
            messages.error(request, "Add at least one quotation item.")
            return render(
                request,
                "quotations/quotation_create.html",
                {"customers": customers, "products": products},
            )

        items = []
        subtotal = Decimal("0")
        sgst = Decimal("0")
        cgst = Decimal("0")

        for i, description in enumerate(descriptions):
            description = description.strip()
            if not description:
                continue

            qty = money(quantities[i])
            price = money(prices[i])
            tax = money(tax_rates[i] if i < len(tax_rates) else "0")

            line_total = qty * price
            tax_amount = line_total * tax / Decimal("100")

            subtotal += line_total
            # V1 assumes intra-state split tax when tax is supplied.
            sgst += tax_amount / Decimal("2")
            cgst += tax_amount / Decimal("2")

            items.append(
                {
                    "description": description,
                    "quantity": qty,
                    "unit": units[i],
                    "price": price,
                    "total": line_total,
                    "tax": tax,
                    "tax_amount": tax_amount,
                }
            )

        grand_total = subtotal + sgst + cgst
        quotation_number = generate_quotation_number()
        terms = request.POST.get("terms_conditions", "").strip()

        with transaction.atomic():
            quotation_id = execute_insert(
                """
                INSERT INTO quotation
                    (quotation_number, customer_id, quotation_date,
                     subtotal, sgst, cgst, grand_total, status,
                     terms_conditions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    quotation_number,
                    customer_id,
                    timezone.localdate(),
                    subtotal,
                    sgst,
                    cgst,
                    grand_total,
                    "GENERATED",
                    terms,
                ],
            )

            for item in items:
                execute_insert(
                    """
                    INSERT INTO quotation_item
                        (quotation_id, description, quantity, unit,
                         price, total, tax_percentage, tax_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        quotation_id,
                        item["description"],
                        item["quantity"],
                        item["unit"],
                        item["price"],
                        item["total"],
                        item["tax"],
                        item["tax_amount"],
                    ],
                )

        messages.success(
            request,
            f"Quotation {quotation_number} created successfully.",
        )
        return redirect("quotation_detail", quotation_id=quotation_id)

    return render(
        request,
        "quotations/quotation_create.html",
        {"customers": customers, "products": products},
    )


def get_quotation(quotation_id):
    quotation = fetch_one(
        """
        SELECT q.*, c.name AS customer_name,
               c.whatsapp_number, c.email AS customer_email,
               c.address AS customer_address
        FROM quotation q
        JOIN quotation_customer c ON c.id = q.customer_id
        WHERE q.id=%s
        """,
        [quotation_id],
    )
    if not quotation:
        raise Http404("Quotation not found.")

    quotation["items"] = fetch_all(
        """
        SELECT *
        FROM quotation_item
        WHERE quotation_id=%s
        ORDER BY id
        """,
        [quotation_id],
    )

    quotation["company"] = fetch_one(
        """
        SELECT *
        FROM quotation_company
        ORDER BY id
        LIMIT 1
        """
    )

    return quotation


def quotation_detail(request, quotation_id):
    quotation = get_quotation(quotation_id)
    return render(
        request,
        "quotations/quotation_detail.html",
        {"quotation": quotation},
    )


def quotation_pdf(request, quotation_id):
    quotation = get_quotation(quotation_id)
    pdf_path = generate_quotation_pdf(quotation)

    execute(
        """
        UPDATE quotation
        SET pdf_path=%s
        WHERE id=%s
        """,
        [str(pdf_path), quotation_id],
    )

    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename=f"{quotation['quotation_number']}.pdf",
        content_type="application/pdf",
    )


def quotation_whatsapp(request, quotation_id):
    quotation = get_quotation(quotation_id)

    phone = "".join(
        ch for ch in str(quotation["whatsapp_number"])
        if ch.isdigit()
    )

    message = (
        f"Hello {quotation['customer_name']},\n\n"
        f"Thank you for your enquiry with "
        f"{quotation['company']['company_name']}.\n\n"
        f"Your quotation {quotation['quotation_number']} "
        f"is ready.\n"
        f"Quotation Amount: ₹{quotation['grand_total']}\n\n"
        f"Regards,\n"
        f"{quotation['company']['company_name']}"
    )

    url = f"https://wa.me/{phone}?text={quote(message)}"

    return redirect(url)
