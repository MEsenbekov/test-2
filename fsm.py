from aiogram.dispatcher.filters.state import State, StatesGroup

# Добавление продуктов
class ProductForm(StatesGroup):
    name = State()
    category = State()
    size = State()
    price = State()
    sku = State()
    photo = State()

# Заказы клиентов
class OrderForm(StatesGroup):
    sku = State()
    size = State()
    quantity = State()
    contact_info = State()
