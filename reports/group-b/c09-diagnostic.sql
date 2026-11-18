-- Reference SQL from reference-td1.csv
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON p.product_id = o.product_id JOIN customers c ON c.customer_id = o.customer_id WHERE c.birth_date <= date('2026-09-26', '-25 years') AND c.birth_date >  date('2026-09-26', '-26 years');

-- Stored faulty SQL: cohere/north-mini-code:free
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) +
    -- Adjust if birthday hasn't occurred yet this year
    CASE
      WHEN SUBSTR(c.birth_date, 6, 2) > '09' THEN -1
      WHEN SUBSTR(c.birth_date, 6, 2) = '09' AND SUBSTR(c.birth_date, 9, 2) > '26' THEN -1
      ELSE 0
    END
  ) = 25;

-- Stored faulty SQL: dots-studio/dots-3-note-preview:free
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE 
    (c.birth_date IS NOT NULL)
    AND (
        CAST(strftime('%Y', '2026-09-26') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) < 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) <= 26)
        )
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) > 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) > 26)
        )
    );

-- Independent completed-age calculation
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE ((2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER)) - ('09-26' < strftime('%m-%d', c.birth_date))) = 25
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;

-- Exact omitted rows: cohere/north-mini-code:free
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE ((2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER)) - ('09-26' < strftime('%m-%d', c.birth_date))) = 25
AND NOT (-- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) +
    -- Adjust if birthday hasn't occurred yet this year
    CASE
      WHEN SUBSTR(c.birth_date, 6, 2) > '09' THEN -1
      WHEN SUBSTR(c.birth_date, 6, 2) = '09' AND SUBSTR(c.birth_date, 9, 2) > '26' THEN -1
      ELSE 0
    END
  ) = 25)
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;

-- Exact omitted rows: dots-studio/dots-3-note-preview:free
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE ((2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER)) - ('09-26' < strftime('%m-%d', c.birth_date))) = 25
AND NOT ((c.birth_date IS NOT NULL)
    AND (
        CAST(strftime('%Y', '2026-09-26') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) < 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) <= 26)
        )
        AND (
            CAST(strftime('%m', c.birth_date) AS INTEGER) > 9
            OR (CAST(strftime('%m', c.birth_date) AS INTEGER) = 9 AND CAST(strftime('%d', c.birth_date) AS INTEGER) > 26)
        )
    ))
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;
