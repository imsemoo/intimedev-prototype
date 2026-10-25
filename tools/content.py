"""Site content. Facts come from intimedev.com (read 25 Oct 2026); see docs/01-brand-discovery.md.
Nothing here may claim clients, results, awards or certifications that the company has not published."""

EMAIL = "info@intimedev.com"
PHONE = "+20 115 388 6625"
PHONE_HREF = "+201153886625"
WHATSAPP = "https://wa.me/201153886625"

# Where the site is published; used for absolute Open Graph URLs. Change to https://intimedev.com/ at launch.
SITE_URL = "https://imsemoo.github.io/intimedev-prototype/"

# JSON form endpoint (Formspree "https://formspree.io/f/<id>", Web3Forms, FormSubmit ajax, or Intimedev's own API).
# Empty: the estimate form composes an email in the visitor's mail app instead of sending.
FORM_ENDPOINT = ""

MARKETS = [
    {"city": "Cairo", "country": "Egypt", "tz": "Africa/Cairo", "weekend": "Fri Sat",
     "note": "Our home base, with local presence and regional business understanding."},
    {"city": "Sydney", "country": "Australia", "tz": "Australia/Sydney", "weekend": "Sat Sun",
     "note": "Years of remote collaboration with Australian businesses across time zones."},
    {"city": "London", "country": "United Kingdom", "tz": "Europe/London", "weekend": "Sat Sun",
     "note": "Long-term development partnerships with UK companies."},
]

# group: build (we make it), connect (we join it to other systems), run (we keep it working)
SERVICES = [
    {
        "slug": "web-applications", "icon": "web", "group": "build", "core": True,
        "name": "Custom web applications",
        "short": "Secure, scalable, business-focused applications.",
        "summary": "Secure, scalable, business-focused web applications built with PHP, CakePHP, Laravel, JavaScript, TypeScript, MySQL and PostgreSQL.",
        "includes": ["Business applications and portals", "Administration panels and dashboards", "REST APIs for web and mobile clients", "Upgrades of existing PHP and CakePHP applications"],
        "stack": ["PHP", "Laravel", "CakePHP", "JavaScript", "TypeScript", "React", "MySQL", "PostgreSQL", "REST APIs"],
        "industries": ["business", "membership", "booking"],
    },
    {
        "slug": "mobile-applications", "icon": "mobile", "group": "build", "core": True,
        "name": "Mobile applications",
        "short": "Cross-platform apps for Android and iOS.",
        "summary": "Responsive, cross-platform mobile applications built with Flutter for Android and iOS, connected to your web portal, API and administration dashboard.",
        "includes": ["Flutter apps for Android and iOS from one codebase", "The API and database the app talks to", "An administration dashboard for your team", "Store releases and ongoing updates"],
        "stack": ["Flutter", "Android", "iOS", "REST APIs", "Laravel", "MySQL"],
        "industries": ["logistics", "events", "booking"],
    },
    {
        "slug": "erp-business-systems", "icon": "erp", "group": "build", "core": True,
        "name": "ERP and business systems",
        "short": "Systems shaped around how you operate.",
        "summary": "Custom ERP platforms, administration systems, workflow automation, reporting dashboards, booking systems and internal tools, shaped around your operations.",
        "includes": ["Custom ERP platforms", "Workflow automation", "Reporting dashboards", "Booking systems and internal tools"],
        "stack": ["Laravel", "PHP", "PostgreSQL", "MySQL", "Xero", "CRM and ERP APIs"],
        "industries": ["business", "logistics", "booking"],
    },
    {
        "slug": "e-commerce", "icon": "commerce", "group": "build", "core": False,
        "name": "E-commerce",
        "short": "Stores, catalogues and payment flows.",
        "summary": "Online stores built and customised with WooCommerce, WordPress, Shopify integrations and custom platforms, with payment flows and order management.",
        "includes": ["WooCommerce and WordPress stores", "Shopify integrations", "Custom store platforms", "Payment flows and order management"],
        "stack": ["WooCommerce", "WordPress", "Shopify integrations", "Stripe", "PayPal", "PHP"],
        "industries": ["commerce", "membership"],
    },
    {
        "slug": "e-learning", "icon": "learning", "group": "build", "core": False,
        "name": "E-learning platforms",
        "short": "Portals, courses and examinations.",
        "summary": "Educational portals, learning management systems, course platforms, examination systems, attendance and student management solutions.",
        "includes": ["Educational portals and LMS", "Course platforms", "Examination systems", "Attendance and student management"],
        "stack": ["Laravel", "PHP", "MySQL", "Flutter", "WordPress"],
        "industries": ["education"],
    },
    {
        "slug": "ai-integrations", "icon": "ai", "group": "connect", "core": True,
        "name": "AI integrations",
        "short": "AI added to the systems you already run.",
        "summary": "AI for content generation, data processing, automation, intelligent search, document analysis and customer support, connected to your existing systems.",
        "includes": ["Content generation", "Data processing and automation", "Intelligent search", "Document analysis and customer support"],
        "stack": ["AI APIs", "Laravel", "PHP", "PostgreSQL", "REST APIs"],
        "industries": ["documents", "business", "education"],
    },
    {
        "slug": "api-integrations", "icon": "api", "group": "connect", "core": False,
        "name": "API and third-party integrations",
        "short": "Payments, CRM, accounting and cloud services.",
        "summary": "Connections to payment gateways, CRM, accounting platforms, cloud storage, email services and external APIs.",
        "includes": ["Payment gateways: Stripe, PayPal", "Accounting: Xero", "CRM and ERP APIs", "Cloud storage and email services"],
        "stack": ["Stripe", "PayPal", "Xero", "Google services", "CRM and ERP APIs", "REST APIs"],
        "industries": ["commerce", "membership", "business"],
    },
    {
        "slug": "file-document-systems", "icon": "files", "group": "connect", "core": False,
        "name": "File storage and document systems",
        "short": "Secure exchange, permissions and backup.",
        "summary": "Secure file exchange, cloud storage, document sharing, permission management, backup and collaboration systems.",
        "includes": ["Secure file exchange", "Cloud storage on S3-compatible services", "Permission management and sharing", "Backup and activity tracking"],
        "stack": ["S3-compatible storage", "Wasabi", "AWS", "Laravel", "Linux"],
        "industries": ["documents", "business"],
    },
    {
        "slug": "server-administration", "icon": "server", "group": "run", "core": False,
        "name": "Server and Linux administration",
        "short": "The servers your software runs on.",
        "summary": "Linux configuration, Apache and Nginx, database management, security hardening, backups, monitoring and optimisation.",
        "includes": ["Linux configuration (including AlmaLinux)", "Apache and Nginx", "Database management and backups", "Security hardening, monitoring and optimisation"],
        "stack": ["Linux", "AlmaLinux", "Apache", "Nginx", "Docker", "MySQL", "MariaDB", "AWS"],
        "industries": ["business", "commerce", "documents"],
    },
    {
        "slug": "maintenance-support", "icon": "support", "group": "run", "core": False,
        "name": "Maintenance and technical support",
        "short": "Upgrades, fixes and long-term care.",
        "summary": "Upgrades, legacy modernisation, bug fixing, security improvements, monitoring, backups and long-term support, including systems other teams walked away from.",
        "includes": ["Legacy modernisation and upgrades", "Bug fixing and security improvements", "Monitoring and backups", "Long-term technical support"],
        "stack": ["PHP", "CakePHP", "Laravel", "Linux", "Git", "Docker"],
        "industries": ["business", "membership", "commerce"],
    },
]

GROUPS = {
    "build": ("Build", "Applications we design and develop."),
    "connect": ("Connect", "How your systems talk to payments, data and AI."),
    "run": ("Run", "The servers and support that keep it all working."),
}

INDUSTRIES = {
    "business": ("Business and enterprise systems", "Custom ERP, administration panels and workflow tools shaped around your operations."),
    "education": ("Education and e-learning", "Learning platforms, examination systems and student management portals."),
    "commerce": ("E-commerce and retail", "Online stores, product catalogues, payment flows and order management."),
    "events": ("Events and ticketing", "Registration, ticketing, seat management and attendee check-in systems."),
    "logistics": ("Logistics and courier services", "Shipment tracking, dispatch management and delivery workflow platforms."),
    "documents": ("Document and file management", "Secure storage, sharing, permissions and document workflow systems."),
    "membership": ("Membership and subscriptions", "Member portals, recurring billing and subscription management platforms."),
    "booking": ("Booking and scheduling", "Appointment booking, resource scheduling and availability management."),
}

STACK = [
    ("Backend", ["PHP", "CakePHP", "Laravel", "REST APIs"]),
    ("Frontend", ["JavaScript", "TypeScript", "HTML5", "CSS3", "React"]),
    ("Mobile", ["Flutter", "Android", "iOS"]),
    ("CMS and e-commerce", ["WordPress", "WooCommerce", "Shopify integrations"]),
    ("Databases", ["MySQL", "MariaDB", "PostgreSQL"]),
    ("Cloud and infrastructure", ["Linux", "AlmaLinux", "Apache", "Nginx", "Docker", "Git", "AWS", "S3-compatible storage", "Wasabi"]),
    ("Integrations", ["Stripe", "PayPal", "Xero", "Google services", "CRM and ERP APIs", "AI APIs"]),
]

PROCESS = [
    ("Discovery", "Understand the business, users, requirements, challenges and project goals."),
    ("Planning", "Define the scope, recommended technologies, timeline, milestones and estimated cost."),
    ("UI and UX design", "Create intuitive interfaces and responsive experiences based on users' needs."),
    ("Development", "Build the solution with clean, secure and maintainable code."),
    ("Testing and deployment", "Test functionality, security, performance, responsiveness and integrations before launch."),
    ("Support and improvement", "Monitor, maintain, upgrade and keep improving the system."),
]

PRINCIPLES = [
    ("Plan before code", "Business-focused planning comes first: scope, stack, milestones and cost are agreed before development starts."),
    ("One team, app to server", "The people who write your application also configure, secure and monitor the server it runs on."),
    ("Legacy is welcome", "We maintain, upgrade and modernise existing systems, including ones other teams walked away from."),
    ("Maintainable by default", "Secure, maintainable development practices, so the system stays affordable to change for years."),
    ("Clear across time zones", "Fourteen years of working with Egypt, Australia and the UK taught us to communicate plainly and on schedule."),
    ("We stay after launch", "Most of our client relationships span years: new features, upgrades, infrastructure and day-to-day support."),
]

BLUEPRINTS = [
    {
        "slug": "business-platform", "name": "Business management platform",
        "summary": "A custom dashboard combining users, workflows, payments, reports, documents and administrative controls.",
        "parts": ["Users and roles", "Workflows", "Payments", "Reports", "Documents", "Administration"],
        "services": ["erp-business-systems", "web-applications", "api-integrations"],
        "industries": ["business", "membership", "booking"],
    },
    {
        "slug": "mobile-web-ecosystem", "name": "Mobile and web ecosystem",
        "summary": "A connected Flutter mobile application, web portal, API, database and administration dashboard.",
        "parts": ["Flutter app", "Web portal", "API", "Database", "Admin dashboard"],
        "services": ["mobile-applications", "web-applications", "server-administration"],
        "industries": ["logistics", "events", "education"],
    },
    {
        "slug": "file-exchange", "name": "Secure file exchange platform",
        "summary": "A secure system for file storage, sharing, access permissions, notifications, backups and activity tracking.",
        "parts": ["Shared space", "Private space", "Permissions", "Notifications", "Backups", "Activity log"],
        "services": ["file-document-systems", "server-administration", "maintenance-support"],
        "industries": ["documents", "business"],
    },
]
