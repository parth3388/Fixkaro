# Backend Assumptions

This backend was built directly from the existing frontend's actual markup
and behaviour (`index.html`, `contact.html`, `track.html`, `script.js`), not
from an invented booking flow. Where the frontend was ambiguous or silent
about something, the smallest reasonable assumption was made rather than
changing the frontend. Every such assumption is listed here.

## 1. What the frontend actually does today (before this backend)

- There is **no** JavaScript API call, `localStorage`/`sessionStorage` usage,
  or mock booking logic anywhere in `script.js`. The `#enquiry-form` submit
  handler just showed a static "thank you" notice and reset the form. The
  `#track-form` submit handler just showed a static "tracking is being
  connected" notice. Both were 100% cosmetic.
- Two pages embed the same `#enquiry-form` markup (`index.html` and
  `contact.html`), with one difference: `contact.html`'s service `<select>`
  has an extra `Business or Institutional` option that `index.html` doesn't.
- The service `<option>` elements have **no `value` attribute**, so the
  browser submits the option's visible text (e.g. `"AC & Cooling"`) as the
  value. There are no service IDs anywhere in the existing frontend.
- `plans.html` renders subscription-style pricing (Domestic/Corporate/
  Institutional × Monthly/Yearly) entirely client-side from a hardcoded
  object in `script.js`. Every "Choose <plan>" button just links to
  `contact.html` — there is no booking or payment action tied to a plan.
- `track.html` collects a **service request number** and a **registered
  mobile number**, but never checks them against anything.

## 2. Assumptions made

### a. No customer accounts / authentication
The frontend has no login, signup, or session UI anywhere. Per the task
instructions ("do not add customer authentication unless the product
requirements actually require it"), booking creation is **anonymous**: no
password, no token, no account. A lightweight `customers` table still exists
to de-duplicate repeat bookers by phone number (upsert-by-phone), but it
holds no credentials — see `app/models/customer.py`.

### b. "Track booking" is verified by phone, not by reference alone
`GET /api/v1/bookings/{booking_reference}` requires a `phone` query
parameter that must match the booking's customer. This isn't explicitly
required by the task's example endpoint signature, but `track.html`'s form
already collects both the reference **and** the registered mobile number, so
enforcing the match:
- matches the existing UI's own data collection exactly (no frontend change
  needed to add a phone field — it was already there), and
- prevents a booking reference alone (an 8-character public string) from
  being enough to look up someone else's name, service and notes.

A wrong reference and a right-reference-wrong-phone both return an identical
404, so the endpoint can't be used to probe which references exist.

The same phone check is required by `POST /bookings/{ref}/cancel`.

### c. Service catalog is a fixed, seeded list — not admin-managed
The frontend's service `<select>` options are static HTML, not
dynamically rendered from any API today. The backend seeds a `services`
table (via the initial Alembic migration, from `app/seed_data.py`) with one
row per existing `<option>`, using the **exact visible text** as `name` (e.g.
`"AC & Cooling"`, `"Business or Institutional"`) plus a generated `slug`
(e.g. `ac-cooling`). `POST /bookings` matches the incoming `service` field
against either `name` or `slug`, case-insensitively — so the existing
`<select>` needed **zero HTML changes** to work with the new backend.
`GET /api/v1/services` now exists so the frontend *could* switch to
rendering the category list from the API later, but nothing requires that
today.

### d. No booking date/time fields
The current `#enquiry-form` collects: full name, mobile, email, city,
service category, and a free-text issue description. **There is no date or
time picker anywhere in the UI.** Rather than adding new form fields (which
the task explicitly says not to do unless strictly required), `Booking.
booking_date` and `Booking.booking_time` are nullable columns, present for
forward compatibility, always `null` from the current frontend. This is
consistent with the site's own copy: "Our team reviews your enquiry and
confirms service availability" (i.e. scheduling happens over a phone call
after the enquiry, not on the site).

### e. No street address field — only "city"
The form only has a `City` input (defaulting to `"Pali"`). There is no
street-address field. `Booking.address_city` stores exactly that. Any more
specific address the customer wants to give has to go in the free-text
"issue" field, same as today.

### f. Booking reference format
The task's own example (`FIX-XXXXXXXX`) was used: `FIX-` followed by 8
random uppercase letters/digits, generated with Python's `secrets` module
(not `random`) so references can't be guessed or enumerated. This differs
slightly from `track.html`'s old placeholder text (`"Example: FK-1024"`),
which was a static hint for a booking system that didn't exist yet. That
placeholder was updated to `"Example: FIX-A1B2C3D4"` so it now shows the
real format — the only other frontend text change made.

### g. No payment integration
Nothing in the frontend collects payment details or references a payment
provider. `plans.html` is a pricing *display* page whose buttons link to
`contact.html`, not to any checkout flow. Per the task instructions, no
Razorpay/Stripe/etc. integration was added.

### h. No admin dashboard / admin API
There is no admin frontend anywhere in the existing site. No admin API,
authentication, or dashboard was built. The data model (explicit
`BookingStatus` enum, `updated_at`/`cancelled_at` timestamps, indexed
`status` column) is deliberately shaped so an admin API to move a booking
through `PENDING → CONFIRMED → ASSIGNED → IN_PROGRESS → COMPLETED` could be
added later behind real authentication, without a schema change.

### i. No third-party notifications (SMS/email/WhatsApp)
The site links directly to `tel:`, `mailto:`, and `wa.me` — it doesn't
integrate any provider programmatically today. No notification provider was
added. If one is added later, it should sit behind a `NotificationService`
abstraction so a booking's creation never fails just because, say, an SMS
provider is down. (No such service exists yet since nothing currently calls
it — this is a placeholder note for the next change, not implemented code.)

### j. Testing uses SQLite, not PostgreSQL
The task asks for PostgreSQL and an "isolated test setup" that doesn't
depend on production credentials. `tests/` uses an in-memory SQLite database
(created directly from the SQLAlchemy models) rather than spinning up a
second PostgreSQL instance for CI/local test runs — this keeps `pytest`
runnable with zero external services. This is a deliberate trade-off:
- The **schema itself** (types, the native Postgres `booking_status` ENUM,
  indexes, foreign keys) is verified separately by actually running
  `alembic upgrade head` / `downgrade base` against real PostgreSQL in
  Docker (see README "Running tests" and "Verification performed").
- All 19 `pytest` tests only exercise ORM-level behaviour and HTTP
  contracts (validation, status codes, response shape), none of which is
  Postgres-specific.
- If true Postgres-backed integration tests are wanted later, point
  `TEST_DATABASE_URL` in `tests/conftest.py` at a second Postgres database
  (e.g. `fixkar_test`) instead of SQLite.

### k. CORS origins default to VS Code Live Server ports
`.env.example` defaults `CORS_ORIGINS` to `http://127.0.0.1:5500,http://
localhost:5500` because that's how this static site is served locally (the
screenshots in this project's history show `127.0.0.1:5500`). Production
origins must be set explicitly via the `CORS_ORIGINS` environment variable
— `allow_origins=["*"]` is never used.

### l. `email` is optional, matching the existing form
`#email` has no `required` attribute in either `index.html` or
`contact.html`'s enquiry form, so it's optional in `BookingCreate` too
(validated as a real email address only if provided).
