# discounts/services.py
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Discount, DiscountUsage


def apply_discount(code, user, order_price, order_id=None):
    try:
        discount = Discount.objects.get(code=code, is_active=True)
    except Discount.DoesNotExist:
        raise ValidationError("کد تخفیف معتبر نیست")

    now = timezone.now()
    if not (discount.start_at <= now <= discount.end_at):
        raise ValidationError("کد تخفیف منقضی شده")

    if order_price < discount.min_order_price:
        raise ValidationError("مبلغ سفارش کمتر از حد مجاز است")

    if DiscountUsage.objects.filter(discount=discount, user=user).exists():
        raise ValidationError("این کد قبلاً توسط شما استفاده شده")

    if discount.max_usage is not None:
        total_used = DiscountUsage.objects.filter(discount=discount).count()
        if total_used >= discount.max_usage:
            raise ValidationError("سقف استفاده از این کد پر شده")

    return calculate_discount(discount, order_price)


def calculate_discount(discount, order_price):
    if discount.type == Discount.PERCENT:
        return (order_price * discount.value) // 100
    return min(discount.value, order_price)






def final_apply_discount(code, user, order_price, order_id):
    try:
        discount = Discount.objects.get(code=code, is_active=True)
    except Discount.DoesNotExist:
        raise ValidationError("کد تخفیف معتبر نیست")

    now = timezone.now()
    if not (discount.start_at <= now <= discount.end_at):
        raise ValidationError("کد تخفیف منقضی شده")

    if order_price < discount.min_order_price:
        raise ValidationError("مبلغ سفارش کمتر از حد مجاز است")

    if DiscountUsage.objects.filter(discount=discount, user=user).exists():
        raise ValidationError("این کد قبلاً توسط شما استفاده شده")

    if discount.max_usage is not None:
        total_used = DiscountUsage.objects.filter(discount=discount).count()
        if total_used >= discount.max_usage:
            raise ValidationError("سقف استفاده از این کد پر شده")

    with transaction.atomic():
        DiscountUsage.objects.create(
            discount=discount,
            user=user,
            order_id=order_id
        )

    

