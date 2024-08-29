import sqlite3
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from config import dp, bot, admin
from fsm import ProductForm, OrderForm
# Все fsm в другом фале
# Создание и настройка базы данных SQLite
# Таблица для добавленных продуктов
def init_db():
    conn = sqlite3.connect('products_orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT,
            price REAL,
            sku TEXT UNIQUE,
            photo_id TEXT
        )
    ''')
# Таблица для заказанных продуктов клиентом
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL,
            size TEXT,
            quantity INTEGER,
            contact_info TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Вызов функции для создания базы данных и таблиц
init_db()

# Это все обработчики событий для добавления товара /add_product команда для добавления продукта

@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я ваш новый бот.")

@dp.message_handler(commands='info')
async def send_info(message: types.Message):
    await message.reply("Я бот, созданный для управления продуктами и заказами.")

@dp.message_handler(commands='add_product', state='*')
async def add_product(message: types.Message):
    await ProductForm.name.set()
    await message.reply("Введите название продукта:")

@dp.message_handler(state=ProductForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await ProductForm.next()
    await message.reply("Введите категорию продукта:")

@dp.message_handler(state=ProductForm.category)
async def process_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text
    await ProductForm.next()
    await message.reply("Введите размер продукта:")

@dp.message_handler(state=ProductForm.size)
async def process_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text
    await ProductForm.next()
    await message.reply("Введите цену продукта:")

@dp.message_handler(state=ProductForm.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await ProductForm.next()
    await message.reply("Введите артикул продукта:")

@dp.message_handler(state=ProductForm.sku)
async def process_sku(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sku'] = message.text
    await ProductForm.next()
    await message.reply("Загрузите фотографию продукта:")

# Здесь все через fsm уже идет в таблицу для добавления товаров

@dp.message_handler(state=ProductForm.photo, content_types=['photo'])
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
        conn = sqlite3.connect('products_orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, category, size, price, sku, photo_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['category'], data['size'], data['price'], data['sku'], data['photo']))
        conn.commit()
        conn.close()
        await message.reply("Продукт успешно добавлен!")
    await state.finish()
# Здесь начинаются обработчики событий для заказа клиента /order команда для вызова в тг
@dp.message_handler(commands='order', state='*')
async def start_order(message: types.Message):
    await OrderForm.sku.set()
    await message.reply("Введите артикул товара, который хотите купить:")

@dp.message_handler(state=OrderForm.sku)
async def process_order_sku(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sku'] = message.text
    await OrderForm.next()
    await message.reply("Введите размер товара:")

@dp.message_handler(state=OrderForm.size)
async def process_order_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text
    await OrderForm.next()
    await message.reply("Введите количество товара:")

@dp.message_handler(state=OrderForm.quantity)
async def process_order_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity'] = message.text
    await OrderForm.next()
    await message.reply("Введите контактные данные (номер телефона):")

# Здесь все через fsm уже идет в таблицу для закзов клиентов

@dp.message_handler(state=OrderForm.contact_info)
async def process_order_contact_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact_info'] = message.text
        conn = sqlite3.connect('products_orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (sku, size, quantity, contact_info)
            VALUES (?, ?, ?, ?)
        ''', (data['sku'], data['size'], data['quantity'], data['contact_info']))
        conn.commit()
        conn.close()
        for admin_id in admin:
            await bot.send_message(admin_id,
                                   f"Новый заказ:\nАртикул: {data['sku']}\nРазмер: {data['size']}\nКоличество: {data['quantity']}\nКонтактные данные: {data['contact_info']}")
    await state.finish()
    await message.reply("Ваш заказ успешно оформлен!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
