// ==========================================================================
// FIX-KAR — Shared site behaviour
// Injects the header/footer on inner pages, wires up the mobile menu,
// the enquiry/track forms, and the interactive plans pricing table.
// ==========================================================================

const page = document.body.dataset.page || "";
const active = (name) => (page === name ? ' class="active"' : "");

// ---- Backend API base URL -------------------------------------------------
// Local dev: the site is opened via a static server (e.g. VS Code Live
// Server on 127.0.0.1:5500) while the FastAPI backend runs separately on
// localhost:8000. In production the API is expected to be reverse-proxied
// on the same domain under /api/v1 (see backend/README.md), so a relative
// path is used there instead.
const API_BASE =
  location.hostname === "localhost" || location.hostname === "127.0.0.1"
    ? "http://localhost:8000/api/v1"
    : "/api/v1";

// ---- Shared header ---------------------------------------------------
const headerTarget = document.querySelector("[data-site-header]");
if (headerTarget) {
  headerTarget.innerHTML = `
    <header class="header">
      <nav class="nav wrap">
        <a href="/"><img class="logo" src="assets/fix-kar-logo.png" alt="FIX-KAR – Affordable, Reliable, Fast"></a>
        <div class="navlinks">
          <a${active("home")} href="/">Home</a>
          <a${active("services")} href="/services">Services</a>
          <a${active("plans")} href="/plans">Plans</a>
          <a${active("how")} href="/how-it-works">How it works</a>
          <a${active("business")} href="/business">For Business</a>
          <a${active("about")} href="/about">About</a>
          <a${active("contact")} href="/contact">Contact</a>
        </div>
        <div class="actions">
          <a class="btn btn-secondary" href="/track">Track Request</a>
          <a class="btn btn-primary" href="/contact">Book Service</a>
          <button class="menu" aria-label="Toggle menu">☰</button>
        </div>
      </nav>
    </header>
  `;
}

// ---- Shared footer -----------------------------------------------------
const footerTarget = document.querySelector("[data-site-footer]");
if (footerTarget) {
  footerTarget.innerHTML = `
    <footer>
      <div class="wrap">
        <div class="footer-grid">
          <div>
            <img class="footer-logo" src="assets/fix-kar-logo.png" alt="FIX-KAR">
            <p>Affordable, reliable and convenient home appliance service support from Pali, Rajasthan.</p>
          </div>
          <div>
            <h4>Explore</h4>
            <a href="/services">Services</a>
            <a href="/plans">Plans</a>
            <a href="/about">About Us</a>
            <a href="/faq">FAQ</a>
          </div>
          <div>
            <h4>Contact</h4>
            <a href="tel:+918824276600">+91 88242 76600</a>
            <a href="mailto:support@fix-kar.in">support@fix-kar.in</a>
            <a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=279%2C%20Ashapura%20Nagar%2C%20Pali%20306401">279, Ashapura Nagar, Pali 306401</a>
          </div>
          <div>
            <h4>Policies</h4>
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
            <a href="/cancellation">Cancellation Policy</a>
            <a href="/refund">Refund Policy</a>
          </div>
        </div>
        <div class="footer-bottom">© 2026 FIX-KAR. All rights reserved.</div>
      </div>
    </footer>
  `;
}

// ---- Mobile menu toggle --------------------------------------------------
const menuButton = document.querySelector(".menu");
if (menuButton) {
  menuButton.addEventListener("click", () => {
    document.querySelector(".header").classList.toggle("mobile-open");
  });
}

document.querySelectorAll(".navlinks a").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelector(".header").classList.remove("mobile-open");
  });
});

// ---- Shared helper: show a success/error message in a form's .notice -----
function showNotice(form, message, isError) {
  const notice = form.querySelector(".notice");
  if (!notice) return;
  notice.textContent = message;
  notice.classList.toggle("is-error", Boolean(isError));
  notice.style.display = "block";
}

// ---- Enquiry form (home + contact page) -----------------------------------
// Submits directly to the FastAPI booking endpoint and shows the booking
// reference returned by the backend instead of a static placeholder message.
const enquiryForm = document.querySelector("#enquiry-form");
if (enquiryForm) {
  const submitButton = enquiryForm.querySelector('button[type="submit"]');
  const submitButtonDefaultText = submitButton ? submitButton.textContent : "";

  enquiryForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const emailValue = enquiryForm.querySelector("#email").value.trim();
    const payload = {
      full_name: enquiryForm.querySelector("#name").value.trim(),
      phone: enquiryForm.querySelector("#mobile").value.trim(),
      email: emailValue || undefined,
      city: enquiryForm.querySelector("#city").value.trim(),
      service: enquiryForm.querySelector("#category").value,
      message: enquiryForm.querySelector("#message").value.trim(),
    };

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Submitting…";
    }

    try {
      const response = await fetch(`${API_BASE}/bookings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => null);

      if (response.ok && data && data.success) {
        showNotice(
          enquiryForm,
          `Thank you, ${data.booking.customer_name}. Your booking reference is ${data.booking.booking_reference} — save it to track your request. Our team will contact you to confirm availability.`,
          false
        );
        enquiryForm.reset();
        const cityField = enquiryForm.querySelector("#city");
        if (cityField) cityField.value = "Pali";
      } else {
        const message = (data && data.error && data.error.message) || "Something went wrong submitting your enquiry. Please call or email FIX-KAR instead.";
        showNotice(enquiryForm, message, true);
      }
    } catch (networkError) {
      showNotice(enquiryForm, "Could not reach the FIX-KAR server. Please check your connection or call us instead.", true);
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = submitButtonDefaultText;
      }
    }
  });
}

// ---- Track-request form ---------------------------------------------------
// Looks up a booking by reference + mobile number via the FastAPI backend.
const trackForm = document.querySelector("#track-form");
if (trackForm) {
  const submitButton = trackForm.querySelector('button[type="submit"]');
  const submitButtonDefaultText = submitButton ? submitButton.textContent : "";

  trackForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const reference = trackForm.querySelector("#request").value.trim();
    const phone = trackForm.querySelector("#phone").value.trim();

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Checking…";
    }

    try {
      const url = `${API_BASE}/bookings/${encodeURIComponent(reference)}?phone=${encodeURIComponent(phone)}`;
      const response = await fetch(url);
      const data = await response.json().catch(() => null);

      if (response.ok && data && data.success) {
        const booking = data.booking;
        showNotice(
          trackForm,
          `${booking.service.name} — status: ${booking.status}. Booked by ${booking.customer_name} in ${booking.city}.`,
          false
        );
      } else {
        const message = (data && data.error && data.error.message) || "We could not find a booking with that reference and mobile number.";
        showNotice(trackForm, message, true);
      }
    } catch (networkError) {
      showNotice(trackForm, "Could not reach the FIX-KAR server. Please check your connection or call us instead.", true);
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = submitButtonDefaultText;
      }
    }
  });
}

// ---- Plans page: interactive pricing table -------------------------------
const plansApp = document.querySelector("#plans-app");
if (plansApp) {
  const plans = {
    domestic: {
      label: "Domestic",
      prices: [199, 299, 499],
      tiers: [
        [
          "Essential",
          "For essential household coverage",
          [
            "Up to 2 registered appliances",
            "Priority booking support",
            "Digital service record",
            "15-day workmanship support",
          ],
        ],
        [
          "Plus",
          "For growing households",
          [
            "Up to 4 registered appliances",
            "Priority technician assignment",
            "Preventive service reminders",
            "30-day workmanship support",
          ],
        ],
        [
          "Complete",
          "For complete home convenience",
          [
            "Up to 7 registered appliances",
            "Priority inspection support",
            "Preventive maintenance benefits",
            "60-day workmanship support",
          ],
        ],
      ],
    },
    corporate: {
      label: "Corporate",
      prices: [1499, 1999, 2499],
      tiers: [
        [
          "Business Essential",
          "For a single office or shop",
          [
            "Up to 10 registered assets",
            "Central service contact",
            "Consolidated service updates",
            "Standard response priority",
          ],
        ],
        [
          "Business Plus",
          "For growing teams",
          [
            "Up to 20 registered assets",
            "Scheduled preventive visits",
            "Priority response coordination",
            "Consolidated service summary",
          ],
        ],
        [
          "Business Complete",
          "For larger operations",
          [
            "Up to 35 registered assets",
            "Multi-category appliance coverage",
            "Priority escalation support",
            "Account coordination",
          ],
        ],
      ],
    },
    institutional: {
      label: "Institutional",
      prices: [1999, 3499, 4999],
      tiers: [
        [
          "Institution Essential",
          "For small institutions",
          [
            "Up to 20 registered assets",
            "Central request management",
            "Scheduled maintenance support",
            "Standard reporting",
          ],
        ],
        [
          "Institution Plus",
          "For multi-department facilities",
          [
            "Up to 40 registered assets",
            "Preventive visit calendar",
            "Priority service coordination",
            "Consolidated reporting",
          ],
        ],
        [
          "Institution Complete",
          "For high-usage facilities",
          [
            "Up to 70 registered assets",
            "Custom preventive schedule",
            "Priority escalation pathway",
            "Dedicated coordination support",
          ],
        ],
      ],
    },
  };

  let selectedPlan = "domestic";
  let billingPeriod = "monthly";

  const grid = document.querySelector("#price-grid");
  const formatMoney = (amount) => "₹" + Math.round(amount).toLocaleString("en-IN");

  function render() {
    const plan = plans[selectedPlan];
    plansApp.classList.toggle("yearly-mode", billingPeriod === "yearly");

    grid.innerHTML = plan.tiers
      .map(([name, description, features], index) => {
        const monthly = plan.prices[index];
        const yearly = Math.round(monthly * 12 * 0.85);
        const isFeatured = index === 1;
        const price = billingPeriod === "monthly" ? monthly : yearly;
        const unit = billingPeriod === "monthly" ? "month" : "year";
        const savings = monthly * 12 - yearly;

        return `
          <article class="price-card${isFeatured ? " featured" : ""}">
            ${isFeatured ? '<span class="eyebrow">Recommended</span>' : `<span class="kicker">${plan.label}</span>`}
            <div class="plan-name">${name}</div>
            <p>${description}</p>
            <div class="price">${formatMoney(price)} <small>/${unit}</small></div>
            <p class="yearly-saving">You save ${formatMoney(savings)} per year</p>
            <ul>${features.map((feature) => `<li>${feature}</li>`).join("")}</ul>
            <a class="btn ${isFeatured ? "btn-primary" : "btn-secondary"}" href="/contact">Choose ${name}</a>
          </article>
        `;
      })
      .join("");
  }

  document.querySelectorAll(".plan-tab").forEach((button) => {
    button.addEventListener("click", () => {
      selectedPlan = button.dataset.plan;
      document.querySelectorAll(".plan-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
      render();
    });
  });

  document.querySelectorAll(".billing-tab").forEach((button) => {
    button.addEventListener("click", () => {
      billingPeriod = button.dataset.billing;
      document.querySelectorAll(".billing-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
      render();
    });
  });

  render();
}
