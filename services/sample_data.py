SAMPLE_SERVICES = [
    {"name": "Nexora Billing", "category": "Finance", "color": "#b8f5d0", "is_published": True,
     "description": "Send invoices, track payments and download statements.",
     "url": "https://billing.example.com"},
    {"name": "Stock Manager", "category": "Operations", "color": "#ffd66b", "is_published": True,
     "description": "Track inventory levels, suppliers and reorder points.",
     "url": "https://stock.example.com"},
    {"name": "Bookings", "category": "Customers", "color": "#9fd0ff", "is_published": True,
     "description": "Let customers book appointments and manage your calendar.",
     "url": "https://book.example.com"},
    {"name": "HR Hub", "category": "People", "color": "#ffb3c7", "is_published": True,
     "description": "Leave requests, payslips and staff records in one place.",
     "url": "https://hr.example.com"},
    {"name": "Training Academy", "category": "People", "color": "#d6c2ff", "is_published": True,
     "description": "Online courses and certificates for staff and partners.",
     "url": "https://learn.example.com"},
    {"name": "Help Desk", "category": "Customers", "color": "#ffc89e", "is_published": True,
     "description": "Log support tickets and follow their progress.",
     "url": "https://help.example.com"},
    {"name": "Analytics", "category": "Operations", "color": "#c9f0ff", "is_published": False,
     "description": "Sales and usage reports across all services.",
     "url": "https://data.example.com"},
]

SAMPLE_FAQS = [
    ("Do I need a separate login for each service?",
     "Yes, for now. Each service manages its own accounts. Single sign-on is planned."),
    ("A service link isn’t opening",
     "Check the status list. If the service shows online, clear your browser cache or "
     "try another browser, then contact us."),
    ("How do I request a new service?",
     "Use the contact form and pick “General enquiry”. Describe what you need."),
    ("Where is my data stored?",
     "Each service stores its own data. See the privacy page on that service’s site."),
]


def reset_services(Service):
    """Replace every service with the sample set. Works with real or historical models."""
    from django.utils.text import slugify

    Service.objects.all().delete()
    Service.objects.bulk_create([
        Service(slug=slugify(item["name"]), display_order=i, status="online", **item)
        for i, item in enumerate(SAMPLE_SERVICES, start=1)
    ])
