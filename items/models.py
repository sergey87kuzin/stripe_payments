import os
import logging

import stripe
from django.db import models
from django.core.validators import MaxValueValidator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('django')
stripe.api_key = os.getenv('API_KEY')

CURRENCIES = (('usd', 'usd'), ('eur', 'eur'), ('chf', 'chf'))


class Item(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=30
    )
    description = models.TextField(verbose_name='Описание')
    price_in_usd = models.DecimalField(
        verbose_name='Цена в долларах',
        max_digits=10,
        decimal_places=2
    )
    price_in_eur = models.DecimalField(
        verbose_name='Цена в евро',
        max_digits=10,
        decimal_places=2
    )
    price_in_chf = models.DecimalField(
        verbose_name='Цена во франках',
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        verbose_name='Валюта',
        choices=CURRENCIES,
        max_length=3
    )
    taxes = models.ManyToManyField(
        'Tax',
        related_name='tax_items',
        verbose_name='налоги'
    )
    discount = models.ForeignKey(
        'Discount',
        related_name='discount_items',
        verbose_name='скидки',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    stripes_id = models.CharField(
        verbose_name='идентификатор на сервере',
        max_length=40,
        blank=True
    )
    price_id = models.CharField(
        verbose_name='идентификатор цены на сервере',
        max_length=40,
        blank=True
    )

    class Meta():
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        CURR_PRICE = {
            'usd': self.price_in_usd * 100,
            'eur': self.price_in_eur * 100,
            'chf': self.price_in_chf * 100
        }
        unit_amount = int(CURR_PRICE[self.currency])
        del CURR_PRICE[self.currency]
        options = {
            key: {'unit_amount': value} for key, value in CURR_PRICE.items()
        }
        try:
            new_item = stripe.Product.create(
                description=self.description,
                name=self.name
            )
            self.stripes_id = new_item.id
            new_price = stripe.Price.create(
                currency=self.currency,
                product=self.stripes_id,
                unit_amount=unit_amount,
                currency_options=options
            )
            self.price_id = new_price.id
        except Exception as e:
            logger.warning(str(e))
        super(Item, self).save(*args, **kwargs)


class Order(models.Model):
    number = models.PositiveIntegerField(verbose_name='Номер заказа')
    items = models.ManyToManyField(
        Item,
        related_name='orders',
        verbose_name='товары',
        through='Count'
    )
    discount = models.ForeignKey(
        'Discount',
        related_name='items',
        verbose_name='скидки',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    class Meta():
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'

    def __str__(self):
        return str(self.number)
        # return ', '.join([item.name for item in self.items.all()])


class Tax(models.Model):
    name = models.CharField(verbose_name='Налог', max_length=30)
    description = models.CharField(
        verbose_name='Описание',
        max_length=75,
        blank=True,
        null=True)
    percentage = models.PositiveIntegerField(
        verbose_name='Процент',
        validators=[MaxValueValidator(99)]
    )
    stripes_id = models.CharField(
        verbose_name='идентификатор на сервере',
        max_length=40,
        blank=True
    )

    class Meta():
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            new_item = stripe.TaxRate.create(
                description=self.description,
                display_name=self.name,
                percentage=self.percentage,
                inclusive=False
            )
            self.stripes_id = new_item.id
        except Exception as e:
            logger.warning(str(e))
        super(Tax, self).save(*args, **kwargs)


class Discount(models.Model):
    name = models.CharField(verbose_name='Скидка', max_length=30)
    percentage = models.PositiveIntegerField(
        verbose_name='Процент',
        validators=[MaxValueValidator(99)]
    )
    stripes_id = models.CharField(
        verbose_name='идентификатор на сервере',
        max_length=40,
        blank=True
    )

    class Meta():
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            new_item = stripe.Coupon.create(
                percent_off=self.percentage
            )
            self.stripes_id = new_item.id
        except Exception as e:
            logger.warning(str(e))
        super(Discount, self).save(*args, **kwargs)


class Count(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_counts',
        verbose_name='Заказ'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='item_counts',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MaxValueValidator(99)]
    )

    class Meta():
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'
        ordering = ('order__number',)

    def __str__(self):
        return f'Заказ {self.order.number} - {self.quantity}*{self.item.name}'
