# Billing standards

- Money is never a float in new code. Use `decimal.Decimal` and quantize to 2 places.
- Every function that changes an amount logs the before and after values.
- Tax rates come from `config/tax_rates.yaml`; never hard-code them.
