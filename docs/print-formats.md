# Corelytic Print Formats

Eleven branded print formats for standard ERPNext / HRMS documents: HR letters, salary slip,
selling, buying and payment documents. The DocTypes stay standard; only the print layout is
custom. Logo, company name, tagline, footer line and colours come from **Corelytic Branding Settings**,
so every format changes when the branding changes.

The formats belong to the **Corelytic Branding** module of `corelytic_erp`. They are standard (`standard: Yes`)
Jinja print formats, created and updated by `bench migrate`.

## Code layout

```text
corelytic_erp/corelytic_erp/
├── corelytic_branding/print_format/        ← all 11 print formats here (one folder each)
│   ├── corelytic_tax_invoice/           (.html + .json)
│   ├── corelytic_quotation/
│   ├── corelytic_salary_slip/
│   └── ... 8 more
├── templates/print/corelytic_print.html ← shared header/footer/CSS (used by all 11)
├── printing.py                     ← Python helpers (logo, GSTIN, HSN...)
├── hooks.py                        ← just a `jinja` block that registers printing.py
└── patches/print_formats/          ← one-time patch for the default formats (already run)
```

| File | Role |
| --- | --- |
| `corelytic_branding/print_format/<name>/<name>.html` | The layout of one format. Frappe reads this file, not the `html` field in the database. |
| `corelytic_branding/print_format/<name>/<name>.json` | The Print Format record: name, DocType, module, margins, `pdf_generator: wkhtmltopdf`. |
| `templates/print/corelytic_print.html` | Jinja macros used by every format: `styles`, `header`, `box`, `totals`, `in_words`, `bank`, `terms`, `signatory`, `footer`, `need`. All CSS is here. |
| `printing.py` | Jinja methods: branding, company details, HSN, party GSTIN, bank account, dates, pronouns, salary rows. |
| `hooks.py` → `jinja = {"methods": [...]}` | Makes the `printing.py` functions callable from templates by name. |
| `patches/print_formats/set_default_print_formats.py` | Ran once (2026-11-08): made the Corelytic formats the default print format of their DocTypes. |

## The formats

| Print format | DocType | Notes |
| --- | --- | --- |
| Corelytic Offer Letter | Job Offer | Offer terms table, Terms & Conditions, candidate acceptance signature |
| Corelytic Appointment Letter | Appointment Letter | Introduction, numbered terms (Appointment Letter content), closing notes; designation from the Job Applicant |
| Corelytic Salary Slip | Salary Slip | Employee details, earnings and deductions side by side, net pay in words. Statistical components and "do not include in total" rows are hidden |
| Corelytic Experience Letter | Employee | Left employee (Relieving Date or status Left): "was employed … from … to …". Active employee: "has been working since …". Pronouns from Gender (he / she, otherwise they) |
| Corelytic Relieving Letter | Employee | Uses Resignation Letter Date and Relieving Date |
| Corelytic Quotation | Quotation | Kind attention (contact), items, taxes, payment terms, bank details |
| Corelytic Tax Invoice | Sales Invoice | Title becomes Credit Note (return) or Debit Note. Billed to / shipped to with GSTIN, HSN/SAC, taxable amount, tax rows, bank details |
| Corelytic Delivery Note | Delivery Note | Consignee, buyer, dispatch details (transporter, vehicle, LR, driver), batch / serial numbers. Amounts hidden when "Print Without Amount" is ticked |
| Corelytic Request for Quotation | Request for Quotation | One supplier per print: Tools > Download PDF picks the supplier, the print preview shows the first one. Empty "Your Rate / Amount" columns for the supplier |
| Corelytic Purchase Order | Purchase Order | Supplier, bill to, ship to, delivery date per item, payment terms |
| Corelytic Payment Receipt | Payment Entry | Receive → "Payment Receipt", Pay → "Payment Voucher", Internal Transfer → "Transfer Voucher". Against-document table and deductions |

Defaults after the patch: each DocType above prints with its Corelytic format, except **Employee**,
which keeps its own default. Pick Corelytic Experience Letter / Corelytic Relieving Letter from the print
format list. To change a default: Customize Form → the DocType → Default Print Format.

## Where the data comes from

| Printed | Source |
| --- | --- |
| Logo | Corelytic Branding Settings → Logo, else Company → Company Logo, else the built-in `public/images/calco-logo-official.svg`. Embedded as a `data:` URI, so PDFs never fetch it over the network |
| Company name, tagline, footer line, colours | Corelytic Branding Settings (blank field = DocType default) |
| Company address | The document's Company Address, else the Company's primary address (Address with "Is Your Company Address") |
| Company GSTIN, phone, email, website | Company → Tax ID, Phone No, Email, Website (phone / email fall back to the address) |
| Customer / Supplier GSTIN | Tax ID on the document, else Customer / Supplier → Tax ID |
| HSN/SAC | India Compliance's `gst_hsn_code` when installed, else Item → Customs Tariff Number |
| Bank details | The company's default Bank Account (Is Company Account, not disabled) |
| Department | Department name without the company suffix ("Production - C" → "Production") |

Data to fill in on a new site, otherwise the header shows only name and tagline:

1. Company → Tax ID (GSTIN), Phone No, Email, Website.
2. An Address linked to the Company with "Is Your Company Address" ticked.
3. A Bank Account with "Is Company Account" ticked (and "Is Default").
4. Item → Customs Tariff Number for the HSN column.

A missing designation or relieving date prints in red as `[Designation not set]` /
`[Relieving Date not set]`, so it is caught before the letter goes out. Draft and cancelled
documents show a DRAFT / CANCELLED badge under the title.

## Changing a format

- **One format:** edit `corelytic_branding/print_format/<name>/<name>.html`.
- **All formats** (header, footer, colours, fonts, totals, signatures): edit
  `templates/print/corelytic_print.html`.
- **New data in a template:** add a function to `printing.py` and list it in `hooks.py` →
  `jinja["methods"]`; the template calls it by function name.
- **New format:** copy a folder in `corelytic_branding/print_format/`, rename the folder and both files to
  the scrubbed name (`Corelytic Proforma Invoice` → `corelytic_proforma_invoice`), set `name` and
  `doc_type` in the `.json`, then run `bench migrate`.

Template skeleton:

```jinja
{%- from "corelytic_erp/templates/print/corelytic_print.html" import styles, header, box, totals, in_words, terms, signatory, footer -%}
{%- set b = corelytic_print_branding(doc) -%}
{{ styles(b) }}
<div class="gp">
	{{ header(b, _("Document Title"), [(_("No"), doc.name), (_("Date"), doc.get_formatted("posting_date"))]) }}
	... body ...
	{{ signatory(b) }}
	{{ footer(b) }}
</div>
```

Do not write `{% set _ = ... %}` in a template: `_` is the translation function and the rest of
the template would break. Use another name (`{% set _x = list.append(...) %}`).

## PDF rules (wkhtmltopdf)

PDFs are made by wkhtmltopdf (old QtWebKit). The templates follow its limits:

- Layout uses tables only: no flexbox, no grid, no CSS variables. Colours are written into the
  CSS by Jinja.
- All CSS is inline in the template, and the logo is a `data:` URI, so no file is fetched.
- **No inline bold inside long paragraphs.** wkhtmltopdf drops the space before a bold run that
  follows a long run of normal text ("dated**09 October**"). Font, `text-rendering`,
  `word-spacing`, `&nbsp;` and px font sizes did not fix it; only `--dpi 300` did, and Frappe
  does not allow per-format options. Bold is fine on its own line, in tables and in headings.
- Letter paragraphs are left aligned (justified text made the gaps worse).
- Only DejaVu fonts are installed in the image; "Inter" in the CSS falls back to DejaVu Sans
  in PDFs and is used in the browser preview.

## Deploying a change

Template / `printing.py` changes: copy the files into the 6 containers, then clear cache;
no migrate. A new format, a changed `.json` or a new patch needs `bench migrate`.

Production (griderp.in) scripts in `~/griderp_build/scripts/`:

| Script | Does |
| --- | --- |
| `deploy-print-prod.sh` | Checks the container's hooks.py / patches.txt equal git HEAD, backs up, saves rollback copies, copies the files into all 6 containers, migrates, clears cache, restarts |
| `build-print-image.sh` | Rebuilds `griderp:latest` on the current image (keeps calco_calls, now corelytic_calls) from git HEAD + the print-format files; tags the old one `griderp:pre-print` |

First deploy (2026-11-08): image `griderp:print-f717290-20261108`, rollback image
`griderp:pre-print`, rollback files `~/griderp_build/rollback/pre-print-20261108_143040/`
(old hooks.py, patches.txt and the previous default print formats).

### Known issue: PDF from the server

wkhtmltopdf loads Frappe's print CSS from the site URL. Inside the containers neither
`griderp.in` nor `localhost:8080` is reachable (only `frontend:8080` is), so
`frappe.get_print(..., as_pdf=True)` from `bench console` fails with HostNotFoundError /
ConnectionRefusedError for **every** format, the standard ones included. The print preview in
the browser is not affected. Whether the PDF button works in the browser was not verified on
2026-11-08; if it fails, the fix belongs to the site / container setup, not to these formats.
