######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = 'product_'


@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert(message in context.driver.title)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert(text_string not in element.text)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    assert(element.first_selected_option.text == text)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert(element.get_attribute('value') == u'')

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html that is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################
@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(' ', '_') + '-btn'
    context.driver.find_element(By.ID, button_id).click()

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='product_name'
# We can then lowercase the name and prefix with product_ to get the id
##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    assert(found)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@then('I should see the message "{message}"')
def step_impl(context, message):
    """ Check the flash message """
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'), # Assuming flash message is displayed in an element with ID 'flash_message'
            message
        )
    )
    assert(found)

@then('I should see "{name}" in the results')
def step_impl(context, name):
    """ Check if the given name is in the search results table """
    # Assuming search results are within an element with ID 'search_results'
    # And we're looking for the name to be present anywhere within its text content
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    assert(found)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    """ Check if the given name is NOT in the search results table """
    element = context.driver.find_element(By.ID, 'search_results')
    # A more robust check might wait for the element to be visible/stable
    # and then check its text. Using a simple assert for now.
    assert(name not in element.text)


@then('the "{table_name}" table should contain {num_rows:d} rows')
def step_impl(context, table_name, num_rows):
    """ Checks if the table has the correct number of data rows """
    # Assuming 'search_results' is the ID of the table or a container for results
    # and data rows are <tr> elements within it.
    table_element = context.driver.find_element(By.ID, 'search_results')
    # Find all 'tr' elements. This might include a header row.
    rows = table_element.find_elements(By.TAG_NAME, 'tr')

    # Heuristic: if the first row contains 'ID', it's likely a header.
    # Adjust this based on your HTML structure (e.g., if you have <thead> and <tbody>,
    # you might want to specifically find 'tbody tr').
    actual_rows = len(rows)
    if actual_rows > 0 and 'ID' in rows[0].text:
        actual_rows -= 1 # Subtract 1 for the header row

    assert(actual_rows == num_rows)


@then('I should see "{value}" in the "{field_name}" field of the {row_num:d}{nth} row')
def step_impl(context, value, field_name, row_num, nth):
    """ Checks a specific field (column) in a specific row of the search results table """
    # Map the field_name (column header) to its corresponding 0-indexed column in the HTML table.
    # IMPORTANT: Adjust these indices if your table columns change!
    column_map = {
        "Id": 0,
        "Name": 1,
        "Description": 2,
        "Price": 3,
        "Available": 4,
        "Category": 5
    }
    column_index = column_map.get(field_name)

    assert column_index is not None, f"Column '{field_name}' not found in column_map. Check your step definition."

    # Get the search results table element
    table_element = context.driver.find_element(By.ID, 'search_results')

    # Get all the rows. If your table has a <thead> and <tbody>, you might do:
    # data_rows = table_element.find_elements(By.CSS_SELECTOR, 'tbody tr')
    # Otherwise, you need to account for the header row if present in the `tr` list.
    all_rows = table_element.find_elements(By.TAG_NAME, 'tr')

    # Adjust row_num (from Gherkin's 1-indexed) to 0-indexed for Python list.
    # Also, account for a potential header row if it's included in `all_rows`.
    # Assuming the first `tr` is a header row, then the first data row is `all_rows[1]`.
    # So, for 1st row (row_num=1), we access all_rows[1]; for 2nd row (row_num=2), all_rows[2], etc.
    # This means `row_num` directly corresponds to the index if we consider the header as index 0.
    # If there's no header, it would be `row_num - 1`.
    # Let's use a robust way to find the data row:
    data_rows = []
    if all_rows and 'ID' in all_rows[0].text: # Heuristic to detect header row
        data_rows = all_rows[1:] # Skip header
    else:
        data_rows = all_rows # No header, all are data rows

    assert len(data_rows) >= row_num, f"Not enough data rows in the table. Expected at least {row_num}, but found {len(data_rows)}."

    # Get the specific row element (0-indexed)
    row_element = data_rows[row_num - 1] # Adjust for 0-indexing of data_rows list

    # Get all cells (td) in that row
    cells = row_element.find_elements(By.TAG_NAME, 'td')
    assert len(cells) > column_index, f"Column index {column_index} is out of bounds for row."

    cell_text = cells[column_index].text.strip() # Get text and remove leading/trailing whitespace

    # Special handling for numerical (Price) and boolean (Available) values
    if field_name == "Price":
        # Convert both to float for comparison to avoid precision issues with strings
        assert float(cell_text) == float(value), f"Expected Price '{value}' but got '{cell_text}'"
    elif field_name == "Available":
        # Convert both to lowercase for case-insensitive boolean comparison
        assert cell_text.lower() == value.lower(), f"Expected Available '{value}' but got '{cell_text}'"
    else:
        assert cell_text == value, f"Expected '{value}' in field '{field_name}' but got '{cell_text}'"