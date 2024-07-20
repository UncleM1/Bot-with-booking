from sqlalchemy import Text, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    time_created:Mapped[DateTime] = mapped_column(DateTime,default=func.now(), )
    time_updated:Mapped[DateTime] = mapped_column(DateTime,default=func.now(), onupdate=func.now() )

class Product(Base):
    __tablename__ = "product"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(String(150),nullable=False)
    description:Mapped[str] = mapped_column(Text)
    price:Mapped[float] = mapped_column(Float(asdecimal=True),nullable=False)
    image: Mapped[float] = mapped_column(String(150),nullable=True)


class Master(Base):
    __tablename__ = "master"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(150),nullable=False)
    description: Mapped[str] = mapped_column(Text)
    image: Mapped[float] = mapped_column(String(150),nullable=True)

class Customer(Base):
    __tablename__ = "customer"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id:Mapped[int] = mapped_column(nullable=False)
    first_name:Mapped[str] = mapped_column(String(15),nullable=False)
    phone_number:Mapped[str] = mapped_column(String(20),nullable=True)
    master_to_order:Mapped[str] = mapped_column(ForeignKey("master.id",ondelete="SET NULL"),nullable=True)
    product_to_order:Mapped[str] = mapped_column(ForeignKey("product.id",ondelete="SET NULL"),nullable=True)
    day_to_order:Mapped[str] = mapped_column(String(10),nullable=True)
    month_to_order: Mapped[str] = mapped_column(String(10), nullable=True)



