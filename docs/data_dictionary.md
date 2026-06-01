# Data Dictionary

| Column | Meaning |
|---|---|
| `invoice_no` | Invoice/order identifier. Values starting with `C` represent cancellations. |
| `stock_code` | Product stock code. |
| `description` | Product description. |
| `quantity` | Units purchased or returned. |
| `invoice_date` | Transaction timestamp. |
| `unit_price` | Price per unit. |
| `customer_id` | Customer identifier. |
| `country` | Customer country. |
| `is_cancelled` | Boolean flag for cancelled invoices. |
| `gross_revenue` | `quantity * unit_price`. |
| `net_revenue` | Revenue counted for non-cancelled sales. |
| `order_date` | Date extracted from invoice timestamp. |
| `month` | Invoice month. |
| `day_name` | Day of week. |
| `hour` | Hour of day. |

