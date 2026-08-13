Create database ecommercetest;

Use ecommercetest;


Create table customer 
(customer_id varchar(6) primary key, 
f_name varchar(20), 
l_name varchar(20), 
phone_number varchar(13), 
email varchar(100) not null);

Alter table customer add CONSTRAINT uq_customer_email UNIQUE (email);

Create table customer_credentials
(customer_id varchar(6) primary key, 
password_hash varchar(50) not null, 
foreign key (customer_id) references customer(customer_id) ON DELETE CASCADE);

Create table vendor 
(vendor_id varchar(6) primary key, 
vendor_name varchar(50) not null,
email varchar(100) not null,  
phone_number varchar(13));

Alter table vendor add CONSTRAINT uq_vendor_email UNIQUE (email);

Create table vendor_credentials
(vendor_id varchar(6) primary key, 
password_hash varchar(50) not null, 
foreign key (vendor_id) references vendor(vendor_id) ON DELETE CASCADE);

Create table product
(product_id varchar(6) primary key, 
vendor_id varchar(6) not null, 
product_name varchar(50) not null, 
description varchar(200), 
price decimal(10,2) not null, 
stock_quantity int(100) not null, 
product_type varchar(10) not null,  
foreign key (vendor_id) references vendor(vendor_id));

Alter table product ADD constraint chk_product_type CHECK (product_type in ('beauty', 'fashion'));

Alter table product ADD constraint chk_price CHECK (price >=0);

Alter table product ADD CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0);

#new additions

Alter table product Add column image_url varchar(2048);

Create table review
(review_id varchar(6) primary key, 
product_id varchar(6),
customer_id varchar(6) not null, 
rating int(1) not null, 
review_date date not null,  
foreign key (product_id) references product(product_id) ON DELETE SET NULL, 
foreign key (customer_id) references customer(customer_id) ON DELETE CASCADE);

Alter table review ADD CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5);

alter table review add comment text(100000);

create table cart
(cart_id varchar(6)  primary key, 
customer_id  varchar(6) not null,  
foreign key (customer_id) references customer(customer_id) ON DELETE CASCADE );

create table cart_items 
( product_id varchar(6)  not null, 
cart_id varchar(6)  not null, 
quantity int(10) not null, 
added_date date not null, 
primary key (product_id, cart_id), 
foreign key (cart_id) references cart(cart_id) ON DELETE CASCADE,
foreign key (product_id) references product(product_id) );

Alter table cart_items ADD CONSTRAINT chk_cart_quantity CHECK (quantity > 0);


create table orders 
( order_id varchar(6)  primary key, 
customer_id varchar(6)  not null, 
cart_id varchar(6)  not null, 
order_date datetime not null, 
subtotal decimal(10,2) not null, 
shipping_fee decimal(10,2) not null, 
foreign key (cart_id) references cart(cart_id),
foreign key (customer_id) references customer(customer_id) ); 


Alter table orders ADD CONSTRAINT chk_order_subtotal CHECK (subtotal >= 0.00);
Alter table orders ADD CONSTRAINT chk_order_shipping CHECK (shipping_fee >= 0.00);

create table payment 
( payment_id  varchar(6) primary key, 
customer_id  varchar(6) not null, 
amount decimal(10,2) not null, 
payment_date date not null, 
payment_type varchar(50) not null,
 order_id  varchar(6) not null, 
foreign key (order_id) references orders(order_id),
foreign key (customer_id) references customer(customer_id));

Alter table payment ADD constraint chk_product_type CHECK (payment_type in ('card','bank transfer', 'mobile money'));

Alter table payment ADD CONSTRAINT chk_payment_amount CHECK (amount >= 0.00);


create table address 
( address_id varchar(6) primary key, 
city varchar(100) not null, 
Landmark varchar(100),
street_address varchar(255) not null, 
customer_id varchar(6) not null , 
foreign key (customer_id) references customer(customer_id) ON DELETE CASCADE);


create table shipping_company 
( shipping_id varchar(6) primary key, 
name varchar(150) not null, 
contact_phone varchar(30) ); 

create table delivery 
( delivery_id varchar(6)  primary key, 
order_id varchar(6)  not null, 
delivery_status varchar(50) not null, 
estimated_delivery_date date, 
 address_id varchar(6), 
shipping_id varchar(6), 
foreign key (order_id) references orders (order_id), 
foreign key (address_id) references address(address_id) ON DELETE SET NULL, 
foreign key (shipping_id)references shipping_company(shipping_id) );

Alter table delivery ADD CONSTRAINT chk_delivery_status  CHECK (delivery_status in ('delivered', 'sent to port', 'on the way'));


Create table bank_transfer(
payment_id varchar(6) primary key, 
bank_name varchar(60) not null, 
account_number varchar(30) not null, 
account_name varchar(100) not null , 
foreign key (payment_id) references payment(payment_id));

Create table mobile_money
(payment_id varchar(6) primary key, 
network varchar(60) not null, 
phone_number varchar(13) not null, 
account_name varchar(100) not null , 
foreign key (payment_id) references payment(payment_id));

Create table card
(payment_id varchar(6) primary key, 
token_id varchar(3) not null, 
card_num varchar(15) not null, 
card_name varchar(100) not null ,
Expiry_date date not null, 
foreign key (payment_id) references payment(payment_id));


Create table fashion
( product_id varchar(6) primary key,
Color varchar(40),
Material varchar(100),
Size varchar(5),
Gender_category varchar(15),
foreign key (product_id) references product(product_id) ON DELETE CASCADE);

Alter table fashion ADD CONSTRAINT chk_fashion_gender CHECK (gender_category IN ('men', 'women', 'unisex', 'kids'));

Create table beauty
( product_id varchar(6) primary key,
skin_type varchar(40),
volume_weight varchar(100),
Is_organic boolean,
foreign key (product_id) references product(product_id) ON DELETE CASCADE);


create table order_items 
( product_id varchar(6)  not null, 
order_id varchar(6)  not null, 
quantity int(10) not null, 
added_date date not null, 
primary key (product_id, order_id), 
foreign key (order_id) references orders(order_id) ON DELETE CASCADE,
foreign key (product_id) references product(product_id) );

Alter table order_items ADD CONSTRAINT chk_orderitems_quantity CHECK (quantity > 0);

 
