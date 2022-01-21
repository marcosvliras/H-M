import logging
import os
import requests
import pandas as pd
import numpy as np
import re
import sqlite3
import logging

from bs4        import BeautifulSoup
from datetime   import datetime
from sqlalchemy import create_engine

# data colection 
def data_collection( url, headers ):
    # Request to URL
    page = requests.get( url, headers=headers )

    # Beautiful soup object
    soup = BeautifulSoup( page.text, 'html.parser' )

    # ================= product Data ================= 
    products = soup.find( 'ul', class_='products-listing small' )
    products_list = products.find_all( 'article', class_='hm-product-item' )

    #id
    product_id = [p.get( 'data-articlecode' ) for p in products_list]

    #category
    product_cat = [p.get( 'data-category' ) for p in products_list]

    # name
    product_name = [p.find( 'a', class_='link' ).get_text() for p in products_list]

    # price
    product_price = [p.find( 'span', class_='price regular' ).get_text() for p in products_list]

    # dataframe from the products showed in main page
    data = pd.DataFrame( [product_id, product_cat, product_name, product_price] ).T
    data.columns = ['product_id', 'product_category', 'product_name','product_price']

    return data

def data_colection_by_product( data, headers ):
    # data colection by product
    custom_header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    df_compositions = pd.DataFrame()

    # unique columns for all products 
    aux = []

    cols = ['Art. No.', 'Composition', 'Fit', 'Product safety', 'Size']
    df_pattern = pd.DataFrame( columns=cols )

    # Using just the id from the data to go through each product and catch each feature inside the page of each product
    for i in range( len(data) ):

        # Api Requests
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i,'product_id'] + '.html'
        logger.debug( 'Product: %s', url )

        page = requests.get( url, headers=custom_header )
        
        # Beautifulsoup object
        soup = BeautifulSoup( page.text, 'html.parser' )
        
        # color name and product id
        product_list = soup.find_all( 'a', class_='filter-option miniature' ) + soup.find_all( 'a', class_='filter-option miniature active' )
        
        color_name = [p.get( 'data-color' ) for p in product_list]
        product_id = [p.get( 'data-articlecode' ) for p in product_list]
        
        # color and id data frame
        df_color = pd.DataFrame( [product_id,color_name] ).T
        df_color.columns = ['product_id','color_name']
        
        for j in range(len( df_color )):  
            
            # Api Requests
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j,'product_id'] + '.html'
            logger.debug( 'Color: %s', url )

            page = requests.get( url, headers=custom_header )

            # Beautifulsoup object
            soup = BeautifulSoup( page.text, 'html.parser' )

            
            # =========== product name ===========
            product_name = soup.find_all( 'h1', class_='primary product-item-headline' )
            product_name = product_name[0].get_text()

            
            # =========== product price ===========
            product_price = soup.find_all( 'div', class_='primary-row product-item-price' )
            product_price = re.findall( r'\d+\.?\d+', product_price[0].get_text() )[0]
            
            # =========== composition ===========
            product_composition_list = soup.find_all( 'div', class_='pdp-description-list-item' )

            composition = [list( filter( None, p.get_text().split( '\n' ) ) ) for p in product_composition_list]

            # rename dataframe
            df_aux = pd.DataFrame( composition ).T
            df_aux.columns = df_aux.iloc[0]
            

            # delete first row
            df_aux = df_aux.iloc[1:].fillna( method='ffill' )

            # remove pocket lining, shell, lining and pocket
            df_aux['Composition'] = df_aux['Composition'].replace( 'Pocket lining: ', '', regex=True )
            df_aux['Composition'] = df_aux['Composition'].replace( 'Shell: ', '', regex=True )
            df_aux['Composition'] = df_aux['Composition'].replace( 'Lining: ', '', regex=True )
            df_aux['Composition'] = df_aux['Composition'].replace( 'Pocket: ', '', regex=True )

            # garantee the same number of columns
            df_aux = pd.concat( [df_pattern, df_aux], axis=0 )
            
            if len(df_aux.columns) > 5:
                df_aux = df_aux.iloc[:,:-1]
            
            # rename columns
            df_aux.columns = ['product_id','composition','fit','product_safety','size']
            
            df_aux['product_name'] = product_name
            df_aux['product_price'] = product_price

            # just to know how many features has in the diferents products
            aux = aux + df_aux.columns.tolist()

            # merge
            df_aux = pd.merge( df_aux, df_color, how='left', on='product_id' )
            
            df_compositions = pd.concat( [df_compositions, df_aux], axis=0 )
            df_compositions = df_compositions.reset_index( drop=True )
            
    # Join Showroom data + details
    df_compositions['style_id'] = df_compositions['product_id'].apply( lambda x: x[:-3] )
    df_compositions['color_id'] = df_compositions['product_id'].apply( lambda x: x[-3:] )

    # scrapy datetime
    df_compositions['scrapy_datetime'] = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )

    return df_compositions

def data_cleaning( df_compositions ):
# data cleaning

    df_data  = df_compositions.dropna( subset=['product_id'] )

    # name
    df_data['product_name'] = df_data['product_name'].apply( lambda x: re.search( '\S+.+', x).group() ).str.lower()
    df_data['product_name'] = df_data['product_name'].str.replace( ' ', '_' )

    # price
    df_data['product_price'] = df_data['product_price'].astype( float )

    # color_name
    df_data['color_name'] = df_data['color_name'].apply( lambda x: x.replace(' ','_').lower() if pd.notnull(x) else x )

    # fit 
    df_data['fit'] = df_data['fit'].apply( lambda x: x.replace(' ','_').lower() if pd.notnull(x) else x )

    # size numeber
    df_data['size_number'] = df_data['size'].apply( lambda x: re.search( '\d{3}cm', x ).group() if pd.notnull(x) else x )
    df_data['size_number'] = df_data['size_number'].apply( lambda x: str( x ).replace( 'cm', '') )

    # size_model
    df_data['size_model'] = df_data['size'].str.extract( '(\d+/\d+)' )

    # product safety dropped
    df_data.drop( 'product_safety', axis=1, inplace=True )

    # ============== composition ===============

    df = df_data['composition'].str.split( ',', expand=True ).reset_index( drop=True )

    df_ref = pd.DataFrame( columns=['cotton','polyester','elasterell','spandex'], index=np.arange( len(data ) ) )

    # ============== composition ===============

    # ===== cotton =====
    df_cotton_0 = df.loc[df[0].str.contains( 'Cotton', na=True ), 0]

    df_cotton_1 = df.loc[df[1].str.contains( 'Cotton', na=True ), 1]

    # combine
    df_cotton = df_cotton_0.combine_first( df_cotton_1 )
    df_cotton.name = 'cotton'

    df_ref = pd.concat( [df_ref, df_cotton], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last' )]

    # ===== polyester =====  
    df_polyester_0 = df.loc[df[0].str.contains( 'Polyester', na=True ), 0]

    df_polyester_1 = df.loc[df[1].str.contains( 'Polyester', na=True ), 1]

    # combine
    df_polyester = df_polyester_0.combine_first( df_polyester_1 )
    df_polyester.name = 'polyester'

    df_ref = pd.concat( [df_ref, df_polyester], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last')]

    # ===== elasterell =====
    df_elasterell = df.loc[df[1].str.contains( 'Elasterell', na=True ), 1]
    df_elasterell.name = 'elasterell'

    df_ref = pd.concat( [df_ref, df_elasterell], axis=1 )
    df_ref = df_ref.loc[:, ~df_ref.columns.duplicated( keep='last' ) ]

    # ===== spandex =====
    df_spandex_1 = df.loc[df[1].str.contains( 'Spandex', na=True ), 1]

    df_spandex_2 = df.loc[df[2].str.contains( 'Spandex', na=True ), 2]

    df_spandex_3 = df.loc[df[3].str.contains( 'Spandex', na=True ), 3]

    aux = df_spandex_1.combine_first( df_spandex_2 )
    df_spandex = aux.combine_first( df_spandex_3 )
    df_spandex.name = 'spandex'
                                                    
    df_ref = pd.concat( [df_ref, df_spandex], axis=1 )
    df_ref = df_ref.loc[:, ~df_ref.columns.duplicated( keep='last' )]

    # join of combine with product_id
    df_aux_ = pd.concat( [df_data['product_id'].reset_index( drop=True ), df_ref], axis=1 )

    df_aux_['cotton']     = df_aux_['cotton'].apply( lambda x: int( re.search( '\d+',x ).group() ) / 100 if pd.notnull( x ) else x )
    df_aux_['polyester']  = df_aux_['polyester'].apply( lambda x: int( re.search( '\d+',x ).group() ) / 100 if pd.notnull( x ) else x )
    df_aux_['elasterell'] = df_aux_['elasterell'].apply( lambda x: int( re.search( '\d+',x ).group() ) / 100 if pd.notnull( x ) else x )
    df_aux_['spandex']    = df_aux_['spandex'].apply( lambda x: int( re.search( '\d+',x ).group() ) / 100 if pd.notnull( x ) else x )

    # final join
    df_aux_ = df_aux_.groupby( 'product_id' ).max().reset_index().fillna(0)

    df_data = pd.merge( df_data,df_aux_, on='product_id', how='left' )

    # drop columns
    df_data = df_data.drop( columns=['size', 'composition'], axis=1 )

    # drop duplicatates
    df_data = df_data.drop_duplicates()

    return df_data

def data_insert( df_data ):
    # data insert
    data_insert = df_data[[
        'product_id',
        'style_id',
        'color_id',
        'product_name',
        'color_name',
        'fit',
        'product_price',
        'size_number',
        'size_model',
        'cotton',
        'polyester',
        'elasterell',
        'spandex',
        'scrapy_datetime'
    ]]

    # create database connection
    conn = create_engine( 'sqlite:///database_hm.sqlite', echo=False )

    # data insert
    data_insert.to_sql( 'vitrine', con=conn, if_exists='append', index=False )

    return None

if __name__ == '__main__':


    # logging
    path = '/c/Users/Marcos/Projects/H-M'

    if not os.path.exists( path + 'Logs' ):
        os.makedirs( path + 'Logs' )

    logging.basicConfig( 
        filename= path + 'Logs/webscraping_hm.log',
        level= logging.DEBUG,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt= '%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger( 'webscraping_hm' )

    # parameters and constants
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    # URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    # data collection
    data = data_collection( url, headers )
    logger.info( 'data collect done' )

    # data collection by product
    data_product = data_colection_by_product( data, headers )
    logger.info( 'data collection by product done' )

    # data cleaning
    data_product_cleaned = data_cleaning( data_product )
    logger.info( 'data product cleaned done' )

    # data insertion
    data_insert( data_product_cleaned )
    logger.info( 'data insertion done' )