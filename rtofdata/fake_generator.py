from faker import Faker


def unique_identifier(faker: Faker, context, **kwargs):
    return faker.unique.bothify(text="????-????-????-####", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def year(faker: Faker, context, **kwargs):
    start = context['start'].year
    end = context['end'].year
    return faker.random.randint(start, end)


def string(faker: Faker, context, field, **kwargs):
    return faker.sentence()


def date(faker: Faker, context, **kwargs):
    return context['date']


def year_between(faker: Faker, context, start_date, end_date, **kwargs):
    start = context['date'].year
    return faker.random.randint(start + start_date , start + end_date)


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