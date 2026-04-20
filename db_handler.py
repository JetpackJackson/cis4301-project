from MARIADB_CREDS import DB_CONFIG
from mariadb import connect
from models.RentalHistory import RentalHistory
from models.Waitlist import Waitlist
from models.Item import Item
from models.Rental import Rental
from models.Customer import Customer
from datetime import date, timedelta


conn = connect(
    user=DB_CONFIG["username"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    database=DB_CONFIG["database"],
    port=DB_CONFIG["port"],
)


cur = conn.cursor()


def add_item(new_item: Item = None):
    """
    new_item - An Item object containing a new item to be inserted into the DB in the item table.
        new_item and its attributes will never be None.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute("SELECT MAX(i_item_sk) FROM item")
    max_sk = cur.fetchone()[0]
    new_sk = max_sk + 1 if max_sk else 1

    rec_start_date = f"{new_item.start_year}-01-01"

    cur.execute(
        """
        INSERT INTO item (i_item_sk, i_item_id, i_rec_start_date, i_product_name, i_brand, 
                         i_class, i_category, i_manufact, i_current_price, i_num_owned)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            new_sk,
            new_item.item_id,
            rec_start_date,
            new_item.product_name,
            new_item.brand,
            new_item.category,
            new_item.category,
            new_item.manufact,
            new_item.current_price,
            new_item.num_owned,
        ),
    )


def add_customer(new_customer: Customer = None):
    """
    new_customer - A Customer object containing a new customer to be inserted into the DB in the customer table.
        new_customer and its attributes will never be None.
    """
    # raise NotImplementedError("you must implement this function")
    parts = new_customer.address.split(", ")
    if len(parts) >= 3:
        street_part = parts[0]
        city = parts[1]
        state_zip = parts[2].split(" ")
        state = state_zip[0]
        zip_code = state_zip[1] if len(state_zip) > 1 else ""
    else:
        street_part = ""
        city = ""
        state = ""
        zip_code = ""

    street_parts = street_part.split(" ", 1)
    street_number = street_parts[0] if street_parts else ""
    street_name = street_parts[1] if len(street_parts) > 1 else ""

    cur.execute("SELECT MAX(ca_address_sk) FROM customer_address")
    max_addr_sk = cur.fetchone()[0]
    new_addr_sk = max_addr_sk + 1 if max_addr_sk else 1

    cur.execute(
        """
        INSERT INTO customer_address (ca_address_sk, ca_street_number, ca_street_name, ca_city, ca_state, ca_zip)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (new_addr_sk, street_number, street_name, city, state, zip_code),
    )

    name_parts = new_customer.name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    cur.execute("SELECT MAX(c_customer_sk) FROM customer")
    max_cust_sk = cur.fetchone()[0]
    new_cust_sk = max_cust_sk + 1 if max_cust_sk else 1

    cur.execute(
        """
        INSERT INTO customer (c_customer_sk, c_customer_id, c_first_name, c_last_name, c_email_address, c_current_addr_sk)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            new_cust_sk,
            new_customer.customer_id,
            first_name,
            last_name,
            new_customer.email,
            new_addr_sk,
        ),
    )


def edit_customer(original_customer_id: str = None, new_customer: Customer = None):
    """
    original_customer_id - A string containing the customer id for the customer to be edited.
    new_customer - A Customer object containing attributes to update. If an attribute is None, it should not be altered.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute(
        "SELECT c_customer_sk, c_current_addr_sk FROM customer WHERE c_customer_id = ?",
        (original_customer_id,),
    )
    row = cur.fetchone()
    if not row:
        return

    cust_sk, addr_sk = row

    if new_customer.name is not None:
        name_parts = new_customer.name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        cur.execute(
            "UPDATE customer SET c_first_name = ?, c_last_name = ? WHERE c_customer_sk = ?",
            (first_name, last_name, cust_sk),
        )

    if new_customer.email is not None:
        cur.execute(
            "UPDATE customer SET c_email_address = ? WHERE c_customer_sk = ?",
            (new_customer.email, cust_sk),
        )

    if new_customer.customer_id is not None:
        cur.execute(
            "UPDATE customer SET c_customer_id = ? WHERE c_customer_sk = ?",
            (new_customer.customer_id, cust_sk),
        )

    if new_customer.address is not None:
        parts = new_customer.address.split(", ")
        if len(parts) >= 3:
            street_part = parts[0]
            city = parts[1]
            state_zip = parts[2].split(" ")
            state = state_zip[0]
            zip_code = state_zip[1] if len(state_zip) > 1 else ""
        else:
            street_part = ""
            city = ""
            state = ""
            zip_code = ""

        street_parts = street_part.split(" ", 1)
        street_number = street_parts[0] if street_parts else ""
        street_name = street_parts[1] if len(street_parts) > 1 else ""

        cur.execute(
            """
            UPDATE customer_address 
            SET ca_street_number = ?, ca_street_name = ?, ca_city = ?, ca_state = ?, ca_zip = ?
            WHERE ca_address_sk = ?
        """,
            (street_number, street_name, city, state, zip_code, addr_sk),
        )


def rent_item(item_id: str = None, customer_id: str = None):
    """
    item_id - A string containing the Item ID for the item being rented.
    customer_id - A string containing the customer id of the customer renting the item.
    """
    # raise NotImplementedError("you must implement this function")
    today = date.today()
    rental_date = today.strftime("%Y-%m-%d")
    due_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    cur.execute(
        """
        INSERT INTO rental (item_id, customer_id, rental_date, due_date)
        VALUES (?, ?, ?, ?)
    """,
        (item_id, customer_id, rental_date, due_date),
    )


def waitlist_customer(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's new place in line.
    """
    # raise NotImplementedError("you must implement this function")
    length = line_length(item_id)
    new_place = length + 1

    cur.execute(
        """
        INSERT INTO waitlist (item_id, customer_id, place_in_line)
        VALUES (?, ?, ?)
    """,
        (item_id, customer_id, new_place),
    )

    return new_place


def update_waitlist(item_id: str = None):
    """
    Removes person at position 1 and shifts everyone else down by 1.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute(
        "SELECT customer_id FROM waitlist WHERE item_id = ? AND place_in_line = 1",
        (item_id,),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "DELETE FROM waitlist WHERE item_id = ? AND place_in_line = 1", (item_id,)
        )
        cur.execute(
            "UPDATE waitlist SET place_in_line = place_in_line - 1 WHERE item_id = ?",
            (item_id,),
        )


def return_item(item_id: str = None, customer_id: str = None):
    """
    Moves a rental from rental to rental_history with return_date = today.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute(
        "SELECT rental_date, due_date FROM rental WHERE item_id = ? AND customer_id = ?",
        (item_id, customer_id),
    )
    row = cur.fetchone()
    if row:
        rental_date, due_date = row
        return_date = date.today().strftime("%Y-%m-%d")

        cur.execute(
            """
            INSERT INTO rental_history (item_id, customer_id, rental_date, due_date, return_date)
            VALUES (?, ?, ?, ?, ?)
        """,
            (item_id, customer_id, rental_date, due_date, return_date),
        )

        cur.execute(
            "DELETE FROM rental WHERE item_id = ? AND customer_id = ?",
            (item_id, customer_id),
        )


def grant_extension(item_id: str = None, customer_id: str = None):
    """
    Adds 14 days to the due_date.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute(
        "SELECT due_date FROM rental WHERE item_id = ? AND customer_id = ?",
        (item_id, customer_id),
    )
    row = cur.fetchone()
    if row:
        due_date = row[0]
        new_due_date = due_date + timedelta(days=14)
        cur.execute(
            "UPDATE rental SET due_date = ? WHERE item_id = ? AND customer_id = ?",
            (new_due_date, item_id, customer_id),
        )


def get_filtered_items(
    filter_attributes: Item = None,
    use_patterns: bool = False,
    min_price: float = -1,
    max_price: float = -1,
    min_start_year: int = -1,
    max_start_year: int = -1,
) -> list[Item]:
    """
    Returns a list of Item objects matching the filters.
    """
    # raise NotImplementedError("you must implement this function")
    query = "SELECT i_item_id, i_product_name, i_brand, i_category, i_manufact, i_current_price, YEAR(i_rec_start_date), i_num_owned FROM item"
    conditions = []
    params = []

    if filter_attributes.item_id is not None:
        if use_patterns:
            conditions.append("i_item_id LIKE ?")
            params.append(f"%{filter_attributes.item_id}%")
        else:
            conditions.append("i_item_id = ?")
            params.append(filter_attributes.item_id)

    if filter_attributes.product_name is not None:
        if use_patterns:
            conditions.append("i_product_name LIKE ?")
            params.append(f"%{filter_attributes.product_name}%")
        else:
            conditions.append("i_product_name = ?")
            params.append(filter_attributes.product_name)

    if filter_attributes.brand is not None:
        if use_patterns:
            conditions.append("i_brand LIKE ?")
            params.append(f"%{filter_attributes.brand}%")
        else:
            conditions.append("i_brand = ?")
            params.append(filter_attributes.brand)

    if filter_attributes.category is not None:
        if use_patterns:
            conditions.append("i_category LIKE ?")
            params.append(f"%{filter_attributes.category}%")
        else:
            conditions.append("i_category = ?")
            params.append(filter_attributes.category)

    if filter_attributes.manufact is not None:
        if use_patterns:
            conditions.append("i_manufact LIKE ?")
            params.append(f"%{filter_attributes.manufact}%")
        else:
            conditions.append("i_manufact = ?")
            params.append(filter_attributes.manufact)

    if min_price != -1:
        conditions.append("i_current_price >= ?")
        params.append(min_price)

    if max_price != -1:
        conditions.append("i_current_price <= ?")
        params.append(max_price)

    if min_start_year != -1:
        conditions.append("YEAR(i_rec_start_date) >= ?")
        params.append(min_start_year)

    if max_start_year != -1:
        conditions.append("YEAR(i_rec_start_date) <= ?")
        params.append(max_start_year)

    if filter_attributes.num_owned != -1:
        conditions.append("i_num_owned = ?")
        params.append(filter_attributes.num_owned)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    items = []
    for row in rows:
        items.append(
            Item(
                item_id=row[0].strip() if row[0] else None,
                product_name=row[1].strip() if row[1] else None,
                brand=row[2].strip() if row[2] else None,
                category=row[3].strip() if row[3] else None,
                manufact=row[4].strip() if row[4] else None,
                current_price=float(row[5]) if row[5] else -1,
                start_year=int(row[6]) if row[6] else -1,
                num_owned=int(row[7]) if row[7] else -1,
            )
        )

    return items


def get_filtered_customers(
    filter_attributes: Customer = None, use_patterns: bool = False
) -> list[Customer]:
    """
    Returns a list of Customer objects matching the filters.
    """
    # raise NotImplementedError("you must implement this function")
    query = """SELECT c.c_customer_id, CONCAT(c.c_first_name, ' ', c.c_last_name), 
               CONCAT(ca.ca_street_number, ' ', ca.ca_street_name, ', ', ca.ca_city, ', ', ca.ca_state, ' ', ca.ca_zip), 
               c.c_email_address 
               FROM customer c 
               JOIN customer_address ca ON c.c_current_addr_sk = ca.ca_address_sk"""
    conditions = []
    params = []

    if filter_attributes.customer_id is not None:
        if use_patterns:
            conditions.append("c.c_customer_id LIKE ?")
            params.append(f"%{filter_attributes.customer_id}%")
        else:
            conditions.append("c.c_customer_id = ?")
            params.append(filter_attributes.customer_id)

    if filter_attributes.name is not None:
        if use_patterns:
            conditions.append("CONCAT(c.c_first_name, ' ', c.c_last_name) LIKE ?")
            params.append(f"%{filter_attributes.name}%")
        else:
            conditions.append("CONCAT(c.c_first_name, ' ', c.c_last_name) = ?")
            params.append(filter_attributes.name)

    if filter_attributes.address is not None:
        if use_patterns:
            conditions.append(
                "CONCAT(ca.ca_street_number, ' ', ca.ca_street_name, ', ', ca.ca_city, ', ', ca.ca_state, ' ', ca.ca_zip) LIKE ?"
            )
            params.append(f"%{filter_attributes.address}%")
        else:
            conditions.append(
                "CONCAT(ca.ca_street_number, ' ', ca.ca_street_name, ', ', ca.ca_city, ', ', ca.ca_state, ' ', ca.ca_zip) = ?"
            )
            params.append(filter_attributes.address)

    if filter_attributes.email is not None:
        if use_patterns:
            conditions.append("c.c_email_address LIKE ?")
            params.append(f"%{filter_attributes.email}%")
        else:
            conditions.append("c.c_email_address = ?")
            params.append(filter_attributes.email)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    customers = []
    for row in rows:
        customers.append(
            Customer(
                customer_id=row[0].strip() if row[0] else None,
                name=row[1].strip() if row[1] else None,
                address=row[2].strip() if row[2] else None,
                email=row[3].strip() if row[3] else None,
            )
        )

    return customers


def get_filtered_rentals(
    filter_attributes: Rental = None,
    min_rental_date: str = None,
    max_rental_date: str = None,
    min_due_date: str = None,
    max_due_date: str = None,
    use_patterns: bool = False,
) -> list[Rental]:
    """
    Returns a list of Rental objects matching the filters.
    """
    # raise NotImplementedError("you must implement this function")
    query = "SELECT item_id, customer_id, rental_date, due_date FROM rental"
    conditions = []
    params = []

    if filter_attributes.item_id is not None:
        if use_patterns:
            conditions.append("item_id LIKE ?")
            params.append(f"%{filter_attributes.item_id}%")
        else:
            conditions.append("item_id = ?")
            params.append(filter_attributes.item_id)

    if filter_attributes.customer_id is not None:
        if use_patterns:
            conditions.append("customer_id LIKE ?")
            params.append(f"%{filter_attributes.customer_id}%")
        else:
            conditions.append("customer_id = ?")
            params.append(filter_attributes.customer_id)

    if min_rental_date is not None:
        conditions.append("rental_date >= ?")
        params.append(min_rental_date)

    if max_rental_date is not None:
        conditions.append("rental_date <= ?")
        params.append(max_rental_date)

    if min_due_date is not None:
        conditions.append("due_date >= ?")
        params.append(min_due_date)

    if max_due_date is not None:
        conditions.append("due_date <= ?")
        params.append(max_due_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    rentals = []
    for row in rows:
        rentals.append(
            Rental(
                item_id=row[0].strip() if row[0] else None,
                customer_id=row[1].strip() if row[1] else None,
                rental_date=str(row[2]) if row[2] else None,
                due_date=str(row[3]) if row[3] else None,
            )
        )

    return rentals


def get_filtered_rental_histories(
    filter_attributes: RentalHistory = None,
    min_rental_date: str = None,
    max_rental_date: str = None,
    min_due_date: str = None,
    max_due_date: str = None,
    min_return_date: str = None,
    max_return_date: str = None,
    use_patterns: bool = False,
) -> list[RentalHistory]:
    """
    Returns a list of RentalHistory objects matching the filters.
    """
    # raise NotImplementedError("you must implement this function")
    query = "SELECT item_id, customer_id, rental_date, due_date, return_date FROM rental_history"
    conditions = []
    params = []

    if filter_attributes.item_id is not None:
        if use_patterns:
            conditions.append("item_id LIKE ?")
            params.append(f"%{filter_attributes.item_id}%")
        else:
            conditions.append("item_id = ?")
            params.append(filter_attributes.item_id)

    if filter_attributes.customer_id is not None:
        if use_patterns:
            conditions.append("customer_id LIKE ?")
            params.append(f"%{filter_attributes.customer_id}%")
        else:
            conditions.append("customer_id = ?")
            params.append(filter_attributes.customer_id)

    if min_rental_date is not None:
        conditions.append("rental_date >= ?")
        params.append(min_rental_date)

    if max_rental_date is not None:
        conditions.append("rental_date <= ?")
        params.append(max_rental_date)

    if min_due_date is not None:
        conditions.append("due_date >= ?")
        params.append(min_due_date)

    if max_due_date is not None:
        conditions.append("due_date <= ?")
        params.append(max_due_date)

    if min_return_date is not None:
        conditions.append("return_date >= ?")
        params.append(min_return_date)

    if max_return_date is not None:
        conditions.append("return_date <= ?")
        params.append(max_return_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    histories = []
    for row in rows:
        histories.append(
            RentalHistory(
                item_id=row[0].strip() if row[0] else None,
                customer_id=row[1].strip() if row[1] else None,
                rental_date=str(row[2]) if row[2] else None,
                due_date=str(row[3]) if row[3] else None,
                return_date=str(row[4]) if row[4] else None,
            )
        )

    return histories


def get_filtered_waitlist(
    filter_attributes: Waitlist = None,
    min_place_in_line: int = -1,
    max_place_in_line: int = -1,
) -> list[Waitlist]:
    """
    Returns a list of Waitlist objects matching the filters.
    """
    # raise NotImplementedError("you must implement this function")
    query = "SELECT item_id, customer_id, place_in_line FROM waitlist"
    conditions = []
    params = []

    if filter_attributes.item_id is not None:
        conditions.append("item_id = ?")
        params.append(filter_attributes.item_id)

    if filter_attributes.customer_id is not None:
        conditions.append("customer_id = ?")
        params.append(filter_attributes.customer_id)

    if min_place_in_line != -1:
        conditions.append("place_in_line >= ?")
        params.append(min_place_in_line)

    if max_place_in_line != -1:
        conditions.append("place_in_line <= ?")
        params.append(max_place_in_line)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    waitlist_items = []
    for row in rows:
        waitlist_items.append(
            Waitlist(
                item_id=row[0].strip() if row[0] else None,
                customer_id=row[1].strip() if row[1] else None,
                place_in_line=int(row[2]) if row[2] else -1,
            )
        )

    return waitlist_items


def number_in_stock(item_id: str = None) -> int:
    """
    Returns num_owned - active rentals. Returns -1 if item doesn't exist.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute("SELECT i_num_owned FROM item WHERE i_item_id = ?", (item_id,))
    row = cur.fetchone()
    if not row:
        return -1

    num_owned = row[0]

    cur.execute("SELECT COUNT(*) FROM rental WHERE item_id = ?", (item_id,))
    active_rentals = cur.fetchone()[0]

    return num_owned - active_rentals


def place_in_line(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's place_in_line, or -1 if not on waitlist.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute(
        "SELECT place_in_line FROM waitlist WHERE item_id = ? AND customer_id = ?",
        (item_id, customer_id),
    )
    row = cur.fetchone()
    if not row:
        return -1
    return row[0]


def line_length(item_id: str = None) -> int:
    """
    Returns how many people are on the waitlist for this item.
    """
    # raise NotImplementedError("you must implement this function")
    cur.execute("SELECT COUNT(*) FROM waitlist WHERE item_id = ?", (item_id,))
    return cur.fetchone()[0]


def save_changes():
    """
    Commits all changes made to the db.
    """
    # raise NotImplementedError("you must implement this function")
    conn.commit()


def close_connection():
    """
    Closes the cursor and connection.
    """
    # raise NotImplementedError("you must implement this function")
    cur.close()
    conn.close()
