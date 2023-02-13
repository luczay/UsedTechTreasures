import pandas as pd
from flask import Flask, render_template, request, make_response
from scraper import Scraper
import constants
from database import Database

app = Flask(__name__)


@app.route('/')
def setup():
    """
        Render the setup.html template for the main page.
    """
    return render_template('setup.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    """
        Scrape data from the selected websites.
    """
    product_name = request.form.get('product_name')
    price_min = int(request.form.get('price_min'))
    price_max = int(request.form.get('price_max'))
    stop = int(request.form.get('number_of_products'))

    scraper = Scraper(product_name, price_min, price_max, stop)

    hardverapro = request.form.get('hardverapro')
    jofogas = request.form.get('jofogas')
    marketplace = request.form.get('marketplace')

    scraper.extract_data(hardverapro, jofogas, marketplace)
    scraper.clean_data()

    if request.form.get('display') == 'true':
        empty_table(temp=True)
        scraper.save_data(temp=True)

        concated_dfs = scraper.concat_dfs()

        return {'display': 'true', 'table': concated_dfs.to_html(table_id='content',
                                                                 classes='table',
                                                                 index=False)}
    else:
        scraper.save_data()
        return {'display': 'false'}


@app.route('/save', methods=['POST'])
def save():
    """
       Save the scraped data to the database.
    """
    df = get_db_content('temp_product')
    df = df.drop(columns=['id'])

    with Database() as db:
        db.add_scraped_data(df, temp=False)
        sql = "TRUNCATE TABLE temp_product"
        db.execute(sql)

    return {'is_done': 'true'}


@app.route('/database')
def database():
    """
        Render the database.html template for the database page.
    """
    return render_template('database.html')


@app.route('/db_content', methods=['POST'])
def db_content():
    """
        Get the content of the database
    """
    df = get_db_content()
    df = df.drop(columns=['id'])

    dict_for_json = {'table': df.to_html(table_id='content',
                                         classes='table',
                                         index=False)}
    return dict_for_json


@app.route('/clear', methods=['POST'])
def clear():
    """
        Removes records from either the temp_product table or the product table
    """
    df = get_db_content('temp_product')

    if len(df.index) == 0:
        empty_table()
    else:
        id_list = df['id'].to_list()
        ids = '('
        for prod_id in id_list:
            ids = ids + str(prod_id) + ', '
        ids = ids[0:-2] + ')'

        with Database() as db:
            sql = "DELETE FROM product WHERE id IN"
            sql = sql + ' ' + ids
            db.execute(sql)
            db.commit()

    return {'is_done': 'true'}


@app.route('/download', methods=['GET'])
def save_to_csv():
    """
        Generate a CSV file from either the temp_product table or the product_table
    """
    df = get_db_content('temp_product')
    if len(df.index) == 0:
        df = get_db_content('product')

    df_csv = df.to_csv(sep=';', encoding='utf-16')
    output = make_response(df_csv)
    output.headers["Content-Disposition"] = "attachment; filename=scraped_data.csv"
    output.headers["Content-type"] = "text/csv"

    return output


@app.route('/search', methods=['POST'])
def search():
    """
        Queries the database to retrieve products that match the specified product name, website, and price range.
    """
    product_name = request.form.get('product_name')
    site = request.form.get('site')
    price_range = request.form.get('price_range')

    slice_at = price_range.find('-')
    if slice_at != -1:
        price_min = price_range[0:slice_at]
        price_max = price_range[slice_at + 1:]
    elif price_range == '':
        price_min = 0
        price_max = 999999999
    else:
        price_min = price_range
        price_max = price_range

    with Database() as db:
        sql = """
                SELECT *
                FROM product
                WHERE 
                    name LIKE %s AND site LIKE %s AND price BETWEEN %s AND %s
              """
        db.execute(sql, (f"%{product_name}%", f"%{site}%", price_min, price_max))
        result = db.fetchall()

    df = pd.DataFrame(data=result, columns=['id'] + constants.columns)
    empty_table(temp=True)
    Database().add_scraped_data(df, temp=True)

    df = df.drop(columns=['id'])

    return {'display': 'true', 'table': df.to_html(table_id='content',
                                                   classes='table',
                                                   index=False)}


# ***************************************************************************************
#                               Helper functions

def get_db_content(db_name='product') -> pd.DataFrame:
    """
        Retrieves all records from the specified table.
    """
    with Database() as db:
        sql = """
                SELECT *
                FROM
              """
        sql = sql + ' ' + db_name
        db.execute(sql)
        result = db.fetchall()

    return pd.DataFrame(data=result, columns=['id'] + constants.columns)


def empty_table(temp=False):
    """
        Removes all records from the specified table.
    """
    db_name = 'product'

    if temp:
        db_name = 'temp_product'
    with Database() as db:
        sql = "TRUNCATE TABLE"
        sql = sql + ' ' + db_name
        db.execute(sql)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
