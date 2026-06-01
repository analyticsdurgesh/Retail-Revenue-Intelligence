-- Monthly revenue and order trend
SELECT month, ROUND(SUM(net_revenue), 2) AS revenue, COUNT(DISTINCT invoice_no) AS orders
FROM retail_orders
WHERE is_cancelled = 0 AND quantity > 0 AND unit_price > 0
GROUP BY month
ORDER BY month;

-- Top countries by revenue
SELECT country, ROUND(SUM(net_revenue), 2) AS revenue, COUNT(DISTINCT customer_id) AS customers
FROM retail_orders
WHERE is_cancelled = 0 AND quantity > 0 AND unit_price > 0
GROUP BY country
ORDER BY revenue DESC
LIMIT 15;

-- Top products by revenue
SELECT description, ROUND(SUM(net_revenue), 2) AS revenue, SUM(quantity) AS units
FROM retail_orders
WHERE is_cancelled = 0 AND quantity > 0 AND unit_price > 0
GROUP BY description
ORDER BY revenue DESC
LIMIT 20;

-- Customer RFM-style ranking
WITH sales AS (
    SELECT customer_id, invoice_no, invoice_date, net_revenue
    FROM retail_orders
    WHERE customer_id IS NOT NULL AND is_cancelled = 0 AND quantity > 0 AND unit_price > 0
)
SELECT
    customer_id,
    CAST(julianday((SELECT MAX(invoice_date) FROM sales)) - julianday(MAX(invoice_date)) AS INTEGER) AS recency_days,
    COUNT(DISTINCT invoice_no) AS frequency,
    ROUND(SUM(net_revenue), 2) AS monetary_value
FROM sales
GROUP BY customer_id
ORDER BY monetary_value DESC
LIMIT 50;

-- Cancellation rate by country
SELECT
    country,
    COUNT(*) AS rows,
    SUM(CASE WHEN is_cancelled = 1 THEN 1 ELSE 0 END) AS cancellation_rows,
    ROUND(100.0 * SUM(CASE WHEN is_cancelled = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate
FROM retail_orders
GROUP BY country
HAVING rows >= 100
ORDER BY cancellation_rate DESC
LIMIT 20;

