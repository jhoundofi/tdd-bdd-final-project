######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestProductService
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product, Category
from tests.factories import ProductFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ############################################################
    #  T E S T   C A S E S
    ############################################################
    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

        # Uncomment this code once READ is implemented
        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)


    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        logging.debug("Product no name: %s", new_product)
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with wrong Content-Type"""
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Get a single Product"""
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(data["description"], test_product.description)
        self.assertEqual(Decimal(data["price"]), test_product.price)
        self.assertEqual(data["available"], test_product.available)
        self.assertEqual(data["category"], test_product.category.name)


    def test_get_product_not_found(self):
        """It should not Get a Product that's not found"""
        response = self.client.get(f"{BASE_URL}/0")  # Use an ID that won't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update an existing Product"""
        # Create a product to update
        test_product = self._create_products(1)[0]
        logging.debug("Original Product: %s", test_product.serialize())

        # Update the product's attributes
        new_description = "Updated description for testing"
        new_price = Decimal("99.99")
        new_available = False
        new_category = "AUTOMOTIVE" # Assuming this is a valid category name

        test_product.description = new_description
        test_product.price = new_price
        test_product.available = new_available
        test_product.category = Category[new_category] # Update the enum directly in the test object

        # Send the update request
        response = self.client.put(f"{BASE_URL}/{test_product.id}", json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        updated_product_json = response.get_json()
        self.assertEqual(updated_product_json["id"], test_product.id)
        self.assertEqual(updated_product_json["description"], new_description)
        self.assertEqual(Decimal(updated_product_json["price"]), new_price)
        self.assertEqual(updated_product_json["available"], new_available)
        self.assertEqual(updated_product_json["category"], new_category)

        # Fetch the product again to ensure it's updated in the database
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fetched_product_json = response.get_json()
        self.assertEqual(fetched_product_json["description"], new_description)
        self.assertEqual(Decimal(fetched_product_json["price"]), new_price)
        self.assertEqual(fetched_product_json["available"], new_available)
        self.assertEqual(fetched_product_json["category"], new_category)


    def test_update_product_not_found(self):
        """It should not Update a Product that's not found"""
        product_data = ProductFactory().serialize()
        response = self.client.put(f"{BASE_URL}/0", json=product_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product_no_data(self):
        """It should not Update a Product with no data"""
        test_product = self._create_products(1)[0]
        response = self.client.put(f"{BASE_URL}/{test_product.id}", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_bad_data(self):
        """It should not Update a Product with bad data"""
        test_product = self._create_products(1)[0]
        bad_data = test_product.serialize()
        bad_data["price"] = "not-a-number"
        response = self.client.put(f"{BASE_URL}/{test_product.id}", json=bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_wrong_content_type(self):
        """It should not Update a Product with wrong Content-Type"""
        test_product = self._create_products(1)[0]
        response = self.client.put(f"{BASE_URL}/{test_product.id}", data="bad data", content_type="text/plain")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_product(self):
        """It should Delete a Product"""
        products = self._create_products(3) # Create 3 products
        product_count = self.get_product_count() # Get initial count from API
        self.assertEqual(product_count, 3)

        test_product = products[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0) # Ensure no content is returned

        # Verify the product is gone
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify the count has decreased
        new_product_count = self.get_product_count()
        self.assertEqual(new_product_count, product_count - 1)


    def test_delete_product_not_found(self):
        """It should not Delete a Product that's not found"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) # Delete on non-existent resource is idempotent (204 OK)


    # ----------------------------------------------------------
    # TEST LIST ALL
    # ----------------------------------------------------------
    def test_list_all_products(self):
        """It should List all Products"""
        self._create_products(5) # Create 5 products
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)


    def test_list_no_products(self):
        """It should return an empty list if no Products are found"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])

    # ----------------------------------------------------------
    # TEST LIST BY NAME
    # ----------------------------------------------------------
    def test_list_products_by_name(self):
        """It should List Products by Name"""
        products = self._create_products(5)
        # Get a name that exists and has multiple instances
        # (This relies on ProductFactory sometimes creating duplicate names)
        test_name = products[0].name
        count = len([p for p in products if p.name == test_name])

        response = self.client.get(BASE_URL, query_string=f"name={test_name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), count)
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_list_products_by_name_not_found(self):
        """It should return empty list if Name is not found"""
        self._create_products(3)
        response = self.client.get(BASE_URL, query_string="name=NonExistentName")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])

    # ----------------------------------------------------------
    # TEST LIST BY CATEGORY
    # ----------------------------------------------------------
    def test_list_products_by_category(self):
        """It should List Products by Category"""
        products = self._create_products(10)
        # Get a category that exists and has multiple instances
        test_category = products[0].category.name # Get the string name of the category
        count = len([p for p in products if p.category.name == test_category])

        response = self.client.get(BASE_URL, query_string=f"category={test_category}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), count)
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_list_products_by_category_not_found(self):
        """It should return empty list if Category is not found"""
        self._create_products(3)
        response = self.client.get(BASE_URL, query_string="category=INVALID_CATEGORY")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])

    # ----------------------------------------------------------
    # TEST LIST BY AVAILABILITY
    # ----------------------------------------------------------
    def test_list_products_by_availability(self):
        """It should List Products by Availability"""
        products = self._create_products(10)
        test_available = products[0].available
        count = len([p for p in products if p.available == test_available])

        # Test for True/False directly
        response = self.client.get(BASE_URL, query_string=f"available={str(test_available).lower()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), count)
        for product in data:
            self.assertEqual(product["available"], test_available)

    def test_list_products_by_availability_invalid_value(self):
        """It should return Bad Request for invalid availability value"""
        self._create_products(3)
        response = self.client.get(BASE_URL, query_string="available=maybe")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid boolean value for available", data["message"])

    ######################################################################
    # Utility functions
    ######################################################################

    def get_product_count(self):
        """save the current number of products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # logging.debug("data = %s", data)
        return len(data)