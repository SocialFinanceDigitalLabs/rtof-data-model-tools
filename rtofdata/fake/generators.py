import builtins
import re
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta

__delta_pattern = re.compile(r"([+-]?\d+)([ymd])?", flags=re.IGNORECASE)


def get_date_or_delta(date_string, context_date):
    if not date_string:
        return context_date

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


def unique_identifier(faker: Faker, *args, **kwargs):
    return faker.unique.bothify(text="??-##", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def ni_number(faker: Faker, *args, **kwargs):
    return faker.unique.bothify(text="??######", letters="ABCEGHJKLMNPRSTWXYZ") + faker.random.choice("ABCD")


def temp_ni_number(faker: Faker, *args, **kwargs):
    return faker.unique.bothify(text="##T#####")


def year(faker: Faker, context, **kwargs):
    start = context['start'].year
    end = context['end'].year
    return faker.random.randint(start, end)


def monthyear(faker: Faker, context, **kwargs):
    my_date = date(faker, context, **kwargs)
    return my_date.strftime("%Y-%m")


def string(faker: Faker, *args, **kwargs):
    return faker.word()


def date(faker: Faker, context, **kwargs):
    return context['date']


def fixed(faker: Faker, context, value, **kwargs):
    return value


def date_between(faker: Faker, context, start_date, end_date, format="%Y-%m-%d", converter=None, **kwargs):
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


def categorical(faker: Faker, context, field, dimensions=None, **kwargs):
    if not dimensions:
        dimensions = field.dimensions.values
    if dimensions:
        return faker.random.choice(dimensions)
    else:
        return None


def list(faker: Faker, context, field, min=0, max=2, unique=True, dimensions=None, sort_values=True, **kwargs):
    if dimensions is None:
        dimensions = field.dimensions.values

    num_values = faker.random.randint(min, max)
    values = [faker.random.choice(dimensions) for i in range(0, num_values)]

    if unique:
        values = [v for v in set(values)]

    if sort_values:
        values.sort()

    return ", ".join(values)


def integer(faker: Faker, *args, min=0, max=100, **kwargs):
    return faker.random.randint(min, max)


def age_finished_study(faker: Faker, context, record, min, max, **kwargs):
    highest_qual_achieved = record['highest_qualification_achieved']
    if highest_qual_achieved == "Unknown":
        return faker.random.randint(min, max)
    return None

 