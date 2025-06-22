from sqlalchemy import DateTime, BigInteger, func, String, Boolean, ForeignKey, Numeric, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    banned: Mapped[bool] = mapped_column(Boolean, default=False)

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # ссылка на родителя (NULL — если это родитель)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    parent: Mapped["Category | None"] = relationship(
        back_populates="children",
        remote_side=[id]
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    category: Mapped["Category"] = relationship(back_populates="products")

    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user: Mapped["TelegramUser"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("telegram_users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    delivery_address: Mapped[str] = mapped_column(Text)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_gateway: Mapped[str] = mapped_column(String(100))
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))

    user: Mapped["TelegramUser"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


class BroadcastMessage(Base):
    __tablename__ = "broadcast_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)


class FAQ(Base):
    __tablename__ = "faq"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(Text)

    """-- 
TRUNCATE categories RESTART IDENTITY CASCADE;
TRUNCATE products RESTART IDENTITY CASCADE;

DO $$
BEGIN
    FOR i IN 1..20 LOOP
        INSERT INTO categories (name, parent_id, created, updated)
        VALUES (format('Категория %s', i), NULL, NOW(), NOW());
    END LOOP;
END $$;

DO $$
DECLARE
    parent RECORD;
    j INT;
BEGIN
    FOR parent IN SELECT id FROM categories WHERE parent_id IS NULL LOOP
        FOR j IN 1..6 LOOP
            INSERT INTO categories (name, parent_id, created, updated)
            VALUES (format('Подкатегория %s.%s', parent.id, j), parent.id, NOW(), NOW());
        END LOOP;
    END LOOP;
END $$;

DO $$
DECLARE
    subcat RECORD;
    k INT;
BEGIN
    FOR subcat IN SELECT id FROM categories WHERE parent_id IS NOT NULL LOOP
        FOR k IN 1..6 LOOP
            INSERT INTO products (name, category_id, created, updated)
            VALUES (format('Продукт %s.%s', subcat.id, k), subcat.id, NOW(), NOW());
        END LOOP;
    END LOOP;
END $$;"""