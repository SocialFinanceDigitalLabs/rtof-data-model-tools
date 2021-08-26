import builtins
import re
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta

__delta_pattern = re.compile(r"([+-]?\d+)([ymd])?", flags=re.IGNORECASE)


def get_date_or_delta(date_string, context_date):
    if not date_string:
        context_date

    if hasattr(date_string, "year"):
        return date_string

    if isinstance(date_string, int):
        return context_date + relativedelta(days=date_string)

    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        pass

    match = __delta_pattern.match(date_string)
    if not match:
        raise ValueError(f"Unrecognised date pattern: {date_string}")

    value = int(match.groups()[0])
    unit = match.groups()[1].lower()
    if unit == "y":
        return context_date + relativedelta(years=value)
    elif unit == "m":
        return context_date + relativedelta(months=value)
    else:
        return context_date + relativedelta(days=value)


def unique_identifier(faker: Faker, context, **kwargs):
    return faker.unique.bothify(text="????-????-????-####", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def year(faker: Faker, context, **kwargs):
    start = context['start'].year
    end = context['end'].year
    return faker.random.randint(start, end)


def string(faker: Faker, context, field, **kwargs):
    return faker.word()


def date(faker: Faker, context, **kwargs):
    return context['date']


def fixed(faker: Faker, context, value, **kwargs):
    return value


def date_between(faker: Faker, context, start_date, end_date, format=None, converter=None, **kwargs):
    start_date = get_date_or_delta(start_date, context['date'])
    end_date = get_date_or_delta(end_date, context['date'])

    date_value = faker.date_between(start_date, end_date)
    if format:
        date_value = date_value.strftime(format)

    if converter:
        try:
            date_value = globals()[converter](date_value)
        except:
            date_value = getattr(builtins, converter)(date_value)

    return date_value


def categorical(faker: Faker, context, field, **kwargs):
    if field.dimensions.values:
        return faker.random.choice(field.dimensions.values)
    else:
        return None


def list(faker: Faker, context, field, **kwargs):
    if field.dimensions.values:
        return [faker.random.choice(field.dimensions.values)]
    else:
        return None


def integer(faker: Faker, context, **kwargs):
    return faker.random.randint(0, 100)