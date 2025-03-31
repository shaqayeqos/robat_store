
import telebot 
import logging
from telebot import types
from telebot.types import ReplyKeyboardMarkup , ReplyKeyboardRemove , InlineKeyboardButton , InlineKeyboardMarkup
from texts import *
from DML import *
from DQL import *
from config import *

bot = telebot.TeleBot(API_TOKEN)
server = 'Local Server'
logging.basicConfig(filename='project.log', level=logging.INFO, format=f"%(asctime)s, %(levelname)s, {server} ,%(message)s",datefmt="%y/%m/%d %H:%M:%S ")
 


#user information
user_steps = dict()  # {cid: step, ...}
user_data = dict()   # {cid: {'first_name': ..., 'last_name': ..., 'address': ..., 'phone': ...}, ...}

#
user_steps_1 = {}

#command
admin_command = {
    'add_product'       :       add_product['add_product'],
    'sale_list'         :       add_product['sale_list']
}

#shuping cart
shaping_cart = dict()  #{cid:{code:qty, ...}, ...}

# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            print(f'{m.chat.first_name} [{str(m.chat.id)}]: {m.text}')
            logging.info(f'پیام از {m.chat.first_name} [{m.chat.id}]: {m.text}')
bot.set_update_listener(listener)  # register listener


# Handle 'start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    message_text = message.text
    logging.info(f'دستور شروع از کاربر {cid} دریافت شد: {message_text}')
    if len(message_text.split()) > 1:  
        _, code = message_text.split()  
        if code.startswith('buy'):  
            product_id = int(code.split('_')[-1])    
            product_info = get_product_info(product_id)
            if product_info is None:
                bot.send_message(cid, add_product['out_stock'])
                logging.warning(f'محصول {product_id} برای کاربر {cid} موجود نیست.')
                return
            if product_info['INVENTORY'] <= 0:  
                bot.send_message(cid, add_product['end'])
                logging.warning(f'محصول {product_id} دیگر در دسترس نیست برای کاربر {cid}.')
                return
            text, file_id, markup = gen_product_message(product_id, 1)
            bot.send_photo(cid, file_id, caption=text, reply_markup=markup)
            logging.info(f'محصول {product_id} به کاربر {cid} ارسال شد.')
            return
    bot.send_message(cid,words['start'], reply_to_message_id=message.message_id,reply_markup=ReplyKeyboardRemove())
    logging.info(f'پیام خوشامدگویی به کاربر {cid} ارسال شد.')
            
    

# Handle 'help'
@bot.message_handler(commands=['help'])
def send_help(message):
    cid = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(first_key['stor'],first_key['driver'])
    markup.add(first_key['support'])
    bot.send_message(cid,words['help'],reply_markup=markup)
    logging.info(f'کاربر {cid} درخواست کمک کرد و پیام کمک ارسال شد.')
    texts = ''


#admin
    if cid in admin:
        texts = 'admin command\n'
        for command,desc in admin_command.items():
            texts += f'/{command} : {desc}\n'
    if texts :
        bot.send_message(cid,texts)
        logging.info(f'کاربر ادمین {cid} لیست دستورات ادمین را درخواست کرد.')


#handle sale list   
@bot.message_handler(commands=['sale_list'])
def sale_list_handler(message):
    cid = message.chat.id
    if cid in admin: 
        sales_data = get_sales_data()  
        if sales_data:
            response_message = f"{add_product['sale_list']}\n"
            for sale in sales_data:
                response_message += f"{add_product['sale']}: {sale['ID']} _ {add_product['customor']}: {sale['CUSTOMER_ID']} _ {add_product['products']}: {sale['PRODUCT_ID']} _ {add_product['numbers']}: {sale['QUANTITY']}\n"
            bot.send_message(cid, response_message)
            logging.info(f'کاربر ادمین {cid} لیست فروش را دریافت کرد.')
        else:
            bot.send_message(cid, add_product['sales'])
            logging.warning(f'کاربر ادمین {cid} درخواست لیست فروش کرد، اما داده‌ای یافت نشد.')
    else:
        echo_message(message)
        logging.warning(f'کاربر {cid} سعی کرد به دستور فروش دسترسی پیدا کند، اما ادمین نیست.')


#handle add product
@bot.message_handler(commands=['add_product'])
def command_add_product_handler(message):
    cid = message.chat.id
    if cid in admin:
        message = f'{add_product["product"]}:\n{add_product["name"]}: {add_product["name_product"]}\n{add_product["price"]}: {add_product["price_p"]}\n{add_product["inventory"]}: {add_product["inventory_p"]}\n{add_product["description"]}: {add_product["description_p"]}'
        bot.send_message(cid, message, reply_markup=types.ReplyKeyboardRemove())
        user_steps[cid] = 'AP'
        logging.info(f'کاربر ادمین {cid} اطلاعات محصول جدید را درخواست کرد و پیام ارسال شد.')
    else:
        echo_message(message)
        logging.warning(f'کاربر {cid} سعی کرد به دستور افزودن محصول دسترسی پیدا کند، اما ادمین نیست.')
   
#hanle product    
@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == 'AP', content_types=['photo'])
def step_AP_handler(message):
    cid = message.chat.id
    try:
        file_id = message.photo[-1].file_id
        caption = message.caption
        if not caption:
            raise ValueError(add_product['error3'])        
        info_lines = caption.split('\n')
        if len(info_lines) < 4:
            raise ValueError(add_product['error1'])
        try:
            name = info_lines[0].split(':')[-1].strip()
            price = int(info_lines[1].split(':')[-1].strip())
            inventory = int(info_lines[2].split(':')[-1].strip())
            description = info_lines[3].split(':')[-1].strip()
        except ValueError as ve:
             bot.send_message(cid,shaping_cart['error4'])
             logging.error(f'کاربر {cid} در پردازش اطلاعات محصول خطا داشت: {ve}') 
             print(f"ValueError: {ve}")
             return

        product_id = insert_product_info( name, price, inventory, description, file_id)
        formatted_link = robat_link.format(product_id=product_id) 
        buy = add_product['buy']                                                                                              
        text = f"{add_product['name']}: {name}\n{add_product['price']}: {price}\n{add_product['description']}: {description}\n[{buy}]({formatted_link})"
        bot.send_photo(channl, file_id, caption=text,parse_mode='MarkdownV2') 
        bot.send_message(cid,f"{add_product['finally']}")
        logging.info(f'کاربر {cid} محصول جدید با نام {name} و قیمت {price} اضافه کرد.')
    except Exception as e:
                bot.send_message(cid,f"{add_product['error2']}")
                logging.error(f'کاربر {cid} در مرحله افزودن محصول خطا داشت: {e}')
                print(f"Error: {e}")  

#add product
def gen_product_message(code, qty):
    product_info = get_product_info(code)
    if product_info is None: 
        logging.warning(f'محصول با کد {code} یافت نشد.')
        return None, None, None
    text = f"{add_product['name']}: {product_info['NAME']}\n{add_product['description']}: {product_info['DESCRIPTION']}\n{add_product['price']}: {product_info['PRICE']}"
    file_id = product_info['FILE_ID']
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('➖', callback_data=f'change_{code}_{qty-1}'),
               InlineKeyboardButton(str(qty), callback_data='nothing'),
               InlineKeyboardButton('➕', callback_data=f'change_{code}_{qty+1}'))
    markup.add(InlineKeyboardButton(add_product['add_cart'], callback_data=f'add_{code}_{qty}'))
    markup.add(InlineKeyboardButton(add_product['cancel'], callback_data='cancel'))
    if qty == 0:
        markup = False
        logging.info(f'کاربر درخواست محصول {code} را با مقدار 0 ارسال کرد.')
    if qty > product_info['INVENTORY']:
        markup = 'not'
        logging.warning(f'کاربر درخواست محصول {code} را با مقدار {qty} ارسال کرد که بیشتر از موجودی است.')  
    logging.info(f'پیام محصول برای کد {code} با مقدار {qty} تولید شد.')
    return text, file_id, markup  

#handle InlineKeyboardMarkup
@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    call_id = call.id
    markup = InlineKeyboardMarkup()
    if data.startswith('change'):
        _, code, qty = data.split('_')
        text, file_id, markup  = gen_product_message(int(code), int(qty))
        if markup == 'not':
           bot.answer_callback_query(call_id,f"{add_product['not_inventory']}")
           logging.warning(f'کاربر {cid} سعی کرد محصول {code} را با مقدار {qty} درخواست کند، اما موجودی کافی نیست.')
        elif markup:
            bot.edit_message_caption(text, cid, mid)
            bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
            logging.info(f'کاربر {cid} اطلاعات محصول {code} را با مقدار {qty} به‌روزرسانی کرد.')
        else:
            bot.answer_callback_query(call_id,f"{add_product['zero']}")
            logging.info(f'کاربر {cid} درخواست محصول {code} را با مقدار 0 ارسال کرد.')

    elif data.startswith('add'):
        _, code, qty = data.split('_')
        code = int(code)
        qty = int(qty)
        try:  
            product = get_product_info(code)
            if product:
                inventory = product['INVENTORY']
                if inventory >= qty:  
                    shaping_cart.setdefault(cid, {})
                    shaping_cart[cid].setdefault(code, 0)
                    shaping_cart[cid][code] += qty
                    new_inventory = inventory - qty
                    update_product_inventory(code, new_inventory)
                    bot.answer_callback_query(call_id, f"{add_product['added']}")
                    bot.edit_message_reply_markup(cid, mid, reply_markup=None)
                    logging.info(f'کاربر {cid} محصول {code} را با مقدار {qty} به سبد خرید اضافه کرد.')
                else:
                    bot.answer_callback_query(call_id, add_product['out_of_stock'])
                    logging.warning(f'کاربر {cid} سعی کرد محصول {code} را با مقدار {qty} درخواست کند، اما موجودی کافی نیست.')
            else:
                bot.answer_callback_query(call_id,add_product['out_stock'] )
                logging.warning(f'محصول با کد {code} یافت نشد.')
        except Exception as e:
            bot.answer_callback_query(call_id, add_product['error9'])
            logging.error(f'کاربر {cid} در هنگام افزودن محصول {code} خطا داشت: {e}')  # ثبت خطا
            print(f"Error: {e}")

    elif data == 'nothing':
        bot.answer_callback_query(call_id, f"{add_product['nothing']}")
        logging.info(f'کاربر {cid} هیچ عملی انجام نداد.')

    elif data == 'cancel':
        bot.answer_callback_query(call_id, f"{add_product['canceled']}")
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        logging.info(f'کاربر {cid} عملیات را لغو کرد.')

    elif data.startswith('true_'):
        user_id = int(data.split('_')[1])  
        bot.send_message(user_id, add_product['true'])  
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)  
        bot.answer_callback_query(call.id, add_product['cid'])
        logging.info(f'کاربر {cid} تأیید کرد که کاربر {user_id} خرید را انجام داده است.')
    
        if user_id in shaping_cart:
            cart_items = shaping_cart[user_id]  
            for product_id, quantity in cart_items.items():
                sale_id = insert_sale_data(user_id, product_id, quantity)  
                if sale_id is not None:
                    insert_invoice_data(sale_id, product_id, quantity, user_id)
                    logging.info(f'فاکتور برای کاربر {user_id} با محصول {product_id} و مقدار {quantity} ایجاد شد.')
            customer_data = get_customer_data_by_chat_id(user_id) 
            invoice_data = get_invoice_data(user_id)
            invoice_message = display_invoice(customer_data, invoice_data)
            bot.send_message(user_id, invoice_message)
            logging.info(f'پیام فاکتور برای کاربر {user_id} ارسال شد.')  
        shaping_cart[user_id] = {}
        
    elif data.startswith('false_'):
        user_id = int(data.split('_')[1])
        bot.send_message(user_id, add_product['false'])  
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)  
        bot.answer_callback_query(call.id, add_product['cid'])
        logging.info(f'کاربر {user_id} خرید را لغو کرد.')

#invoice
def display_invoice(customer_data, invoice_data):
    if customer_data and invoice_data:
        if customer_data and invoice_data:
            invoice_message = f"{add_product['invoice']}\n"
            invoice_message += f"{words['full_name']} {customer_data['NAME']} {customer_data['LAST_NAME']}\n"  
            invoice_message += f"{words['address']} {customer_data['ADDRESS']}\n"
            invoice_message += f"{words['number']} {customer_data['PHONE']}\n\n"
            total_price = 0

        for item in invoice_data:
            product_name = item.get('product_name', add_product['uncertain' ])
            quantity = item.get('QUANTITY', 0)  
            price = item.get('price', 0) 
            total_price += price * quantity
            invoice_message += f"- {product_name}: {quantity} {add_product['number']}، {add_product['price']}: {price} {add_product['money']}\n"

        invoice_message += f"\n{add_product['plural']}: {total_price} {add_product['money']}\n"
        invoice_message += add_product['thanks']
        logging.info(f'فاکتور برای کاربر {customer_data["NAME"]} {customer_data["LAST_NAME"]} با مجموع {total_price} {add_product["money"]} ایجاد شد.')
        return invoice_message
    else:
        logging.warning('داده‌های مشتری یا فاکتور موجود نیستند.')
        return add_product['inv']

#hanle Drivers
@bot.message_handler(func=lambda message: message.text == first_key['driver'])
def handle_drivers(message):
    cid = message.chat.id
    bot.send_message(cid,words['drivers'],reply_to_message_id=message.message_id)
    logging.info(f'کاربر {cid} درخواست اطلاعات رانندگان را داشت.')

#hanle Support
@bot.message_handler(func=lambda message: message.text == first_key['support'])
def send_support(message):
    cid = message.chat.id
    bot.send_message(cid,words['support'], reply_to_message_id=message.message_id)
    logging.info(f'کاربر {cid} درخواست اطلاعات پشتیبانی را داشت.')

#handle Store
@bot.message_handler(func=lambda message: message.text == first_key['stor'])
def send_store(message):
    cid = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(store_key['product'],store_key['shopping_cart'])
    markup.add(store_key['user_account'])
    markup.add(store_key['back'])
    bot.send_message(cid,words['store'],reply_markup=markup)
    logging.info(f'کاربر {cid} وارد بخش فروشگاه شد.')

#handel product
@bot.message_handler(func=lambda message: message.text == store_key['product'])
def set_product(message):
    cid = message.chat.id
    link_text = words['shoping']  
    response_text = f"[__{link_text}__]({channl_link})"
    bot.send_message(cid, response_text , parse_mode='MarkdownV2')
    logging.info(f'کاربر {cid} درخواست اطلاعات محصول را داشت.')

#handle Back
@bot.message_handler(func=lambda message: message.text == store_key['back'])
def back_to_main(message):
        cid = message.chat.id
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(first_key['stor'],first_key['driver'])
        markup.add(first_key['support'])
        bot.send_message(cid,words['shupp_back'], reply_markup=markup)
        logging.info(f'کاربر {cid} به صفحه اصلی بازگشت.')

#SHOPING CART
#handle hopping cart show 
@bot.message_handler(func=lambda message: message.text == store_key['shopping_cart'])
def shopping_cart(message):
    cid = message.chat.id
    if cid not in shaping_cart or not shaping_cart[cid]:
        bot.send_message(cid, add_product['shoping_empty'])
        logging.info(f'کاربر {cid} سبد خرید خالی را مشاهده کرد.')
    else:
        cart_message = f"{add_product['u_shoping']}\n"
        total_price = 0
        for product_id, qty in shaping_cart[cid].items():
            product = get_product_info(product_id)  
            if product:
                cart_message += f"{product['NAME']} - {qty} {add_product['number']}- {product['PRICE']} {add_product['money']}\n"
                total_price += product['PRICE'] * qty
        cart_message += f"\n{add_product['plural']}: {total_price} {add_product['money']}"
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(store_key['payment']))
        markup.add(types.KeyboardButton(store_key['delet_product']))
        markup.add(types.KeyboardButton(store_key['back']))
        bot.send_message(cid,cart_message, reply_markup=markup)
        logging.info(f'کاربر {cid} سبد خرید را مشاهده کرد و مجموع قیمت: {total_price} {add_product["money"]} است.') 

#handle shopping cart show 
@bot.message_handler(func=lambda message: message.text == store_key['delet_product'])
def shopping_cart(message):
    cid = message.chat.id
    if cid not in shaping_cart or not shaping_cart[cid]:
        bot.send_message(cid, add_product['shoping_empty'])
        logging.info(f'کاربر {cid} سبد خرید خالی را مشاهده کرد.') 
    else:
        cart_message = f"{add_product['u_shoping']}\n"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product_id, qty in shaping_cart[cid].items():
            product = get_product_info(product_id)
            if product:
                cart_message += f"{product['NAME']} - {qty} {add_product['number']} (ID: {product_id})\n"
                keyboard.add(types.KeyboardButton(f"{add_product['delet']} {product['NAME']} (ID: {product_id})"))
                keyboard.add(types.KeyboardButton(store_key['back']))
                logging.info(f'کاربر {cid} محصول {product["NAME"]} (ID: {product_id}) را در سبد خرید مشاهده کرد.')
        cart_message += f"{add_product['delet_p']}\n"
        bot.send_message(cid, cart_message, reply_markup=keyboard)
        logging.info(f'کاربر {cid} سبد خرید را با محصولات زیر مشاهده کرد:\n{cart_message}')

#handle delet product 
@bot.message_handler(func=lambda message: message.text.startswith(add_product['delet']))
def remove_product_from_cart(message):
    cid = message.chat.id
    product_info = message.text.split(" (ID: ")
    product_name = product_info[0].replace(add_product['delet'], "")
    product_id = int(product_info[1].replace(")", ""))
    if cid in shaping_cart and product_id in shaping_cart[cid]:
        qty = shaping_cart[cid][product_id]  
        del shaping_cart[cid][product_id]  
        increase_inventory(product_id, qty)
        bot.send_message(cid, f"{add_product['delet_name']} '{product_name}' {product_id} {add_product['delet_2']}")
        logging.info(f'کاربر {cid} محصول {product_name} (ID: {product_id}) را از سبد خرید حذف کرد. مقدار حذف شده: {qty}')
    else:
        bot.send_message(cid, add_product['delet_1'])
        logging.warning(f'کاربر {cid} سعی کرد محصول (ID: {product_id}) را از سبد خرید حذف کند، اما این محصول در سبد خرید موجود نیست.')

#update inventory
def update_product_inventory(product_id, new_inventory):
    conn = mysql.connector.connect(**config) 
    cursor = conn.cursor()
    cursor.execute("UPDATE PRODUCT SET INVENTORY = %s WHERE ID = %s", (new_inventory, product_id))  
    conn.commit() 
    cursor.close()
    conn.close()

#decrease inventory
def decrease_inventory(product_id, quantity):
    product_info = get_product_info(product_id)
    if product_info and product_info['INVENTORY'] >= quantity:
        new_inventory = product_info['INVENTORY'] - quantity
        update_product_inventory(product_id, new_inventory)
        return True
    return False

#increase inventory
def increase_inventory(product_id, quantity):
    product_info = get_product_info(product_id)
    if product_info:
        new_inventory = product_info['INVENTORY'] + quantity
        update_product_inventory(product_id, new_inventory)
        return True
    return False


#handle payment 
@bot.message_handler(func=lambda message: message.text == store_key['payment'])
def set_user_info(message):
    cid = message.chat.id
    customer_data = get_customer_data_by_chat_id(cid)
    total_price = calculate_total_price(cid)
    if not customer_data:
        bot.send_message(cid, add_product['users'])
        logging.warning(f'کاربر {cid} اطلاعات کاربری ندارد و پیام مربوط به اطلاعات کاربری ارسال شد.')
    else:
        if total_price > 0:
            bot.send_message(cid, f"{add_product['bank_card']}\n1234-5678-9012-3456\n{total_price} {add_product['money']}")
            user_steps_1[cid] = 'AM'
            logging.info(f'کاربر {cid} اطلاعات پرداخت را دریافت کرد. مجموع مبلغ: {total_price} {add_product["money"]}.')  
        else:
            bot.send_message(cid, add_product['shoping_empty'])
            logging.info(f'کاربر {cid} سبد خرید خالی دارد و پیام مربوط به سبد خرید خالی ارسال شد.')

              
#hanle product calcuation 
def calculate_total_price(cid):
    total_price = 0
    if cid in shaping_cart:
        for product_id, qty in shaping_cart[cid].items():
            product = get_product_info(product_id)
            if product:
                total_price += product['PRICE'] * qty
    logging.info(f'کاربر {cid} مجموع قیمت سبد خرید را محاسبه کرد: {total_price} {add_product["money"]}.')
    return total_price 

@bot.message_handler(func=lambda message: user_steps_1.get(message.chat.id) == 'AM',content_types=['photo'])
def handle_payment_receipt(message):
    cid = message.chat.id
    total_price = calculate_total_price(cid)   
    caption = f"{add_product['captions_1']}\n{total_price} {add_product['money']}"
    admins = admin 
    markup = types.InlineKeyboardMarkup()   
    markup.add(types.InlineKeyboardButton(text=add_product['true'], callback_data=f"true_{cid}"))
    markup.add(types.InlineKeyboardButton(text=add_product['false'], callback_data=f"false_{cid}")) 
    bot.send_photo(admins, message.photo[-1].file_id, caption=caption, reply_markup=markup)
    bot.send_message(cid, add_product['check'])
    logging.info(f'کاربر {cid} رسید پرداخت را ارسال کرد. مجموع مبلغ: {total_price} {add_product["money"]}.')       
# clear    
    user_steps_1[cid] = None


#CUSTOMER
#handle user info (name)
@bot.message_handler(func=lambda message: message.text == store_key['user_account'])
def set_user_info(message):
    cid = message.chat.id
    customer_data = get_customer_data_by_chat_id(cid)
    if customer_data:
        full_name = f"{customer_data['NAME']} {customer_data['LAST_NAME']}"
        message_text = f"{words['inf']}\n{words['full_name']} {full_name}\n{words['address']} {customer_data['ADDRESS']}\n{words['number']} {customer_data['PHONE']}"
        bot.send_message(cid, message_text)
        logging.info(f'کاربر {cid} اطلاعات کاربری خود را مشاهده کرد: {message_text}')
    else:
        bot.send_message(cid,words['first_name'])
        logging.warning(f'کاربر {cid} اطلاعات کاربری ندارد و پیام مربوط به نام اول ارسال شد.')
    user_steps[cid] = 'A'


#handle (last name)
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'A')
def step_A_handler(message):
    cid = message.chat.id
    first_name = message.text
    try:
        if first_name.isdigit(): 
            raise ValueError(words['error5'])
        user_data[cid] = {'first_name': first_name}
        bot.send_message(cid,words['last_name'])
        user_steps[cid] = 'B'
        logging.info(f'کاربر {cid} نام اول خود را ثبت کرد: {first_name}')
    except ValueError as ve:
        bot.send_message(cid, str(ve))
        print(f"Error: {ve}")
        logging.error(f'کاربر {cid} در ثبت نام اول خطا داشت: {ve}')
        
#handler (addres)
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'B')
def step_B_handler(message):
    cid = message.chat.id
    last_name = message.text
    try:
        if last_name.isdigit():  
            raise ValueError(words['error6'])
        user_data[cid]['last_name'] = last_name
        bot.send_message(cid, words['address_'])
        user_steps[cid] = 'C'
        logging.info(f'کاربر {cid} نام خانوادگی خود را ثبت کرد: {last_name}') 
    except ValueError as ve:
        bot.send_message(cid, str(ve))
        print(f"Error: {ve}")
        logging.error(f'کاربر {cid} در ثبت نام خانوادگی خطا داشت: {ve}')

#handler (phone number)
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'C')
def step_C_handler(message):
    cid = message.chat.id
    address = message.text
    user_data[cid]['address'] = address
    bot.send_message(cid,words['phone_number'])
    user_steps[cid] = 'D'
    logging.info(f'کاربر {cid} آدرس خود را ثبت کرد: {address}')

#handler show inf
@bot.message_handler(func=lambda message: user_steps.get(message.chat.id) == 'D')
def step_D_handler(message):
    cid = message.chat.id
    phone = message.text
    try:
        if not phone.isdigit() or len(phone) != 11: 
            raise ValueError(words['error7'])

        user_data[cid]['phone'] = phone

        user_id = insert_customer_data(
            user_data[cid]['first_name'],
            user_data[cid]['last_name'],
            phone,
            user_data[cid]['address'],
            cid
        )
        
        if user_id is not None:
            full_name = f"{user_data[cid]['first_name']} {user_data[cid]['last_name']}"
            message = f"{words['inf']}\n{words['full_name']} {full_name}\n{words['address']} {user_data[cid]['address']}\n{words['number']} {user_data[cid]['phone']}"
            bot.send_message(cid, message)
            logging.info(f'کاربر {cid} اطلاعات خود را ثبت کرد: {message}')
        else:
            bot.send_message(cid,words['error'])
            logging.error(f'کاربر {cid} در ثبت اطلاعات با خطا مواجه شد.')
    except ValueError as ve:
        bot.send_message(cid, str(ve))  
        bot.send_message(cid, words['phone_number'])
        print(f"Error: {ve}")
        logging.warning(f'کاربر {cid} در وارد کردن شماره تلفن خطا داشت: {ve}')
    except Exception as e:
        bot.send_message(cid, words['error'])
        print(f"Error: {e}")
        logging.error(f'کاربر {cid} در پردازش اطلاعات با خطا مواجه شد: {e}') 
        
# clear inf
def clear_user_data(cid):
    user_data.pop(cid, None)
    user_steps.pop(cid, None)
    logging.info(f'اطلاعات کاربر {cid} پاک شد.')

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, add_product['new_text'])
    logging.info(f'کاربر {message.chat.id} ورودی ناشناخته ارسال کرد: {message.text}') 



bot.infinity_polling(skip_pending=True)



