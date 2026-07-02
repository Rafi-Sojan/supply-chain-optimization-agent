# Real Dataset Folder

Put your real CSV files here using these exact filenames:

- `products.csv`
- `suppliers.csv`
- `warehouses.csv`
- `customers.csv`
- `inventory.csv`
- `demand_history.csv`
- `shipping_costs.csv`

When any real CSV exists in this folder, the backend switches from sample data
to real data mode and expects all seven files to be present.

## Required Columns

`products.csv`

```csv
product_id,product_name,category,unit_price
```

`suppliers.csv`

```csv
supplier_id,supplier_name,product_id,unit_cost,lead_time_days,reliability_score,capacity,quality_score,past_delay_rate
```

`warehouses.csv`

```csv
warehouse_id,warehouse_name,region,storage_capacity
```

`customers.csv`

```csv
customer_id,customer_name,region
```

`inventory.csv`

```csv
warehouse_id,product_id,on_hand,reserved
```

`demand_history.csv`

```csv
product_id,region,period,demand
```

`shipping_costs.csv`

```csv
warehouse_id,customer_id,product_id,shipping_cost,distance_km,delivery_time_days
```

## Validation Rules

- IDs must match across files.
- `demand_history.region` must exist in `customers.region`.
- Numeric columns must be numeric and non-negative.
- `period` should use `YYYY-MM-DD` format.
- Shipping costs should include enough warehouse-customer-product lanes for the optimizer to satisfy demand.
