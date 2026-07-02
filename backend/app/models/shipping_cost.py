from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShippingCost(Base):
    __tablename__ = "shipping_costs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    warehouse_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
