# features/products.feature

Feature: The product store service back-end
  As a Product Store Owner
  I need a RESTful catalog service
  So that I can keep track of all my products

  Background:
    Given the following products
      | name     | description     | price   | available | category   |
      | Hat      | A red fedora    | 59.95   | True      | CLOTHS     |
      | Shoes    | Blue shoes      | 120.50  | False     | CLOTHS     |
      | Big Mac  | 1/4 lb burger   | 5.99    | True      | FOOD       |
      | Sheets   | Full bed sheets | 87.00   | True      | HOUSEWARES |
      | Lamp     | Desk lamp       | 25.00   | True      | HOME_GOODS |
      | Keyboard | Mechanical KB   | 75.00   | False     | ELECTRONICS|
      | Monitor  | Curved monitor  | 299.99  | True      | ELECTRONICS|
      | Book     | Python Guide    | 45.00   | True      | BOOKS      |
      | Chair    | Ergonomic chair | 200.00  | False     | FURNITURE  |
      | Table    | Dining table    | 350.00  | True      | FURNITURE  |

  Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Catalog Administration" in the title
    And I should not see "404 Not Found"

  Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hammer"
    And I set the "Description" to "Claw hammer"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "34.95"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hammer" in the "Name" field
    And I should see "Claw hammer" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "Tools" in the "Category" dropdown
    And I should see "34.95" in the "Price" field

  Scenario: Read a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 1 rows
    And I should see "Hat" in the "Name" field of the 1st row
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "Cloths" in the "Category" dropdown
    And I should see "59.95" in the "Price" field

  Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "Shoes"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 1 rows
    And I should see "Shoes" in the "Name" field of the 1st row
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Shoes" in the "Name" field
    When I set the "Description" to "Brand new running shoes"
    And I select "True" in the "Available" dropdown
    And I set the "Price" to "150.00"
    And I press the "Update" button
    Then I should see the message "Success"
    And I should see "Brand new running shoes" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "150.00" in the "Price" field
    When I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Brand new running shoes" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "150.00" in the "Price" field

  Scenario: Delete a Product
    When I visit the "Home Page"
    And I set the "Name" to "Big Mac"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 1 rows
    And I should see "Big Mac" in the "Name" field of the 1st row
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Success"
    And I should not see "Big Mac" in the results

  Scenario: List all Products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 10 rows
    And I should see "Hat" in the "Name" field of the 1st row
    And I should see "Shoes" in the "Name" field of the 2nd row
    And I should see "Big Mac" in the "Name" field of the 3rd row
    And I should see "Sheets" in the "Name" field of the 4th row

  Scenario: Search for Products by Category
    When I visit the "Home Page"
    And I select "ELECTRONICS" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 2 rows
    And I should see "Keyboard" in the "Name" field of the 1st row
    And I should see "Monitor" in the "Name" field of the 2nd row

  Scenario: Search for Products by Availability
    When I visit the "Home Page"
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 3 rows
    And I should see "Shoes" in the "Name" field of the 1st row
    And I should see "Keyboard" in the "Name" field of the 2nd row
    And I should see "Chair" in the "Name" field of the 3rd row

  Scenario: Search for Products by Name
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 1 rows
    And I should see "Hat" in the "Name" field of the 1st row

  Scenario: Search for Products by Partial Name
    When I visit the "Home Page"
    And I set the "Name" to "book"
    And I press the "Search" button
    Then I should see the message "Success"
    And the "results" table should contain 1 rows
    And I should see "Book" in the "Name" field of the 1st row