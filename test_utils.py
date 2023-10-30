from faker import Faker

from get_user import get_user


def create_fake_host(fake: Faker, user_id: int):
    new_host = {
        'user_id': user_id,
        'about': fake.text(),
        'is_superhost': fake.boolean(),
        'response_rate': fake.random_int(min=0, max=10000) / 100,
        'acceptance_rate': fake.random_int(min=0, max=10000) / 100,
        'response_time': ['within an hour', 'within a few hours', 'within a day', 'a few days or more'][fake.random_int(min=0, max=3)],
        'identity_verified': fake.boolean(),
        'neighbourhood': fake.word(),
        'location': fake.word(),
    }
    return new_host


def create_fake_user(fake: Faker):
    return {
        'name': fake.name(),
        'picture_url': fake.url(),
        'email': fake.unique.email(),
        'password': fake.password(),
        'is_host': fake.boolean(),
    }


def create_fake_listing(fake, test_host_id: str):
    return {
        'host_id': test_host_id,
        'name': fake.name(),
        'picture_url': fake.url(),
        'price': fake.random_int(min=0, max=1000000) / 10,
        'coord': f"({fake.latitude()}, {fake.longitude()})",
        'property_type': fake.word(),
        'room_type': fake.word(),
        'accommodates': fake.random_int(min=1, max=15),
        'bathrooms': fake.word(),
        'bedrooms': fake.random_int(min=1, max=15),
        'beds': fake.random_int(min=1, max=15),
        'amenities': [fake.word()],
        'neighbourhood': fake.word(),
        'neighbourhood_overview': fake.text(),
        'rating': fake.random_int(min=0, max=5),
        'location': fake.word(),
    }

def create_fake_review(fake, test_listing_id: str, test_user_id: str):
    return {
        'listing_id': test_listing_id,
        'reviewer_id': test_user_id,
        'comments': fake.text(),
        'rating': fake.random_int(min=0, max=5),
    }


def delete_keys(dic: dict, keys: list):
    for key in keys:
        del dic[key]
