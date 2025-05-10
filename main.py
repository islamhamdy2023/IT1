from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser

# بيانات المنتجات
products_data = [
    {'title': 'A4', 'price': 150, 'image': 'assets/a4.jpg'},
    {'title': 'A3', 'price': 200, 'image': 'assets/a3.jpg'},
]

SHIPPING_COST = 30
class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.7, 0.9, 1, 1)  # Light blue background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        title_label = Label(text="About the App", font_size=28, bold=True, color=(0, 0, 0, 1))
        description_label = Label(
            text="This app is designed for selling stationery products online.\n"
                 "It offers an easy way to browse and order products.",
            font_size=20, color=(0, 0, 0, 1)
        )
        notes_label = Label(
            text="Note: If you want to add more than one product please enter back before checkout.",
            font_size=18, color=(0, 0, 0, 1)
        )

        layout.add_widget(title_label)
        layout.add_widget(description_label)
        layout.add_widget(notes_label)

        back_button = Button(text="Back", size_hint=(None, None), size=(200, 50),
                             pos_hint={'center_x': 0.5}, background_color=(0.2, 0.6, 1, 1))
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_back(self, instance):
        self.manager.current = 'product_list'  # Go back to the main screen



# شاشة تفاصيل المنتج
class ProductDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product = None

        self.layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.layout.canvas.before.clear()

        self.image = Image(size_hint=(1, 0.4))
        self.title = Label(font_size=24, color=(0, 0, 0, 1))
        self.price = Label(font_size=20, color=(0.1, 0.1, 0.1, 1))
        self.quantity_input = TextInput(hint_text='Quantity', multiline=False, input_filter='int', size_hint_y=None, height=40)
        self.total_label = Label(font_size=18, color=(0, 0, 0, 1))

        self.add_to_cart_btn = Button(text='Add to Cart', size_hint=(1, 0.15), background_color=(0.2, 0.6, 0.8, 1))
        self.add_to_cart_btn.bind(on_press=self.add_to_cart)

        self.back_btn = Button(text='Back', size_hint=(1, 0.1), background_color=(0.8, 0.1, 0.1, 1))
        self.back_btn.bind(on_press=self.go_back)

        self.quantity_input.bind(text=self.update_total)

        self.layout.add_widget(self.image)
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.price)
        self.layout.add_widget(self.quantity_input)
        self.layout.add_widget(self.total_label)
        self.layout.add_widget(self.add_to_cart_btn)
        self.layout.add_widget(self.back_btn)
        with self.canvas.before:
            Color(0.7, 0.9, 1, 1)  # اللون اللبني
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(self.layout)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
        

    def set_product(self, product):
        self.product = product
        self.image.source = product['image']
        self.title.text = product['title']
        self.price.text = f"{product['price']} EGP"
        self.quantity_input.text = "1"
        self.update_total()

    def update_total(self, *args):
        try:
            quantity = int(self.quantity_input.text)
        except:
            quantity = 0
        total = quantity * self.product['price'] + SHIPPING_COST
        self.total_label.text = f"Total: {total} EGP (including {SHIPPING_COST} shipping)"

    def add_to_cart(self, instance):
        app = App.get_running_app()
        cart_screen = app.root.get_screen('cart')
        cart_screen.add_to_cart(self.product, self.quantity_input.text)
        app.root.current = 'cart'

    def go_back(self, instance):
        App.get_running_app().root.current = 'product_list'


# شاشة سلة المشتريات
class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []

        layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.cart_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.cart_list)

        self.total_label = Label(font_size=18, color=(0, 0, 0, 1))

        self.checkout_btn = Button(text='Checkout', size_hint=(1, 0.1), background_color=(0.2, 0.6, 0.8, 1))
        self.checkout_btn.bind(on_press=self.checkout)

        self.back_btn = Button(text='Back', size_hint=(1, 0.1), background_color=(0.8, 0.1, 0.1, 1))
        self.back_btn.bind(on_press=self.go_back)

        layout.add_widget(scroll)
        layout.add_widget(self.total_label)
        layout.add_widget(self.checkout_btn)
        layout.add_widget(self.back_btn)
        with self.canvas.before:
            Color(0.7, 0.9, 1, 1)  # اللون اللبني
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(layout)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        

    def add_to_cart(self, product, quantity):
        item = {'product': product, 'quantity': int(quantity)}
        self.cart_items.append(item)
        self.update_cart()

    def update_cart(self):
        self.cart_list.clear_widgets()
        total = 0
        for item in self.cart_items:
            product = item['product']
            quantity = item['quantity']
            total += product['price'] * quantity
            cart_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            cart_item.add_widget(Label(text=product['title'], color=(0, 0, 0, 1)))
            cart_item.add_widget(Label(text=f"x{quantity}", color=(0, 0, 0, 1)))
            cart_item.add_widget(Label(text=f"{product['price'] * quantity} EGP", color=(0, 0, 0, 1)))
            self.cart_list.add_widget(cart_item)
        self.total_label.text = f"Total: {total + SHIPPING_COST} EGP (including shipping)"

    def checkout(self, instance):
        app = App.get_running_app()
        order_screen = app.root.get_screen('order_form')
        order_screen.set_cart(self.cart_items)
        app.root.current = 'order_form'

    def go_back(self, instance):
        App.get_running_app().root.current = 'product_list'


# شاشة الطلب
class OrderFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []

        layout = BoxLayout(orientation='vertical', spacing=5, padding=5)

        self.name_input = TextInput(hint_text='Full Name', multiline=False, size_hint_y=None, height=40)
        self.email_input = TextInput(hint_text='Email', multiline=False, size_hint_y=None, height=40)
        self.phone_input = TextInput(hint_text='Phone Number', multiline=False, size_hint_y=None, height=40)
        self.address_input = TextInput(hint_text='Address', multiline=False, size_hint_y=None, height=40)

        self.submit_btn = Button(text='Submit Order', background_color=(0.2, 0.6, 0.8, 1), size_hint_y=None, height=45)
        self.submit_btn.bind(on_press=self.submit_order)

        self.back_btn = Button(text='Back', background_color=(0.8, 0.1, 0.1, 1), size_hint_y=None, height=45)
        self.back_btn.bind(on_press=self.go_back)
        self.order_details_label = Label(font_size=18, color=(0, 0, 0, 1))

        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.address_input)
        layout.add_widget(self.order_details_label)
        layout.add_widget(self.submit_btn)
        layout.add_widget(self.back_btn)
        with self.canvas.before:
            Color(0.7, 0.9, 1, 1)  # اللون اللبني
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(layout)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        

    def set_cart(self, cart_items):
        self.cart_items = cart_items
        details_text = "Items Ordered:\n"
        for item in self.cart_items:
            product = item['product']
            quantity = item['quantity']
            details_text += f"{product['title']} x {quantity} \n"
        self.order_details_label.text = details_text

    def submit_order(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        phone = self.phone_input.text
        address = self.address_input.text

        if not all([name, email, phone, address]):
            self.show_popup("Error", "All fields are required.")
            return

        total = sum([item['product']['price'] * item['quantity'] for item in self.cart_items]) + SHIPPING_COST
        summary = f"Order Success!\nName: {name}\nPhone: {phone}\nAddress: {address}\nTotal: {total} EGP"

        self.send_email(name, email, phone, address, total)
        self.send_whatsapp(name, phone, address, total)

        self.cart_items.clear()

        self.show_popup("Success", summary)
        App.get_running_app().root.get_screen('cart').cart_items.clear()
        App.get_running_app().root.current = 'product_list'

    def send_email(self, name, email, phone, address, total):
        msg = MIMEMultipart()
        msg['From'] = 'your_email@gmail.com'
        msg['To'] = 'islamhamdy489@gmail.com'
        msg['Subject'] = 'New Order Received'

        body = f"New order received:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\nTotal: {total} EGP"
        msg.attach(MIMEText(body, 'plain'))
        # البريد الالكتروني هنا مش شغال بدون بيانات حقيقية
        pass

    def send_whatsapp(self, name, phone, address, total):
        message = f"New order received:\nName: {name}\nPhone: {phone}\nAddress: {address}\nTotal: {total} EGP"
        webbrowser.open(f"https://wa.me/201223722670?text={message}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def go_back(self, instance):
        App.get_running_app().root.current = 'cart'


# شاشة عرض المنتجات
class ProductListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical')
        content_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        header = Image(source='assets/background.jpg', size_hint=(1, 0.3))
        content_layout.add_widget(header)

        for product in products_data:
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=160, padding=5, spacing=5)
            image = Image(source=product['image'], size_hint=(0.35, 1))
            info = BoxLayout(orientation='vertical', spacing=3)
            title = Label(text=product['title'], font_size=20, color=(0, 0, 0, 1))
            price = Label(text=f"{product['price']} EGP", font_size=16, color=(0.1, 0.1, 0.1, 1))
            btn_detail = Button(text='Add to Cart', size_hint=(1, 0.4), background_color=(0.2, 0.6, 0.8, 1))
            btn_detail.bind(on_press=lambda x, p=product: self.go_to_detail(p))
            info.add_widget(title)
            info.add_widget(price)
            info.add_widget(btn_detail)
            item.add_widget(image)
            item.add_widget(info)
            content_layout.add_widget(item)

        main_layout.add_widget(content_layout)
        with self.canvas.before:
            Color(0.7, 0.9, 1, 1)  # اللون اللبني
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        float_layout = FloatLayout()
        float_layout.add_widget(main_layout)
        info_button = Button(text='About App',
                             size_hint=(None, None),
                             size=(120, 40),
                             pos_hint={'right': 0.98, 'top': 0.98},
                             background_color=(1, 1, 1, 1),  # خلفية بيضاء
                             color=(0, 0, 0, 1))  # لون الخط اسود
        info_button.bind(on_release=self.go_to_about)
        float_layout.add_widget(info_button)

        self.add_widget(float_layout)
        
    def go_to_about(self, instance):
        self.manager.current = 'about'
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    def go_to_about(self, instance):
        self.manager.current = 'about'
        

    def go_to_detail(self, product):
        app = App.get_running_app()
        detail_screen = app.root.get_screen('product_detail')
        detail_screen.set_product(product)
        app.root.current = 'product_detail'


# التطبيق الرئيسي
class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ProductListScreen(name='product_list'))
        sm.add_widget(ProductDetailScreen(name='product_detail'))
        sm.add_widget(CartScreen(name='cart'))
        sm.add_widget(OrderFormScreen(name='order_form'))
        sm.add_widget(AboutScreen(name='about'))  # ضيف شاشة About هنا
        return sm

if __name__ == '__main__':
    MainApp().run()
